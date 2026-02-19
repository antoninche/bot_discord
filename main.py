import discord
from discord.ext import commands, tasks
import youtube_dl
import asyncio
import random
from colorama import Fore
# from discord_slash import SlashCommand
# from discord_slash.utils.manage_commands import create_option, create_choice

intents = discord.Intents.default()
intents.members = True  # Activation de l'intention des membres
intents.message_content = True

bot = commands.Bot(command_prefix="!", description="Bot de Antonin", intents=intents)
# slash = SlashCommand(bot, sync_commands=True)

# Le bot est lancé 
@bot.event
async def on_ready():
    change_status.start()
    print("Ready !")

# Information sur le serveur
@bot.command()
async def serverInfo(ctx):
    server = ctx.guild
    numberOfTextChannels = len(server.text_channels)
    numberOfVoiceChannels = len(server.voice_channels)
    serverDescription = server.description
    numberOfPerson = server.member_count
    serverName = server.name

    # Création de l'embed
    embed = discord.Embed(title="Informations sur le serveur", color=0x7289da)
    embed.add_field(name="Nom du serveur", value=serverName, inline=False)
    embed.add_field(name="Nombre de membres", value=numberOfPerson, inline=False)
    embed.add_field(name="Description", value=serverDescription or "Aucune description", inline=False)
    embed.add_field(name="Salons textuels", value=numberOfTextChannels, inline=False)
    embed.add_field(name="Salons vocaux", value=numberOfVoiceChannels, inline=False)

    # Envoi de l'embed
    await ctx.send(embed=embed)


# Commande HELP
@bot.command()
async def aide(ctx):
    commandes = {
        "serverInfo": "Avoir toutes les informations sur le serveur",
        "mute": "Pourvoir mute quelqu'un.",
        "unmute": "Pouvoir unmute  quelqu'un.",
        "kick": "Kick une personne du serveur.",
        "ban": "Bannir une personne du serveur.",
        "unban": "Debannir une personne du serveur.",
        "clear": "Supprimer un nombre de messages dans un channel.",
        "bans_list": "Obtenir la liste des ID des bannis",
        "jeux": "Giveway",
        "cuisiner": "Demander de créer une recette."
    }
    
    embed = discord.Embed(title="Liste des commandes disponibles", color=0x00ff00)
    
    for cmd, desc in commandes.items():
        embed.add_field(name=f"!{cmd}", value=desc, inline=False)
    
    await ctx.send(embed=embed)



# Commandes d'administration

# Mute / unmute 
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
async def mute(ctx, member: discord.Member, *, reason="Aucune raison n'a été renseignée"):
    mutedRole = await getMutedRole(ctx)
    await member.add_roles(mutedRole, reason=reason)

    embed = discord.Embed(title="Mute",
                          description=f"{member.mention} a été mute avec succès.",
                          color=0xff0000)
    if reason:
        embed.add_field(name="Raison", value=reason, inline=False)

    await ctx.send(embed=embed)
    print(f"{Fore.BLUE}{member.name} a été mute. Raison : {reason}")


@bot.command()
async def unmute(ctx, member: discord.Member, *, reason="Aucune raison n'a été renseignée"):
    mutedRole = await getMutedRole(ctx)
    await member.remove_roles(mutedRole, reason=reason)

    embed = discord.Embed(title="Unmute",
                          description=f"{member.mention} a été unmute avec succès.",
                          color=0x00ff00)
    if reason:
        embed.add_field(name="Raison", value=reason, inline=False)

    await ctx.send(embed=embed)
    print(f"{Fore.BLUE}{member.name} a été unmute. Raison : {reason}")



@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, nombre: int):
    async for message in ctx.channel.history(limit=nombre + 1):
        await message.delete()
    embed = discord.Embed(title="Messages supprimés", description=f"{nombre} messages ont été supprimés.", color=0xff0000)
    await ctx.send(embed=embed)
    print(f"{Fore.GREEN}{nombre} messages ont été supprimés.")  # Change la couleur du texte à vert




@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.Member, *reason):
    reason = " ".join(reason) if reason else None
    # await ctx.guild.kick(user, reason=reason)
    embed = discord.Embed(title="Membre expulsé", description=f"{user.name} a été expulsé du serveur.", color=0xff0000)
    embed.add_field(name="Raison", value=reason if reason else "Aucune raison spécifiée", inline=False)
    await ctx.send(embed=embed)
    print(f"{Fore.RED}{user.name} a été kick. Raison : {reason}")
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.Member, *reason):
    reason = " ".join(reason) if reason else None
    await ctx.guild.ban(user, reason=reason)
    embed = discord.Embed(title="Membre banni", description=f"{user.name} a été banni du serveur.", color=0xff0000)
    embed.add_field(name="Raison", value=reason if reason else "Aucune raison spécifiée", inline=False)
    await ctx.send(embed=embed)
    print(f"{Fore.RED}{user.name} a été ban. Raison : {reason}")

# Unban user
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user, *reason):
    reason = " ".join(reason) if reason else None
    banned_users = await ctx.guild.bans()

    for banned_entry in banned_users:
        banned_user = banned_entry.user
        if banned_user.name == user:
            await ctx.guild.unban(banned_user, reason=reason)

            embed = discord.Embed(title="Débannissement",
                                  description=f"L'utilisateur {banned_user.name} a été débanni avec succès.",
                                  color=0x00ff00)
            if reason:
                embed.add_field(name="Raison", value=reason, inline=False)

            await ctx.send(embed=embed)
            return

    await ctx.send(f"L'utilisateur {user} n'est pas trouvé dans la liste des bannis.")
    print(f"{Fore.RED}{user.name} a été unban. Raison : {reason}")


# List of bans
@bot.command()
async def bans_list(ctx):
    banned_users = await ctx.guild.bans()

    embed = discord.Embed(title="Liste des utilisateurs bannis", color=0xff0000)

    if banned_users:
        for entry in banned_users:
            embed.add_field(name=entry.user.name, value=f"Raison : {entry.reason}", inline=False)
    else:
        embed.description = "Aucun utilisateur n'a été banni sur ce serveur."

    await ctx.send(embed=embed)


# Private command
def isOwner(ctx):
    return ctx.message.id == 1204831024891043900

@bot.command()
@commands.check(isOwner)
async def private(ctx):
    embed = discord.Embed(title="Commande privée", description="Cette commande ne peut être utilisée que par le propriétaire du bot.", color=0xff0000)
    await ctx.send(embed=embed)

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


# Role
@bot.event
@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message.id == 1206239069856604180:  
        if str(reaction.emoji) == "✅":  
            role = discord.utils.get(user.guild.roles, name="Jeux vidéos")  
            if role is not None:  
                await user.add_roles(role)
                print(f"{user.name} a maintenant le rôle {role.name}")
            else:
                print("Le rôle n'existe pas ou n'a pas été trouvé.")
     
    if reaction.message.id == 1206239106644844554:  
        if str(reaction.emoji) == "✅":  
            role = discord.utils.get(user.guild.roles, name="Programmation")  
            if role is not None:  
                await user.add_roles(role)
                print(f"{user.name} a maintenant le rôle {role.name}")
            else:
                print("Le rôle n'existe pas ou n'a pas été trouvé.")

    if reaction.message.id == 1206239142057353266:  
        if str(reaction.emoji) == "✅":  
            role = discord.utils.get(user.guild.roles, name="HOMME")  
            if role is not None:  
                await user.add_roles(role)
                print(f"{user.name} a maintenant le rôle {role.name}")
            else:
                print("Le rôle n'existe pas ou n'a pas été trouvé.")

    if reaction.message.id == 1206239142057353266:  
        if str(reaction.emoji) == "❌":  # Ajout du rôle "FEMME"
            role = discord.utils.get(user.guild.roles, name="FEMME")  
            if role is not None:  
                await user.add_roles(role)
                print(f"{user.name} a maintenant le rôle {role.name}")
            else:
                print("Le rôle n'existe pas ou n'a pas été trouvé.")

    if reaction.message.id == 1206239181928538132:  
        if str(reaction.emoji) == "✅":  # Ajout du rôle "+18 ans"
            role = discord.utils.get(user.guild.roles, name="+18 ans")  
            if role is not None:  
                await user.add_roles(role)
                print(f"{user.name} a maintenant le rôle {role.name}")
            else:
                print("Le rôle n'existe pas ou n'a pas été trouvé.")

    if reaction.message.id == 1206239181928538132:  
        if str(reaction.emoji) == "❌":  # Ajout du rôle "-18 ans"
            role = discord.utils.get(user.guild.roles, name="-18 ans")  
            if role is not None:  
                await user.add_roles(role)
                print(f"{user.name} a maintenant le rôle {role.name}")
            else:
                print("Le rôle n'existe pas ou n'a pas été trouvé.")





# Giveway command
@bot.command()
async def jeux(ctx):
    temps = 10
    await ctx.send(f"La roulette commencera dans {temps} secondes. Envoyez \"moi\" dans ce channel pour y participer.")

    players = []

    def check(message):
        return message.channel == ctx.message.channel and message.author not in players and message.content == "moi"

    try:
        while True:
            participation = await bot.wait_for("message", timeout=temps, check=check)
            players.append(participation.author)
            await ctx.send(
                f"**{participation.author.name}** participe au tirage ! Le tirage commence dans {temps} secondes")
    except asyncio.TimeoutError:
        await asyncio.sleep(temps - 3)

    price = [" a gagné un rôle spécial", " peut expulser quelqu'un", " peut demander à devenir modérateur", " devient VIP",
             " peut mute quelqu'un", " peut donner un gage à quelqu'un"]
    await ctx.send("Le tirage commence dans 3 secondes")
    await asyncio.sleep(1)
    await ctx.send("2")
    await asyncio.sleep(1)
    await ctx.send("1")
    winner = random.choice(players)
    await ctx.send(f"{winner.mention} {random.choice(price)}. Vous avez gagné !!!")
    players.clear()

# Event

# When a message is deleted
@bot.event
async def on_message_delete(message):
    print(f"Le message de **{message.author}** a été supprimé.")
    if message.content:
        print(f"Son contenu était le suivant : {message.content}")
    elif message.attachments:
        print("Le message contenait des fichiers :")
        for attachment in message.attachments:
            print(attachment.url)

# When a message is edited
@bot.event
async def on_message_edit(before, after):
    print(f"{before.author} a édité son message.")
    if before.content:
        print(f"Avant -> {before.content}")
    if after.content:
        print(f"Après -> {after.content}")


# When a person joins the server
@bot.event
async def on_member_join(member):
    channel = member.guild.get_channel(1205866097207803905)
    
    embed = discord.Embed(title="Nouvel arrivant !", description=f"Bienvenue à toi sur notre serveur {member.mention} :)", color=0x00ff00)
    embed.set_thumbnail(url=member.avatar_url)
    
    await channel.send(embed=embed)

# When a person leaves the server
@bot.event
async def on_member_remove(member):
    channel = member.guild.get_channel(1205866097207803905)
    
    embed = discord.Embed(title="Départ d'un membre", description=f"{member.name} a quitté notre serveur :(", color=0xff0000)
    
    await channel.send(embed=embed)

# When a person reacts, the bot does the same
@bot.event
async def on_reaction_add(reaction, user):
    await reaction.message.add_reaction(reaction.emoji)


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
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url
        , before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"))

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

# Gestion des erreurs
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
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Mauvais argument fourni pour cette commande.')
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'Cette commande est en cooldown. Veuillez réessayer dans {error.retry_after:.2f} secondes.')
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send('Cette commande est désactivée et ne peut pas être utilisée.')
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send('Cette commande ne peut pas être utilisée en messages privés.')
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send('Une erreur s\'est produite lors de l\'exécution de la commande.')
        print(f'Erreur lors de l\'exécution de la commande : {error.original}')
    else:
        await ctx.send('Une erreur inattendue s\'est produite.')
        print(f'Erreur inattendue : {error}')

# Launch the bot and receipt the token in file
file = open('token.txt', 'r+')
token = file.readlines()[0]

bot.run(token)
