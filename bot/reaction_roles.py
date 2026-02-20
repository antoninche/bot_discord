from __future__ import annotations

import discord
from discord.ext import commands

from bot.bot import DiscordBot
from bot.checks import is_admin


class ReactionRolesCog(commands.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

    @commands.command(name="reactionrole")
    @is_admin()
    async def reactionrole_prefix(
        self,
        ctx: commands.Context,
        message_id: int,
        emoji: str,
        role: discord.Role,
    ) -> None:
        """
        Associe une réaction à un rôle sur un message existant.

        Usage:
        !reactionrole <message_id> <emoji> @Role
        """
        if ctx.guild is None:
            await ctx.send("Commande utilisable uniquement sur un serveur.")
            return

        data = await self.bot.reaction_roles_store.read()
        g = data.get(str(ctx.guild.id))
        if not isinstance(g, dict):
            g = {}
        m = g.get(str(message_id))
        if not isinstance(m, dict):
            m = {}

        m[emoji] = role.id
        g[str(message_id)] = m
        data[str(ctx.guild.id)] = g
        await self.bot.reaction_roles_store.write(data)

        await ctx.send("Reaction role enregistré. Assure-toi que la réaction existe sur le message.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        if payload.guild_id is None:
            return
        if payload.user_id is None:
            return
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return
        if payload.user_id == getattr(self.bot.user, "id", None):
            return

        data = await self.bot.reaction_roles_store.read()
        g = data.get(str(payload.guild_id))
        if not isinstance(g, dict):
            return
        m = g.get(str(payload.message_id))
        if not isinstance(m, dict):
            return

        emoji = str(payload.emoji)
        role_id = m.get(emoji)
        if not isinstance(role_id, int):
            return

        role = guild.get_role(role_id)
        if role is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None:
            return

        try:
            await member.add_roles(role, reason="Reaction role")
        except discord.Forbidden:
            return

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        if payload.guild_id is None:
            return
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        data = await self.bot.reaction_roles_store.read()
        g = data.get(str(payload.guild_id))
        if not isinstance(g, dict):
            return
        m = g.get(str(payload.message_id))
        if not isinstance(m, dict):
            return

        emoji = str(payload.emoji)
        role_id = m.get(emoji)
        if not isinstance(role_id, int):
            return

        role = guild.get_role(role_id)
        if role is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None:
            return

        try:
            await member.remove_roles(role, reason="Reaction role removed")
        except discord.Forbidden:
            return


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ReactionRolesCog(bot))  # type: ignore[arg-type]