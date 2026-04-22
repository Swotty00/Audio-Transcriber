import logging
import logging.config
from pathlib import Path

import yaml

from config.settings import settings


def setup_logging() -> None:
    config_path = Path(__file__).parent / "logging.yaml"

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Aplica o log_level do .env no root logger
    config["root"]["level"] = settings.log_level

    # Garante que data/ existe antes de criar o arquivo de log
    Path("data").mkdir(exist_ok=True)

    logging.config.dictConfig(config)
