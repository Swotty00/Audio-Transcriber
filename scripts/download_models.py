"""
Faz o download e extrai os modelos Vosk necessários para o projeto.

Uso:
    python scripts/download_models.py           # baixa o modelo padrão (small pt)
    python scripts/download_models.py --model large
    python scripts/download_models.py --list
"""

import argparse
import sys
import zipfile
from pathlib import Path

import requests
from tqdm import tqdm

MODELS = {
    "small-pt": {
        "description": "Português (pequeno, ~50MB) — recomendado para começar",
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip",
        "dest": "models/vosk",
    },
    "large-pt": {
        "description": "Português (grande, ~1.5GB) — maior precisão",
        "url": "https://alphacephei.com/vosk/models/vosk-model-pt-fb-v0.1.1-20220516_2113.zip",
        "dest": "models/vosk",
    },
    "small-en": {
        "description": "Inglês (pequeno, ~40MB)",
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
        "dest": "models/vosk",
    },
}

ROOT = Path(__file__).resolve().parent.parent


def list_models() -> None:
    print("\nModelos disponíveis:\n")
    for name, info in MODELS.items():
        dest = ROOT / info["dest"]
        status = "[instalado]" if any(dest.iterdir()) else ""
        print(f"  {name:<12} {info['description']} {status}")
    print()


def download(url: str, dest_path: Path) -> Path:
    """Baixa um arquivo com barra de progresso. Retorna o path do zip."""
    dest_path.mkdir(parents=True, exist_ok=True)
    filename = dest_path / url.split("/")[-1]

    if filename.exists():
        print(f"Arquivo já existe: {filename}. Pulando download.")
        return filename

    print(f"Baixando {url} ...")
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    total = int(response.headers.get("content-length", 0))
    with open(filename, "wb") as f, tqdm(total=total, unit="B", unit_scale=True) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            bar.update(len(chunk))

    return filename


def extract(zip_path: Path, dest_dir: Path) -> Path:
    """Extrai o zip e renomeia a pasta extraída para o dest_dir."""
    print(f"Extraindo {zip_path.name} ...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        top_level = {p.split("/")[0] for p in zf.namelist() if p.strip("/")}
        zf.extractall(dest_dir)

    if len(top_level) == 1:
        extracted = dest_dir / top_level.pop()
        final = dest_dir
        print(f"Modelo extraído em: {extracted}")
        return extracted

    return dest_dir


def install_model(name: str) -> None:
    if name not in MODELS:
        print(f"Modelo '{name}' não encontrado. Use --list para ver os disponíveis.")
        sys.exit(1)

    info = MODELS[name]
    dest = ROOT / info["dest"]

    zip_path = download(info["url"], dest)
    model_path = extract(zip_path, dest)

    zip_path.unlink()
    print(f"\nPronto! Modelo '{name}' instalado em: {model_path}")
    print("Atualize VOSK_MODEL_PATH no .env se necessário.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Gerenciador de modelos Vosk")
    parser.add_argument(
        "--model",
        default="small-pt",
        help="Nome do modelo a instalar (padrão: small-pt)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Lista modelos disponíveis",
    )
    args = parser.parse_args()

    if args.list:
        list_models()
        return

    install_model(args.model)


if __name__ == "__main__":
    main()
