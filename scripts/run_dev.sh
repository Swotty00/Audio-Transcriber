#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# run_dev.sh — inicializa o ambiente e sobe o app em modo desenvolvimento
# ---------------------------------------------------------------------------

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# --- cores para output ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}[run_dev]${NC} $*"; }
warn()  { echo -e "${YELLOW}[run_dev]${NC} $*"; }
error() { echo -e "${RED}[run_dev]${NC} $*" >&2; }

# ---------------------------------------------------------------------------
# 1. Verifica Python
# ---------------------------------------------------------------------------
if ! command -v python3 &>/dev/null; then
    error "Python 3 não encontrado. Instale antes de continuar."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
info "Python $PYTHON_VERSION encontrado."

# ---------------------------------------------------------------------------
# 2. Cria/ativa virtualenv
# ---------------------------------------------------------------------------
VENV_DIR="$ROOT/.venv"

if [ ! -d "$VENV_DIR" ]; then
    info "Criando virtualenv em .venv ..."
    python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
info "Virtualenv ativado."

# ---------------------------------------------------------------------------
# 3. Instala dependências se necessário
# ---------------------------------------------------------------------------
if [ ! -f "$VENV_DIR/.deps_installed" ] || [ requirements.txt -nt "$VENV_DIR/.deps_installed" ]; then
    info "Instalando dependências (requirements.txt) ..."
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    touch "$VENV_DIR/.deps_installed"
else
    info "Dependências já instaladas."
fi

# ---------------------------------------------------------------------------
# 4. Verifica .env
# ---------------------------------------------------------------------------
if [ ! -f "$ROOT/.env" ]; then
    warn ".env não encontrado. Criando a partir de .env.example ..."
    if [ -f "$ROOT/.env.example" ]; then
        cp "$ROOT/.env.example" "$ROOT/.env"
        warn "Edite o .env com suas configurações antes de continuar."
    else
        warn "Crie um arquivo .env na raiz do projeto."
    fi
fi

# ---------------------------------------------------------------------------
# 5. Verifica modelo Vosk
# ---------------------------------------------------------------------------
VOSK_MODEL_PATH=$(python3 -c "
import os, sys
sys.path.insert(0, '.')
try:
    from config.settings import settings
    print(settings.vosk_model_path)
except Exception:
    print('models/vosk')
" 2>/dev/null)

if [ -z "$(ls -A "$ROOT/$VOSK_MODEL_PATH" 2>/dev/null)" ]; then
    warn "Modelo Vosk não encontrado em '$VOSK_MODEL_PATH'."
    warn "Baixando modelo padrão (small-pt) ..."
    python3 scripts/download_models.py --model small-pt
fi

# ---------------------------------------------------------------------------
# 6. Garante que a pasta data/ existe
# ---------------------------------------------------------------------------
mkdir -p "$ROOT/data"

# ---------------------------------------------------------------------------
# 7. Sobe o Streamlit
# ---------------------------------------------------------------------------
info "Iniciando Audio Transcriber..."
echo ""

exec streamlit run app/main.py \
    --server.port="${STREAMLIT_PORT:-8501}" \
    --server.address="${STREAMLIT_HOST:-localhost}" \
    --server.fileWatcherType=poll \
    --logger.level="$( python3 -c "
import sys; sys.path.insert(0, '.')
try:
    from config.settings import settings; print(settings.log_level.lower())
except Exception:
    print('info')
" 2>/dev/null )"
