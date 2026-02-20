from __future__ import annotations

import logging
from pathlib import Path
from typing import Sequence

import discord
from discord.ext import commands

from bot.config import BotConfig, load_config
from bot.guild_config import GuildConfigManager
from bot.logging_config import setup_logging
from bot.storage import JsonStore

LOGGER = logging.getLogger(__name__)

DEFAULT_EXTENSIONS: Sequence[str] = (
    "bot.admin",
    "bot.fun",
    "bot.roles",
    "bot.music",
    "bot.utility",
    "bot.moderation",
    "bot.automod",
    "bot.levels",
    "bot.reaction_roles",
    "bot.tickets",
)


class DiscordBot(commands.Bot):
    def __init__(self, config: BotConfig) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=self._dynamic_prefix,
            intents=intents,
            help_command=commands.DefaultHelpCommand(),
        )

        self.config = config

        # Data stores
        data_dir = Path("data")
        self.guild_config = GuildConfigManager(
            store=JsonStore.from_path(data_dir / "guild_config.json"),
            default_prefix=config.prefix,
        )
        self.modlog_store = JsonStore.from_path(data_dir / "modlog.json")
        self.warnings_store = JsonStore.from_path(data_dir / "warnings.json")
        self.reaction_roles_store = JsonStore.from_path(data_dir / "reaction_roles.json")
        self.levels_store = JsonStore.from_path(data_dir / "levels.json")

    async def _dynamic_prefix(self, bot: commands.Bot, message: discord.Message) -> list[str]:
        if message.guild is None:
            return [self.config.prefix]
        settings = await self.guild_config.get(message.guild.id)
        return [settings.prefix]

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