from __future__ import annotations

import discord
from discord.ext import commands


class MusicCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="join")
    async def join_prefix(self, ctx: commands.Context) -> None:
        if not isinstance(ctx.author, discord.Member) or ctx.author.voice is None:
            await ctx.send("Tu dois être dans un canal vocal.")
            return

        channel = ctx.author.voice.channel
        if not isinstance(channel, discord.VoiceChannel):
            await ctx.send("Canal vocal invalide.")
            return

        if ctx.voice_client is None:
            await channel.connect()
        else:
            await ctx.voice_client.move_to(channel)

        await ctx.send(f"Connecté à: {channel.name}")

    @commands.command(name="leave")
    async def leave_prefix(self, ctx: commands.Context) -> None:
        if ctx.voice_client is None:
            await ctx.send("Je ne suis pas connecté.")
            return

        await ctx.voice_client.disconnect()
        await ctx.send("Déconnecté.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MusicCog(bot))