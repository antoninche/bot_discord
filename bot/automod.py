from __future__ import annotations

import re
import time
from collections import deque
from dataclasses import dataclass

import discord
from discord.ext import commands

from bot.bot import DiscordBot


URL_RE = re.compile(r"(https?://|discord\.gg/|www\.)", re.IGNORECASE)


@dataclass(slots=True)
class SpamWindow:
    timestamps: deque[float]


class AutoModCog(commands.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot
        self._spam: dict[tuple[int, int], SpamWindow] = {}
        self._spam_limit = 5
        self._spam_window_seconds = 5.0

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild is None:
            return
        if message.author.bot:
            return
        if not isinstance(message.author, discord.Member):
            return

        settings = await self.bot.guild_config.get(message.guild.id)
        if not settings.automod_enabled:
            return

        # Admin/mod bypass
        if message.author.guild_permissions.administrator:
            return

        # Anti-links
        if settings.automod_antilinks and URL_RE.search(message.content or ""):
            try:
                await message.delete()
            except discord.Forbidden:
                return
            await message.channel.send(f"{message.author.mention} liens interdits.", delete_after=3)
            await self._log(message.guild, f"[AUTOMOD] anti-links: {message.author} | message supprimé")
            return

        # Anti-caps (si message assez long)
        if settings.automod_anticaps:
            text = message.content or ""
            letters = [c for c in text if c.isalpha()]
            if len(letters) >= 8:
                upper = sum(1 for c in letters if c.isupper())
                if upper / max(1, len(letters)) >= 0.7:
                    try:
                        await message.delete()
                    except discord.Forbidden:
                        return
                    await message.channel.send(f"{message.author.mention} trop de majuscules.", delete_after=3)
                    await self._log(message.guild, f"[AUTOMOD] anti-caps: {message.author} | message supprimé")
                    return

        # Anti-spam simple
        key = (message.guild.id, message.author.id)
        now = time.time()
        win = self._spam.get(key)
        if win is None:
            win = SpamWindow(timestamps=deque(maxlen=self._spam_limit + 2))
            self._spam[key] = win

        win.timestamps.append(now)
        while win.timestamps and (now - win.timestamps[0]) > self._spam_window_seconds:
            win.timestamps.popleft()

        if len(win.timestamps) >= self._spam_limit:
            # Action: timeout 30s
            until = discord.utils.utcnow() + discord.timedelta(seconds=30)  # type: ignore[attr-defined]
            try:
                await message.author.timeout(until, reason="AutoMod spam")
            except discord.Forbidden:
                return
            await message.channel.send(f"{message.author.mention} spam détecté (timeout 30s).", delete_after=3)
            await self._log(message.guild, f"[AUTOMOD] spam: {message.author} | timeout 30s")

    async def _log(self, guild: discord.Guild, text: str) -> None:
        settings = await self.bot.guild_config.get(guild.id)
        if settings.log_channel_id is None:
            return
        channel = guild.get_channel(settings.log_channel_id)
        if isinstance(channel, discord.TextChannel):
            await channel.send(text)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoModCog(bot))  # type: ignore[arg-type]