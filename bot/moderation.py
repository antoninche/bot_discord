from __future__ import annotations

import datetime as dt
from typing import Any

import discord
from discord.ext import commands

from bot.bot import DiscordBot
from bot.checks import is_admin


def _now_iso() -> str:
    return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat()


class ModerationCog(commands.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

    async def _send_modlog(self, guild: discord.Guild, message: str) -> None:
        settings = await self.bot.guild_config.get(guild.id)
        if settings.log_channel_id is None:
            return
        channel = guild.get_channel(settings.log_channel_id)
        if isinstance(channel, discord.TextChannel):
            await channel.send(message)

    @commands.command(name="kick")
    @is_admin()
    async def kick_prefix(self, ctx: commands.Context, member: discord.Member, *, reason: str = "Aucune raison") -> None:
        if ctx.guild is None:
            await ctx.send("Commande utilisable uniquement sur un serveur.")
            return
        try:
            await member.kick(reason=reason)
            await ctx.send(f"Membre expulsé: {member} | Raison: {reason}")
            await self._send_modlog(ctx.guild, f"[KICK] {member} | par {ctx.author} | {reason}")
        except discord.Forbidden:
            await ctx.send("Permission refusée (role du bot trop bas ou permission manquante).")

    @commands.command(name="ban")
    @is_admin()
    async def ban_prefix(self, ctx: commands.Context, member: discord.Member, *, reason: str = "Aucune raison") -> None:
        if ctx.guild is None:
            await ctx.send("Commande utilisable uniquement sur un serveur.")
            return
        try:
            await member.ban(reason=reason, delete_message_days=0)
            await ctx.send(f"Membre banni: {member} | Raison: {reason}")
            await self._send_modlog(ctx.guild, f"[BAN] {member} | par {ctx.author} | {reason}")
        except discord.Forbidden:
            await ctx.send("Permission refusée (role du bot trop bas ou permission manquante).")

    @commands.command(name="unban")
    @is_admin()
    async def unban_prefix(self, ctx: commands.Context, user_id: int, *, reason: str = "Aucune raison") -> None:
        if ctx.guild is None:
            await ctx.send("Commande utilisable uniquement sur un serveur.")
            return
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=reason)
            await ctx.send(f"Utilisateur débanni: {user} | Raison: {reason}")
            await self._send_modlog(ctx.guild, f"[UNBAN] {user} | par {ctx.author} | {reason}")
        except discord.NotFound:
            await ctx.send("Utilisateur introuvable dans la liste des bannis.")
        except discord.Forbidden:
            await ctx.send("Permission refusée (permission manquante).")

    @commands.command(name="timeout")
    @is_admin()
    async def timeout_prefix(self, ctx: commands.Context, member: discord.Member, duration: str, *, reason: str = "Aucune raison") -> None:
        """
        Exemple: !timeout @membre 10m raison
        duration: 10s, 5m, 2h, 1d
        """
        if ctx.guild is None:
            await ctx.send("Commande utilisable uniquement sur un serveur.")
            return

        seconds = self._parse_duration(duration)
        if seconds is None:
            await ctx.send("Durée invalide. Formats: 10s, 5m, 2h, 1d")
            return

        until = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc) + dt.timedelta(seconds=seconds)
        try:
            await member.timeout(until, reason=reason)
            await ctx.send(f"Timeout appliqué à {member} pour {duration} | Raison: {reason}")
            await self._send_modlog(ctx.guild, f"[TIMEOUT] {member} | par {ctx.author} | {duration} | {reason}")
        except discord.Forbidden:
            await ctx.send("Permission refusée (permission modération manquante).")

    @staticmethod
    def _parse_duration(value: str) -> int | None:
        value = value.strip().lower()
        if len(value) < 2:
            return None
        unit = value[-1]
        num = value[:-1]
        if not num.isdigit():
            return None
        n = int(num)
        if n <= 0:
            return None
        if unit == "s":
            return n
        if unit == "m":
            return n * 60
        if unit == "h":
            return n * 3600
        if unit == "d":
            return n * 86400
        return None

    @commands.command(name="warn")
    @is_admin()
    async def warn_prefix(self, ctx: commands.Context, member: discord.Member, *, reason: str = "Aucune raison") -> None:
        if ctx.guild is None:
            await ctx.send("Commande utilisable uniquement sur un serveur.")
            return

        data = await self.bot.warnings_store.read()
        g = data.get(str(ctx.guild.id))
        if not isinstance(g, dict):
            g = {}
        u = g.get(str(member.id))
        if not isinstance(u, list):
            u = []

        u.append(
            {
                "by": getattr(ctx.author, "id", None),
                "reason": reason,
                "at": _now_iso(),
            }
        )
        g[str(member.id)] = u
        data[str(ctx.guild.id)] = g
        await self.bot.warnings_store.write(data)

        await ctx.send(f"Avertissement ajouté pour {member}: {reason}")
        await self._send_modlog(ctx.guild, f"[WARN] {member} | par {ctx.author} | {reason}")

    @commands.command(name="warnings")
    @is_admin()
    async def warnings_prefix(self, ctx: commands.Context, member: discord.Member) -> None:
        if ctx.guild is None:
            await ctx.send("Commande utilisable uniquement sur un serveur.")
            return

        data = await self.bot.warnings_store.read()
        g = data.get(str(ctx.guild.id))
        if not isinstance(g, dict):
            await ctx.send("Aucun avertissement.")
            return
        u = g.get(str(member.id))
        if not isinstance(u, list) or not u:
            await ctx.send("Aucun avertissement.")
            return

        lines: list[str] = []
        for i, entry in enumerate(u[-10:], start=max(1, len(u) - 9)):
            if not isinstance(entry, dict):
                continue
            reason = str(entry.get("reason", ""))
            at = str(entry.get("at", ""))
            by = entry.get("by")
            by_str = str(by) if isinstance(by, int) else "N/A"
            lines.append(f"{i}. {reason} (par {by_str}, {at})")

        msg = "\n".join(lines) if lines else "Aucun avertissement."
        embed = discord.Embed(title=f"Avertissements: {member}", description=msg, color=discord.Color.orange())
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ModerationCog(bot))  # type: ignore[arg-type]