from __future__ import annotations

import random
import time
from dataclasses import dataclass

import discord
from discord.ext import commands

from bot.bot import DiscordBot


@dataclass(slots=True)
class XPCooldown:
    last_ts: float


def level_from_xp(xp: int) -> int:
    # Progression simple : level^2 * 100
    lvl = 0
    while (lvl + 1) * (lvl + 1) * 100 <= xp:
        lvl += 1
    return lvl


class LevelsCog(commands.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot
        self._cooldowns: dict[tuple[int, int], XPCooldown] = {}
        self._cooldown_seconds = 20.0

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild is None:
            return
        if message.author.bot:
            return
        if not isinstance(message.author, discord.Member):
            return

        settings = await self.bot.guild_config.get(message.guild.id)
        if not settings.xp_enabled:
            return

        key = (message.guild.id, message.author.id)
        now = time.time()
        cd = self._cooldowns.get(key)
        if cd is not None and (now - cd.last_ts) < self._cooldown_seconds:
            return
        self._cooldowns[key] = XPCooldown(last_ts=now)

        gain = random.randint(5, 15)

        data = await self.bot.levels_store.read()
        g = data.get(str(message.guild.id))
        if not isinstance(g, dict):
            g = {}

        xp = g.get(str(message.author.id))
        if not isinstance(xp, int):
            xp = 0

        old_level = level_from_xp(xp)
        xp += gain
        new_level = level_from_xp(xp)

        g[str(message.author.id)] = xp
        data[str(message.guild.id)] = g
        await self.bot.levels_store.write(data)

        if new_level > old_level:
            await message.channel.send(f"{message.author.mention} passe niveau {new_level}.")

    @commands.command(name="rank")
    async def rank_prefix(self, ctx: commands.Context, member: discord.Member | None = None) -> None:
        if ctx.guild is None:
            await ctx.send("Commande utilisable uniquement sur un serveur.")
            return

        target = member or (ctx.author if isinstance(ctx.author, discord.Member) else None)
        if target is None:
            await ctx.send("Contexte invalide.")
            return

        data = await self.bot.levels_store.read()
        g = data.get(str(ctx.guild.id))
        xp = 0
        if isinstance(g, dict):
            v = g.get(str(target.id))
            if isinstance(v, int):
                xp = v

        lvl = level_from_xp(xp)
        embed = discord.Embed(title=f"Rank: {target}", color=discord.Color.blurple())
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="XP", value=str(xp), inline=True)
        embed.add_field(name="Niveau", value=str(lvl), inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="leaderboard")
    async def leaderboard_prefix(self, ctx: commands.Context) -> None:
        if ctx.guild is None:
            await ctx.send("Commande utilisable uniquement sur un serveur.")
            return

        data = await self.bot.levels_store.read()
        g = data.get(str(ctx.guild.id))
        if not isinstance(g, dict) or not g:
            await ctx.send("Aucune donnée XP.")
            return

        items: list[tuple[int, int]] = []
        for k, v in g.items():
            if isinstance(v, int) and k.isdigit():
                items.append((int(k), v))

        items.sort(key=lambda t: t[1], reverse=True)
        top = items[:10]

        lines: list[str] = []
        for i, (user_id, xp) in enumerate(top, start=1):
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else str(user_id)
            lines.append(f"{i}. {name} — {xp} XP (lvl {level_from_xp(xp)})")

        embed = discord.Embed(title="Leaderboard", description="\n".join(lines), color=discord.Color.blurple())
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LevelsCog(bot))  # type: ignore[arg-type]