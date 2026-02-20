from __future__ import annotations

import discord
from discord.ext import commands

from bot.bot import DiscordBot


class CloseTicketView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Fermer le ticket", style=discord.ButtonStyle.danger, custom_id="ticket_close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message("Contexte invalide.", ephemeral=True)
            return

        await interaction.response.send_message("Ticket fermé.", ephemeral=True)
        try:
            await channel.delete(reason="Ticket fermé")
        except discord.Forbidden:
            pass


class TicketsCog(commands.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

    @commands.command(name="ticket")
    async def ticket_prefix(self, ctx: commands.Context) -> None:
        guild = ctx.guild
        if guild is None:
            await ctx.send("Commande utilisable uniquement sur un serveur.")
            return
        if not isinstance(ctx.author, discord.Member):
            await ctx.send("Contexte invalide.")
            return

        category = discord.utils.get(guild.categories, name="Tickets")
        if category is None:
            try:
                category = await guild.create_category("Tickets", reason="Création catégorie tickets")
            except discord.Forbidden:
                await ctx.send("Permission refusée (création catégorie).")
                return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            ctx.author: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True) if guild.me else None,
        }
        overwrites = {k: v for k, v in overwrites.items() if v is not None}

        channel_name = f"ticket-{ctx.author.name}".lower().replace(" ", "-")
        try:
            ticket_channel = await guild.create_text_channel(
                channel_name,
                category=category,
                overwrites=overwrites,
                reason="Création ticket",
            )
        except discord.Forbidden:
            await ctx.send("Permission refusée (création salon).")
            return

        embed = discord.Embed(
            title="Ticket",
            description="Explique ton problème ici. Un membre du staff peut répondre.",
            color=discord.Color.blurple(),
        )
        await ticket_channel.send(content=ctx.author.mention, embed=embed, view=CloseTicketView())
        await ctx.send(f"Ticket créé: {ticket_channel.mention}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TicketsCog(bot))  # type: ignore[arg-type]