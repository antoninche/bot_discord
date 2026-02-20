from __future__ import annotations

import datetime as dt

import discord
from discord.ext import commands

from bot.checks import is_admin
from bot.bot import DiscordBot


def _fmt_dt(value: dt.datetime | None) -> str:
    if value is None:
        return "N/A"
    return value.strftime("%Y-%m-%d %H:%M")


class UtilityCog(commands.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

    @commands.command(name="userinfo")
    async def userinfo_prefix(self, ctx: commands.Context, member: discord.Member | None = None) -> None:
        if ctx.guild is None:
            await ctx.send("Commande utilisable uniquement sur un serveur.")
            return

        target = member or (ctx.author if isinstance(ctx.author, discord.Member) else None)
        if target is None:
            await ctx.send("Contexte invalide.")
            return

        roles = [r.name for r in target.roles if r.name != "@everyone"]
        embed = discord.Embed(title=f"User info: {target}", color=discord.Color.blurple())
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="ID", value=str(target.id), inline=True)
        embed.add_field(name="Compte créé", value=_fmt_dt(target.created_at), inline=True)
        embed.add_field(name="Arrivé sur le serveur", value=_fmt_dt(target.joined_at), inline=True)
        embed.add_field(name="Rôles", value=", ".join(roles) if roles else "Aucun", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="serverinfo")
    async def serverinfo_prefix(self, ctx: commands.Context) -> None:
        guild = ctx.guild
        if guild is None:
            await ctx.send("Commande utilisable uniquement sur un serveur.")
            return

        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        roles = len(guild.roles)
        embed = discord.Embed(title=f"Server info: {guild.name}", color=discord.Color.blurple())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="ID", value=str(guild.id), inline=True)
        embed.add_field(name="Créé le", value=_fmt_dt(guild.created_at), inline=True)
        embed.add_field(name="Membres", value=str(guild.member_count or "N/A"), inline=True)
        embed.add_field(name="Salons texte", value=str(text_channels), inline=True)
        embed.add_field(name="Salons vocaux", value=str(voice_channels), inline=True)
        embed.add_field(name="Rôles", value=str(roles), inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="avatar")
    async def avatar_prefix(self, ctx: commands.Context, member: discord.Member | None = None) -> None:
        target = member or (ctx.author if isinstance(ctx.author, discord.Member) else None)
        if target is None:
            await ctx.send("Contexte invalide.")
            return
        embed = discord.Embed(title=f"Avatar: {target}", color=discord.Color.blurple())
        embed.set_image(url=target.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="roleinfo")
    async def roleinfo_prefix(self, ctx: commands.Context, *, role_name: str) -> None:
        guild = ctx.guild
        if guild is None:
            await ctx.send("Commande utilisable uniquement sur un serveur.")
            return

        target = role_name.strip().lower()
        role = next((r for r in guild.roles if r.name.lower() == target), None)
        if role is None:
            await ctx.send("Rôle introuvable.")
            return

        embed = discord.Embed(title=f"Role info: {role.name}", color=role.color if role.color.value else discord.Color.blurple())
        embed.add_field(name="ID", value=str(role.id), inline=True)
        embed.add_field(name="Membres", value=str(len(role.members)), inline=True)
        embed.add_field(name="Créé le", value=_fmt_dt(role.created_at), inline=True)
        embed.add_field(name="Mention", value=role.mention, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="setprefix")
    @is_admin()
    async def setprefix_prefix(self, ctx: commands.Context, prefix: str) -> None:
        if ctx.guild is None:
            await ctx.send("Commande utilisable uniquement sur un serveur.")
            return
        prefix = prefix.strip()
        if not prefix:
            await ctx.send("Prefix invalide.")
            return

        await self.bot.guild_config.set_prefix(ctx.guild.id, prefix)
        await ctx.send(f"Prefix mis à jour: {prefix}")

    @commands.command(name="setlogchannel")
    @is_admin()
    async def setlogchannel_prefix(self, ctx: commands.Context, channel: discord.TextChannel | None = None) -> None:
        if ctx.guild is None:
            await ctx.send("Commande utilisable uniquement sur un serveur.")
            return
        channel_id = channel.id if channel else None
        await self.bot.guild_config.set_log_channel(ctx.guild.id, channel_id)
        await ctx.send("Salon de logs mis à jour.")

    @commands.command(name="xp")
    @is_admin()
    async def xp_prefix(self, ctx: commands.Context, state: str) -> None:
        if ctx.guild is None:
            await ctx.send("Commande utilisable uniquement sur un serveur.")
            return
        state = state.strip().lower()
        if state not in {"on", "off"}:
            await ctx.send("Utilise: !xp on | !xp off")
            return
        await self.bot.guild_config.set_xp(ctx.guild.id, enabled=(state == "on"))
        await ctx.send(f"XP: {state}")

    @commands.command(name="automod")
    @is_admin()
    async def automod_prefix(self, ctx: commands.Context, state: str) -> None:
        if ctx.guild is None:
            await ctx.send("Commande utilisable uniquement sur un serveur.")
            return
        state = state.strip().lower()
        if state not in {"on", "off"}:
            await ctx.send("Utilise: !automod on | !automod off")
            return
        await self.bot.guild_config.set_automod(ctx.guild.id, enabled=(state == "on"))
        await ctx.send(f"Auto-mod: {state}")

    @commands.command(name="antilinks")
    @is_admin()
    async def antilinks_prefix(self, ctx: commands.Context, state: str) -> None:
        if ctx.guild is None:
            await ctx.send("Commande utilisable uniquement sur un serveur.")
            return
        state = state.strip().lower()
        if state not in {"on", "off"}:
            await ctx.send("Utilise: !antilinks on | !antilinks off")
            return
        await self.bot.guild_config.set_automod(ctx.guild.id, antilinks=(state == "on"))
        await ctx.send(f"Anti-links: {state}")

    @commands.command(name="anticaps")
    @is_admin()
    async def anticaps_prefix(self, ctx: commands.Context, state: str) -> None:
        if ctx.guild is None:
            await ctx.send("Commande utilisable uniquement sur un serveur.")
            return
        state = state.strip().lower()
        if state not in {"on", "off"}:
            await ctx.send("Utilise: !anticaps on | !anticaps off")
            return
        await self.bot.guild_config.set_automod(ctx.guild.id, anticaps=(state == "on"))
        await ctx.send(f"Anti-caps: {state}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UtilityCog(bot))  # type: ignore[arg-type]