from __future__ import annotations

import discord
from discord.ext import commands

from bot.checks import is_admin


class RolesCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @staticmethod
    def _find_role(guild: discord.Guild, role_name: str) -> discord.Role | None:
        target = role_name.strip().lower()
        for role in guild.roles:
            if role.name.lower() == target:
                return role
        return None

    @commands.command(name="addrole")
    @is_admin()
    async def add_role_prefix(self, ctx: commands.Context, *, role_name: str) -> None:
        if not isinstance(ctx.author, discord.Member) or ctx.guild is None:
            await ctx.send("Contexte invalide.")
            return

        role = self._find_role(ctx.guild, role_name)
        if role is None:
            await ctx.send("Rôle introuvable.")
            return

        await ctx.author.add_roles(role, reason="Commande addrole")
        await ctx.send(f"Rôle ajouté: {role.name}")

    @commands.command(name="removerole")
    @is_admin()
    async def remove_role_prefix(self, ctx: commands.Context, *, role_name: str) -> None:
        if not isinstance(ctx.author, discord.Member) or ctx.guild is None:
            await ctx.send("Contexte invalide.")
            return

        role = self._find_role(ctx.guild, role_name)
        if role is None:
            await ctx.send("Rôle introuvable.")
            return

        await ctx.author.remove_roles(role, reason="Commande removerole")
        await ctx.send(f"Rôle retiré: {role.name}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RolesCog(bot))