from __future__ import annotations

import random
from typing import Sequence

import discord
from discord.ext import commands


EIGHTBALL_ANSWERS: Sequence[str] = (
    "Oui.",
    "Non.",
    "Peut-être.",
    "Probablement.",
    "Je ne pense pas.",
    "Impossible à dire.",
    "Repose la question plus tard.",
    "Très probable.",
    "Très improbable.",
)


class FunCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="roll")
    async def roll_prefix(self, ctx: commands.Context, faces: int = 6) -> None:
        faces = max(2, min(faces, 1_000))
        value = random.randint(1, faces)
        await ctx.send(f"Résultat: {value} (1..{faces})")

    @discord.app_commands.command(name="roll", description="Lance un dé (1..N).")
    @discord.app_commands.describe(faces="Nombre de faces (2 à 1000).")
    async def roll_slash(self, interaction: discord.Interaction, faces: int = 6) -> None:
        faces = max(2, min(faces, 1_000))
        value = random.randint(1, faces)
        await interaction.response.send_message(f"Résultat: {value} (1..{faces})", ephemeral=True)

    @commands.command(name="8ball")
    async def eightball_prefix(self, ctx: commands.Context, *, question: str) -> None:
        _ = question.strip()
        answer = random.choice(EIGHTBALL_ANSWERS)
        await ctx.send(answer)

    @commands.command(name="coinflip")
    async def coinflip_prefix(self, ctx: commands.Context) -> None:
        await ctx.send(random.choice(("Pile", "Face")))

    @commands.command(name="choose")
    async def choose_prefix(self, ctx: commands.Context, *, options: str) -> None:
        parts = [p.strip() for p in options.split("|") if p.strip()]
        if len(parts) < 2:
            await ctx.send("Utilise le format: !choose option1 | option2 | option3")
            return
        await ctx.send(random.choice(parts))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(FunCog(bot))