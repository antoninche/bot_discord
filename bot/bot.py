from __future__ import annotations

import logging
from typing import Sequence

import discord
from discord.ext import commands

from bot.config import BotConfig, load_config
from bot.logging_config import setup_logging

LOGGER = logging.getLogger(__name__)

DEFAULT_EXTENSIONS: Sequence[str] = (
    "bot.admin",
    "bot.fun",
    "bot.roles",
    "bot.music",
)


class DiscordBot(commands.Bot):
    def __init__(self, config: BotConfig) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=config.prefix,
            intents=intents,
            help_command=commands.DefaultHelpCommand(),
        )

        self.config = config

    async def setup_hook(self) -> None:
        await self._load_extensions()

        if self.config.sync_slash_commands:
            await self._sync_slash_commands()

    async def _load_extensions(self) -> None:
        for ext in DEFAULT_EXTENSIONS:
            try:
                await self.load_extension(ext)
                LOGGER.info("Extension chargée: %s", ext)
            except Exception:
                LOGGER.exception("Erreur au chargement de l'extension: %s", ext)

    async def _sync_slash_commands(self) -> None:
        try:
            guild_id = self.config.guild_id_for_dev_sync
            if guild_id is not None:
                guild = discord.Object(id=guild_id)
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                LOGGER.info("Slash commands synchronisées sur guild %s: %s", guild_id, len(synced))
            else:
                synced = await self.tree.sync()
                LOGGER.info("Slash commands synchronisées globalement: %s", len(synced))
        except Exception:
            LOGGER.exception("Erreur pendant la synchronisation des slash commands.")

    async def on_ready(self) -> None:
        LOGGER.info("Connecté en tant que %s (id=%s)", self.user, getattr(self.user, "id", None))


def run() -> None:
    config = load_config("config.json")
    setup_logging(config.log_level)

    bot = DiscordBot(config)
    bot.run(config.token)
