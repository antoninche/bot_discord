from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class StorageError(RuntimeError):
    pass


@dataclass(slots=True)
class JsonStore:
    """
    Stockage JSON simple, atomique et sûr pour un bot Discord.

    - Lecture/écriture via fichiers
    - Verrou asyncio pour éviter les écritures concurrentes
    - Écriture atomique (write temp + replace)
    """

    path: Path
    _lock: asyncio.Lock

    @classmethod
    def from_path(cls, path: str | Path) -> "JsonStore":
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        return cls(path=p, _lock=asyncio.Lock())

    async def read(self) -> dict[str, Any]:
        async with self._lock:
            if not self.path.exists():
                return {}
            try:
                raw = self.path.read_text(encoding="utf-8")
                if not raw.strip():
                    return {}
                data = json.loads(raw)
                if not isinstance(data, dict):
                    raise StorageError(f"JSON racine non dict dans {self.path}")
                return data
            except json.JSONDecodeError as exc:
                raise StorageError(f"JSON invalide dans {self.path}: {exc}") from exc

    async def write(self, data: dict[str, Any]) -> None:
        if not isinstance(data, dict):
            raise StorageError("write() attend un dict au niveau racine.")

        async with self._lock:
            tmp = self.path.with_suffix(self.path.suffix + ".tmp")
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(self.path)