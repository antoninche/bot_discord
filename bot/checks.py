from __future__ import annotations

import discord
from discord.ext import commands


def is_admin() -> commands.Check:
    """
    Check réutilisable: autorise uniquement les membres ayant la permission Administrateur.
    """

    async def predicate(ctx: commands.Context) -> bool:
        if not isinstance(ctx.author, discord.Member):
            return False
        return ctx.author.guild_permissions.administrator

    return commands.check(predicate)