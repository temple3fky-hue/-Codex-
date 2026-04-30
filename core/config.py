"""配置读写。"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from models.schemas import AppSettings

CONFIG_PATH = Path("data/settings.json")


def load_settings() -> AppSettings:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        settings = AppSettings()
        save_settings(settings)
        return settings
    return AppSettings(**json.loads(CONFIG_PATH.read_text(encoding="utf-8")))


def save_settings(settings: AppSettings) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(asdict(settings), ensure_ascii=False, indent=2), encoding="utf-8"
    )
