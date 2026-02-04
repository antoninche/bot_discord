# Slash commands
# @slash.slash(name="Lancer", description="Lance un dé pour toi.", guild_ids=[1204828700252704839], options=[
#     create_option(
#         name="Tricher",
#         description="Tricher pour sortir toujours le même résultat (4).",
#         option_type=3,
#         required=True,
#         choices=[
#             create_choice(
#                 name="Oui",
#                 value="y"
#             ),
#             create_choice(
#                 name="Non",
#                 value="n"
#             )
#         ]
#     ),
#     create_option(
#         name="limite_inferieur",
#         description="Le nombre le plus petit que le dé peut donner.",
#         option_type=4,
#         required=False
#     ),
#     create_option(
#         name="limite_superieure",
#         description="Le nombre le plus grand que le dé peut donner.",
#         option_type=4,
#         required=False
#     )
# ])
# async def lancer(ctx, tricher, limite_inferieure=1, limite_superieure=6):
#     await ctx.send("Je lance le dé ..")
#     if tricher == "y":
#         num = 4
#     else:
#         num = random.randint(1, 6)
#     await ctx.send(f'Le résultat est : **{num}**')




# # Commande de base : coucou
# @bot.command()
# async def coucou(ctx):
#     await ctx.send("Coucou !")

# # Commande pour répéter un texte
# @bot.command()
# async def say(ctx, *texte):
#     await ctx.send(" ".join(texte))

# # Commande pour traduire en chinois
# @bot.command()
# async def chinese(ctx, *text):
#     chineseChar = "丹书匚刀巳下呂廾工丿片乚爪冂口尸Q尺丂丁凵V山乂Y乙"
#     chineseText = []
#     for word in text:
#         for char in word:
#             if char.isalpha():
#                 index = ord(char) - ord("a")
#                 transformed = chineseChar[index]
#                 chineseText.append(transformed)
#             else:
#                 chineseText.append(char)
#         chineseText.append(" ")
#     await ctx.send("".join(chineseText))







# When a message appears
# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return
#     await message.channel.send(f">{message.content}\n{message.author}")
#     await bot.process_commands(message)





# When a person types
# @bot.event
# async def on_typing(channel, user, when):
#     await channel.send(f"{user.name} a commencé à écrire dans ce channel le {when}.")