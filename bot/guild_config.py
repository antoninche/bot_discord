from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from bot.storage import JsonStore


@dataclass(slots=True)
class GuildSettings:
    prefix: str
    log_channel_id: int | None
    automod_enabled: bool
    automod_antilinks: bool
    automod_anticaps: bool
    xp_enabled: bool


DEFAULT_SETTINGS = GuildSettings(
    prefix="!",
    log_channel_id=None,
    automod_enabled=False,
    automod_antilinks=False,
    automod_anticaps=False,
    xp_enabled=False,
)


class GuildConfigManager:
    """
    Stocke une configuration par serveur (guild_id) dans un JSON unique.
    """

    def __init__(self, store: JsonStore, default_prefix: str) -> None:
        self._store = store
        self._default_prefix = default_prefix

    def _defaults(self) -> GuildSettings:
        s = DEFAULT_SETTINGS
        return GuildSettings(
            prefix=self._default_prefix or s.prefix,
            log_channel_id=s.log_channel_id,
            automod_enabled=s.automod_enabled,
            automod_antilinks=s.automod_antilinks,
            automod_anticaps=s.automod_anticaps,
            xp_enabled=s.xp_enabled,
        )

    async def get(self, guild_id: int) -> GuildSettings:
        data = await self._store.read()
        raw = data.get(str(guild_id))
        d = asdict(self._defaults())

        if isinstance(raw, dict):
            for k, v in raw.items():
                if k in d:
                    d[k] = v

        # Validation légère
        prefix = d.get("prefix")
        if not isinstance(prefix, str) or not prefix.strip():
            prefix = self._default_prefix

        log_channel_id = d.get("log_channel_id")
        if not (isinstance(log_channel_id, int) and log_channel_id > 0):
            log_channel_id = None

        def _b(x: Any) -> bool:
            return bool(x) if isinstance(x, bool) else False

        return GuildSettings(
            prefix=prefix.strip(),
            log_channel_id=log_channel_id,
            automod_enabled=_b(d.get("automod_enabled")),
            automod_antilinks=_b(d.get("automod_antilinks")),
            automod_anticaps=_b(d.get("automod_anticaps")),
            xp_enabled=_b(d.get("xp_enabled")),
        )

    async def set_prefix(self, guild_id: int, prefix: str) -> None:
        prefix = prefix.strip()
        if not prefix:
            raise ValueError("Prefix vide.")

        data = await self._store.read()
        entry = data.get(str(guild_id))
        if not isinstance(entry, dict):
            entry = {}
        entry["prefix"] = prefix
        data[str(guild_id)] = entry
        await self._store.write(data)

    async def set_log_channel(self, guild_id: int, channel_id: int | None) -> None:
        data = await self._store.read()
        entry = data.get(str(guild_id))
        if not isinstance(entry, dict):
            entry = {}
        entry["log_channel_id"] = channel_id
        data[str(guild_id)] = entry
        await self._store.write(data)

    async def set_automod(self, guild_id: int, *, enabled: bool | None = None,
                         antilinks: bool | None = None, anticaps: bool | None = None) -> None:
        data = await self._store.read()
        entry = data.get(str(guild_id))
        if not isinstance(entry, dict):
            entry = {}
        if enabled is not None:
            entry["automod_enabled"] = enabled
        if antilinks is not None:
            entry["automod_antilinks"] = antilinks
        if anticaps is not None:
            entry["automod_anticaps"] = anticaps
        data[str(guild_id)] = entry
        await self._store.write(data)

    async def set_xp(self, guild_id: int, enabled: bool) -> None:
        data = await self._store.read()
        entry = data.get(str(guild_id))
        if not isinstance(entry, dict):
            entry = {}
        entry["xp_enabled"] = enabled
        data[str(guild_id)] = entry
        await self._store.write(data)