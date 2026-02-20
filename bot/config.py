from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


class ConfigError(ValueError):
    """Configuration invalide ou incomplète."""


@dataclass(frozen=True, slots=True)
class BotConfig:
    token: str
    prefix: str
    sync_slash_commands: bool
    guild_id_for_dev_sync: Optional[int]
    log_level: str


def _require_str(data: dict[str, Any], key: str) -> str:
    v = data.get(key)
    if not isinstance(v, str) or not v.strip():
        raise ConfigError(f"Clé '{key}' manquante ou invalide (string non vide attendue).")
    return v.strip()


def _optional_int(data: dict[str, Any], key: str) -> Optional[int]:
    v = data.get(key)
    if v is None:
        return None
    if isinstance(v, int) and v > 0:
        return v
    raise ConfigError(f"Clé '{key}' invalide (entier positif ou null attendu).")


def _optional_bool(data: dict[str, Any], key: str, default: bool) -> bool:
    v = data.get(key, default)
    if isinstance(v, bool):
        return v
    raise ConfigError(f"Clé '{key}' invalide (bool attendu).")


def load_config(path: str | Path = "config.json") -> BotConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Fichier de config introuvable: {config_path.resolve()}")

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"JSON invalide dans {config_path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigError("Le JSON racine doit être un objet (dict).")

    token = _require_str(raw, "token")
    prefix = _require_str(raw, "prefix")
    sync_slash_commands = _optional_bool(raw, "sync_slash_commands", default=True)
    guild_id_for_dev_sync = _optional_int(raw, "guild_id_for_dev_sync")
    log_level = _require_str(raw, "log_level").upper()

    return BotConfig(
        token=token,
        prefix=prefix,
        sync_slash_commands=sync_slash_commands,
        guild_id_for_dev_sync=guild_id_for_dev_sync,
        log_level=log_level,
    )