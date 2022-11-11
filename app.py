# BOT APP
import os
import random
import discord
from dotenv import load_dotenv
import game


#Instantiate Game Manager
GM = game.GameManager()

your_fights_name = 'YOUR TEXTEN FIGHTS'
texten_arena_name = 'TEXTEN ARENA'
your_fights_category = None
texten_arena_category = None

intents = discord.Intents.default()
intents.members = True
intents.presences = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    for guild in client.guilds:  

        print("trying to create categories")
        
        your_fights_category = discord.utils.find(lambda g: g.name == your_fights_name, guild.categories)
        if your_fights_category is None:
            your_fights_category = await guild.create_category(your_fights_name)
        else:
            print(f"category {your_fights_name} already exists")

        texten_arena_category = discord.utils.find(lambda g: g.name == texten_arena_name, guild.categories)
        if texten_arena_category is None:
            texten_arena_category = await guild.create_category(texten_arena_name)
        else:
            print(f"category {texten_arena_name} already exists")

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

# @client.event
# async def on_member_join(member):
#     await member.create_dm()
#     await member.dm_channel.send(
#         f'Hi {member.name}, welcome to my Discord server!'
#     )



@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    print(message.content)

    #CHECK FOR "!delete_game" COMMAND - ADMIN ONLY COMMAND - DELETE A GAME BETWEEN TWO PLAYERS -
    if  '!delete_game ' in message.content.lower():
        lookup_members = message.content.split(" ")[1:]
        player1 = get_member(message, lookup_members[0])   
        player2 = get_member(message, lookup_members[1])    
        if message.author.guild_permissions.administrator and player1 is not None and player2 is not None:
            game_id = GM.create_game_id(message.guild.id, player1.id, player2.id)
            if GM.check_if_game_exist(game_id):
                game = GM.get_game_object(game_id)
                await game_over(game, message.channel)
                return
    
    if '!cleanup' in message.content.lower() and message.author.guild_permissions.administrator:
        your_fights_category = discord.utils.find(lambda g: g.name == your_fights_name, message.guild.categories)
        texten_arena_category = discord.utils.find(lambda g: g.name == texten_arena_name, message.guild.categories)
        for channel in your_fights_category.channels:
            await channel.delete()

        for channel in texten_arena_category.channels:
            await channel.delete()

    if '!lookup' in message.content.lower():
        lookup_member = message.content.split(" ")[1]
        await message.channel.send(f"looking for user {lookup_member}")
        membero = get_member(message, lookup_member)
        if membero is None:
           await message.channel.send(f"user not found")
        else: 
            await message.channel.send(f"found user @{membero.name}")
        return

    #CHALLENGE OTHER PLAYER FOR A FIGHT
    if '!challenge ' in message.content.lower():
        lookup_member = message.content.split(" ")[1]        
        player2 = get_member(message, lookup_member)

        #Below code should also check if there is an open match between the players - Implement this later!
        if player2 is None:
           await message.channel.send(f"Bitch ain't here!")
        else: 
            if player2 == message.author:
                await message.channel.send(f"Can't challange yourself")
                return                      
            challenge_id = GM.create_challenge_id(message.guild.id,message.author.id, player2.id)
            if GM.check_if_game_exist(challenge_id):
                await message.channel.send(f"Game already in progress!")
                return
            if not GM.check_if_challenge_exist(challenge_id):
                if GM.create_new_challenge(challenge_id):
                    await message.channel.send(f"{player2.mention} do you accept the challenge from {message.author.mention}?")
                else:
                    await message.channel.send(f"Something went wrong - couldn't create a challenge")
            else:
                await message.channel.send(f"You already have a open challenge with this player, try to accept his challenge")   
            # p1_overwrites = {
            #     message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            #     message.author: discord.PermissionOverwrite(read_messages=True)
            #     }
            # p2_overwrites = {
            #     message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            #     player2: discord.PermissionOverwrite(read_messages=True)
            #     }
            # player1_room = await your_fights_category.create_text_channel(f"{message.author.name}_VS_{player2.name}", overwrites = p1_overwrites)
            # player2_room = await your_fights_category.create_text_channel(f"{player2.name}_VS_{message.author.name}", overwrites = p2_overwrites)
            # # await player1_room.set_permissions(player2, read_messages=False, send_messages=False)
            # # await player2_room.set_permissions(message.author, read_messages=False, send_messages=False)
        return


    if '!accept ' in message.content.lower():
        lookup_member = message.content.split(" ")[1]        
        player2 = get_member(message, lookup_member)
        if player2 is None:
           await message.channel.send(f"Bitch ain't here!")
        else: 
            if player2 == message.author:
                await message.channel.send(f"Can't accept yourself")
                return   

            game_id = GM.create_game_id(message.guild.id,message.author.id, player2.id)
            if GM.check_if_game_exist(game_id):
                await message.channel.send(f"Game already in progress!")
                return

            your_fights_category = discord.utils.find(lambda g: g.name == your_fights_name, message.guild.categories)
            texten_arena_category = discord.utils.find(lambda g: g.name == texten_arena_name, message.guild.categories)
            p1_overwrites = {
                    message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    message.author: discord.PermissionOverwrite(read_messages=True)
                    }
            p2_overwrites = {
                    message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    player2: discord.PermissionOverwrite(read_messages=True)
                    }
            general_overwrites = {
                    message.guild.default_role: discord.PermissionOverwrite(send_messages=False)                    
                    }                    
            player1_room = await your_fights_category.create_text_channel(f"{message.author.name}_VS_{player2.name}", overwrites = p1_overwrites)
            player2_room = await your_fights_category.create_text_channel(f"{player2.name}_VS_{message.author.name}", overwrites = p2_overwrites)
            general_room = await texten_arena_category.create_text_channel(f"{player2.name}_VS_{message.author.name}", overwrites = general_overwrites)
            game_created = GM.create_new_game(game_id,message.author.id, player2.id, message.author.name, player2.name,player1_room.id, player2_room.id, general_room.id)
            GM.delete_challenge(game_id)
            if game_created:
                start_message = game_created.get_match_start_message()
                await player1_room.send(start_message)
                await player2_room.send(start_message)
                await general_room.send(start_message)
            # await player1_room.set_permissions(player2, read_messages=False, send_messages=False)
            # await player2_room.set_permissions(message.author, read_messages=False, send_messages=False)
        return  

    if '!abort ' in message.content.lower():
        lookup_member = message.content.split(" ")[1]        
        player2 = get_member(message, lookup_member)
        if player2 is None:
           await message.channel.send(f"Bitch ain't here!")
        else:   
            game_id = GM.create_game_id(message.guild.id, message.author.id, player2.id)
            if GM.check_if_game_exist(game_id):
                game = GM.get_game_object(game_id)
                await game_over(game, message.channel)
                return

    game_id = GM.check_if_message_sent_from_game_room(message.channel.id)
    if game_id:
        game_object = GM.get_game_object(game_id)
        response = GM.handle_game_room_message(game_id, message)
        if response[1]:
            p1_room = discord.utils.find(lambda g: g.id == game_object.p1_room_id, message.channel.guild.channels)
            p2_room = discord.utils.find(lambda g: g.id == game_object.p2_room_id, message.channel.guild.channels) 
            general_room = discord.utils.find(lambda g: g.id == game_object.general_room_id, message.channel.guild.channels)
            await p1_room.send(response[0])
            await p2_room.send(response[0])
            await general_room.send(response[0])
        else:
            await message.channel.send(response[0])
        return

async def game_over(game_object, channel):
    if game_object is None:
        await channel.send(f"Game session not found")
        return
    else:
        p1_room = discord.utils.find(lambda g: g.id == game_object.p1_room_id, channel.guild.channels)
        p2_room = discord.utils.find(lambda g: g.id == game_object.p2_room_id, channel.guild.channels) 
        general_room = discord.utils.find(lambda g: g.id == game_object.general_room_id, channel.guild.channels)

        if p1_room is None:
            await channel.send(f"Couldn't delete p1 room")
        else:
            await p1_room.delete()

        if p2_room is None:
            await channel.send(f"Couldn't delete p2 room")
        else:
            await p2_room.delete()

        if general_room is None:
            await channel.send(f"Couldn't find general room")
        else:
            await general_room.send("Game Over!")
        
        if GM.delete_game_object(game_object.game_id):
            await channel.send(f"Game deleted")
        else:
            await channel.send(f"Something went wrong- Game couldn't be deleted")

def get_member(message, input_name):
    '''Check if the given discord user name is a mention or an actual user name - when passing mentions via API, discord send the user ID in <@############> format'''
    if input_name[:2] == "<@" and input_name[-1] == ">":
        return discord.utils.find(lambda g: str(g.id) == input_name[2:-1], message.guild.members)
    else:
        return discord.utils.find(lambda g: g.name == input_name, message.guild.members)

client.run(TOKEN)