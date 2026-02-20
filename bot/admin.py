from __future__ import annotations

import discord
from discord.ext import commands

from bot.checks import is_admin


class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="ping")
    async def ping_prefix(self, ctx: commands.Context) -> None:
        latency_ms = int(self.bot.latency * 1000)
        await ctx.send(f"Pong ({latency_ms} ms)")

    @commands.command(name="purge")
    @is_admin()
    async def purge_prefix(self, ctx: commands.Context, limit: int = 10) -> None:
        limit = max(1, min(limit, 200))
        deleted = await ctx.channel.purge(limit=limit + 1)
        await ctx.send(f"{len(deleted) - 1} message(s) supprimé(s).", delete_after=3)

    @discord.app_commands.command(name="ping", description="Affiche la latence du bot.")
    async def ping_slash(self, interaction: discord.Interaction) -> None:
        latency_ms = int(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong ({latency_ms} ms)", ephemeral=True)

    @discord.app_commands.command(name="purge", description="Supprime des messages (admin).")
    @discord.app_commands.describe(limit="Nombre de messages à supprimer (1 à 200).")
    async def purge_slash(self, interaction: discord.Interaction, limit: int = 10) -> None:
        if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Permission insuffisante.", ephemeral=True)
            return

        limit = max(1, min(limit, 200))
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message("Commande utilisable uniquement dans un salon texte.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        deleted = await channel.purge(limit=limit)
        await interaction.followup.send(f"{len(deleted)} message(s) supprimé(s).", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdminCog(bot))