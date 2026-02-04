import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
import asyncio
import random
import youtube_dl

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", description="Bot de Titouan", intents=intents)
slash = SlashCommand(bot, sync_commands=True)

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    change_status.start()
    print("Ready !")

# Server information command
@bot.command()
async def serverInfo(ctx):
    server = ctx.guild
    numberOfTextChannels = len(server.text_channels)
    numberOfVoiceChannels = len(server.voice_channels)
    serverDescription = server.description
    numberOfPerson = server.member_count
    serverName = server.name
    message = f"Le serveur **{serverName}** contient *{numberOfPerson}* personnes ! \nLa description du serveur est {serverDescription}. \nCe serveur possède {numberOfTextChannels} salons écrit et {numberOfVoiceChannels} salon vocaux."
    await ctx.send(message)

# Basic command: say hello
@bot.command()
async def coucou(ctx):
    await ctx.send("Coucou !")

# Repeat a text command
@bot.command()
async def say(ctx, *texte):
    await ctx.send(" ".join(texte))

# Translate to Chinese command
@bot.command()
async def chinese(ctx, *text):
    chineseChar = "丹书匚刀巳下呂廾工丿片乚爪冂口尸Q尺丂丁凵V山乂Y乙"
    chineseText = []
    for word in text:
        for char in word:
            if char.isalpha():
                index = ord(char) - ord("a")
                transformed = chineseChar[index]
                chineseText.append(transformed)
            else:
                chineseText.append(char)
        chineseText.append(" ")
    await ctx.send("".join(chineseText))

# Administration commands

async def createMutedRole(ctx):
    mutedRole = await ctx.guild.create_role(name="Muted",
                                            permissions=discord.Permissions(
                                                send_messages=False,
                                                speak=False),
                                            reason="Creation du role Muted pour mute des gens.")
    for channel in ctx.guild.channels:
        await channel.set_permissions(mutedRole, send_messages=False, speak=False)
    return mutedRole

async def getMutedRole(ctx):
    roles = ctx.guild.roles
    for role in roles:
        if role.name == "Muted":
            return role
    return await createMutedRole(ctx)

@bot.command()
async def mute(ctx, member: discord.Member, *, reason="Aucune raison n'a été renseigné"):
    mutedRole = await getMutedRole(ctx)
    await member.add_roles(mutedRole, reason=reason)
    await ctx.send(f"{member.mention} a été mute !")

@bot.command()
async def unmute(ctx, member: discord.Member, *, reason="Aucune raison n'a été renseigné"):
    mutedRole = await getMutedRole(ctx)
    await member.remove_roles(mutedRole, reason=reason)
    await ctx.send(f"{member.mention} a été unmute !")

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Cette commande est introuvable')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Il manque un argument.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("Vous n'avez pas les permissions nécessaires.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send('Désolé, vous n\'avez pas la permission de faire cette action.')
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send('Je n\'ai pas les permissions pour exécuter cette action.')
    else:
        await ctx.send("Une erreur s'est produite lors de l'exécution de cette commande.")

# Clear messages command
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, nombre: int):
    messages = await ctx.channel.history(limit=nombre + 1).flatten()
    for message in messages:
        await message.delete()

# Kick a user command
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.Member, *reason):
    reason = " ".join(reason) if reason else None
    await ctx.guild.kick(user, reason=reason)
    await ctx.send(f"{user} a été expulsé.")

# Ban a user command
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.Member, *reason):
    reason = " ".join(reason) if reason else None
    await ctx.guild.ban(user, reason=reason)
    embed = discord.Embed(title="**Banissement**", description="Un modérateur a frappé !", url="https://www.google.com/", color=0xfa8072)
    embed.set_thumbnail(url="https://discordemoji.com/assets/emoji/BanneHammer.png")
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url, url="https://www.google.com/")
    embed.add_field(name="Membre banni", value=user.name, inline=True)
    embed.add_field(name="Raison", value=reason, inline=True)
    embed.add_field(name="Modérateur", value=ctx.author.name, inline=True)
    await ctx.send(embed=embed)

# Unban a user command
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user, *reason):
    reason = " ".join(reason) if reason else None
    banned_users = await ctx.guild.bans()
    for banned_entry in banned_users:
        banned_user = banned_entry.user
        if banned_user.name == user:
            await ctx.guild.unban(banned_user, reason=reason)
            await ctx.send(f"L'utilisateur {user} a été débanni.")
            return
    await ctx.send(f"L'utilisateur {user} n'est pas trouvé dans la liste des bannis.")

# List banned users command
@bot.command()
async def bansId(ctx):
    ids = [str(entry.user.id) for entry in await ctx.guild.bans()]
    await ctx.send("La liste des id des utilisateurs bannis du serveur est :")
    await ctx.send("\n".join(ids))

# Private command
def isOwner(ctx):
    return ctx.message.author.id == 1204831024891043900

@bot.command()
@commands.check(isOwner)
async def private(ctx):
    await ctx.send("Cette commande ne peut être utilisée que par le propriétaire du bot.")

# Reaction command
@bot.command()
async def cuisiner(ctx):
    await ctx.send("Envoyez le plat que vous voulez cuisiner")

    def checkMessage(message):
        return message.author == ctx.message.author and ctx.message.channel == message.channel

    try:
        recette = await bot.wait_for("message", timeout=10, check=checkMessage)
    except asyncio.TimeoutError:
        await ctx.send("Veuillez réitérer la commande.")
        return
    message = await ctx.send(
        f"La préparation de {recette.content} va commencer. Veuillez valider en réagissant avec ✅. Sinon réagissez avec ❌")
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    def checkEmoji(reaction, user):
        return ctx.message.author == user and message.id == reaction.message.id and (
                    str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=10, check=checkEmoji)
        if reaction.emoji == "✅":
            await ctx.send("La recette a démarré.")
        else:
            await ctx.send("La recette a bien été annulée.")
    except asyncio.TimeoutError:
        await ctx.send("La recette a bien été annulée.")

# Giveaway command
@bot.command()
async def roulette(ctx):
    temps = 10
    await ctx.send(f"La roulette commencera dans {temps} secondes. Envoyez \"moi\" dans ce channel pour y participer.")

    players = []

    def check(message):
        return message.channel == ctx.message.channel and message.author not in players and message.content == "moi"

    try:
        while True:
            participation = await bot.wait_for("message", timeout=temps, check=check)
            players.append(participation.author)
            await ctx.send(f"**{participation.author.name}** participe au tirage ! Le tirage commence dans {temps} secondes")
    except asyncio.TimeoutError:
        await asyncio.sleep(temps - 3)

    price = [" a gagné un rôle spécial", " peut expulser quelqu'un", " peut demander à devenir modérateur", " devient VIP", " peut mute quelqu'un", " peut donner un gage à quelqu'un"]
    await ctx.send("Le tirage commence dans 3 secondes")
    await asyncio.sleep(1)
    await ctx.send("2")
    await asyncio.sleep(1)
    await ctx.send("1")
    winner = random.choice(players)
    await ctx.send(f"{winner.mention} {random.choice(price)}. Vous avez gagné !!!")
    players.clear()

# Event handling

# When a message is sent
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await message.channel.send(f">{message.content}\n{message.author}")
    await bot.process_commands(message)

# When a message is deleted
@bot.event
async def on_message_delete(message):
    await message.channel.send(f"Le message de **{message.author}** a été supprimé.")
    print(f"Le message de **{message.author}** a été supprimé. Son contenu était le suivant : {message.content}")

# When a message is edited
@bot.event
async def on_message_edit(before, after):
    await before.channel.send(f"{before.author} a édité son message. Avant -> {before.content}\n Après -> {after.content}")
    print((f"{before.author} a édité son message. Avant -> {before.content}\n Après -> {after.content}"))

# When a member joins the server
@bot.event
async def on_member_join(member):
    channel = member.guild.get_channel(1205866097207803905)
    await channel.send(f"Bienvenue à toi sur notre serveur {member.name} :)")

# When a member leaves the server
@bot.event
async def on_member_remove(member):
    channel = member.guild.get_channel(1205866097207803905)
    await channel.send(f"{member.name} a quitté notre serveur :(")

# When a member reacts
@bot.event 
async def on_reaction_add(reaction, user):
    await reaction.message.add_reaction(reaction.emoji)

# When a member starts typing
@bot.event
async def on_typing(channel, user, when):
    await channel.send(f"{user.name} a commencé à écrire dans ce channel le {when}.")

# When a message is sent in DM
@bot.event
async def on_message_in_dm(message):
    if message.author == bot.user:
        return
    if isinstance(message.channel, discord.DMChannel):
        guild = bot.get_guild(473862992769799)
        channel = guild.get_channel(473862992769799)
        await channel.send(message.author.mention + message.content)

# Task from the bot
status = ["Fortnite",
        "Programmation",
        "Valorant", 
        "Homework", 
        "On the net", 
        "At the hospital", 
        "I'm sleeping"]

@tasks.loop(seconds=10.0, count=None)
async def change_status():
    game = discord.Game(random.choice(status))
    await bot.change_presence(status=discord.Status.dnd, activity=game)

# Music
musics = {}

ytdl = youtube_dl.YoutubeDL()

class Video:
    def __init__(self, link):
        video = ytdl.extract_info(link, download=False)
        video_format = video["formats"][0]
        self.url = video["webpage_url"]
        self.stream_url = video_format["url"]

@bot.command()
async def leave(ctx):
    client = ctx.guild.voice_client
    await client.disconnect()
    musics[ctx.guild] = []

@bot.command()
async def resume(ctx):
    client = ctx.guild.voice_client
    if client.is_paused():
        client.resume()

@bot.command()
async def pause(ctx):
    client = ctx.guild.voice_client
    if not client.is_paused():
        client.pause()

@bot.command()
async def skip(ctx):
    client = ctx.guild.voice_client
    client.stop()

def play_song(client, queue, song):
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url,
        before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"))

    def next(_):
        if len(queue) > 0:
            new_song = queue[0]
            del queue[0]
            play_song(client, queue, new_song)
        else:
            asyncio.run_coroutine_threadsafe(client.disconnect(), bot.loop)

    client.play(source, after=next)

@bot.command()
async def play(ctx, url):
    print("play")
    client = ctx.guild.voice_client

    if client and client.channel:
        video = Video(url)
        musics[ctx.guild].append(video)
    else:
        channel = ctx.author.voice.channel
        video = Video(url)
        musics[ctx.guild] = []
        client = await channel.connect()
        await ctx.send(f"Je lance : {video.url}")
        play_song(client, musics[ctx.guild], video)

# Slash commands
@slash.slash(name="Lancer", description="Lance un dé pour toi.", guild_ids=[1204828700252704839], options=[
    create_option(
        name="Tricher",
        description="Tricher pour sortir toujours le même résultat (4).",
        option_type=3,
        required=True,
        choices=[
            create_choice(
                name="Oui",
                value="y"
            ),
            create_choice(
                name="Non",
                value="n"
            )
        ]
    ),
    create_option(
        name="limite_inferieur",
        description="Le nombre le plus petit que le dé peut donner.",
        option_type=4,
        required=False
    ),
    create_option(
        name="limite_superieure",
        description="Le nombre le plus grand que le dé peut donner.",
        option_type=4,
        required=False
    )
])
async def lancer(ctx, tricher, limite_inferieure=1, limite_superieure=6):
    await ctx.send("Je lance le dé ..")
    if tricher == "y":
        num = 4
    else:
        num = random.randint(limite_inferieure, limite_superieure)
    await ctx.send(f'Le résultat est : **{num}**')

# Run the bot
bot.run("MTIwNDgzMTAyNDg5MTA0MzkwMA.G7k-1s.SMUBHen0TWIL-rfXRzkz-WfJSdJeBZRfwAsSW8")
