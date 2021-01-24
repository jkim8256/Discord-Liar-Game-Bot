import discord
from discord.ext import commands
import time
import random
from discord.utils import get, find
import asyncio
import nacl

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = '!')
mems = []
dict = {} #id : word. search id to get word
inputs = {} # name : votes
word = ""

@client.event
async def on_ready():
    print('Bot is ready')

@client.event
async def on_member_join(member):
    print(f'{member} has joined the server')

@client.event
async def on_member_remove(member):
    print(f'{member} has left the server')

@client.command()
async def reset(ctx):
    global mems
    global dict
    global inputs
    global word

    mems = []
    dict = {}
    inputs = {}
    word = ""
    await ctx.send('Reset done. Ready to play another game.')

@client.command()
async def start(ctx):
    global mems
    global dict
    global inputs
    global word

    channel = discord.utils.get(ctx.guild.voice_channels, name='General')
    channel_id = channel.id
    print(channel_id)
    memids = [] #(list) of member ids
    for key in channel.voice_states.keys():#members:
        mems.append(key)
        memids.append(key)
    print(mems) #print member info
    print(memids) #print member info

    # 1 person or less playing
    if(len(memids) < 2):
        await ctx.send("can't play alone")
        return
    # more than 1 playing
    else:
        elist = []
        num = len(memids)
        # the choice can be more than 2, but for now i have 2 per list
        wordlist_f = ['kimchi',
                        'steak',
                        'spaghetti']
        wordlist_o = ['doctor',
                        'soldier',
                        'president']
        def checker(m):
            return m.content.isdigit()

        await ctx.send('There are 2 categories of words. \n Option 1: Food\n Option 2: Occupation\n Type "1" to choose food, or "2" to choose occupation.')

        mes = await client.wait_for('message', check = checker)
        if int(mes.content,base = 10) == 1:
            word = random.choice(wordlist_f)
        elif int(mes.content,base = 10) == 2:
            word = random.choice(wordlist_o)
        else:
            await ctx.send("Can't follow simple instructions? Ending the program. Bye")
            return

        await client.wait_until_ready()

        # loop for distributing word to members
        while len(elist) < (num - 1):
            #if list is empty
            if not elist:
                uid = random.choice(memids)
                print(uid)
                elist.append(uid)
                dict.update({uid : word})
                count += 1
                # sending dm
                user = await client.fetch_user(uid)
                print(user)
                if user:
                    await user.send(f"You are a Citizen. The word is: {word}")
                else:
                    await ctx.send("Oops, error occurred. Ending the program.")
                    return
            else:
                uid = random.choice(memids)
                if not uid in elist:
                    elist.append(uid)
                    dict.update({uid : word})
                    count += 1
                    # sending dm
                    user = client.get_user(uid)
                    if user:
                        await user.send(f"You are a Citizen. The word is: {word}")
                    else:
                        await ctx.send("Oops, error occurred. Ending the program.")
                        return
                    #print(user) #checker

        #print(elist) # checker

            # loop for assigning a liar
        while len(elist) < num:
            uid = random.choice(memids)
            if not uid in elist:
                elist.append(uid)
                print(uid)
                dict.update({uid : "Liar"})
                count += 1
                # sending dm
                user = await client.fetch_user(uid)
                print(user)
                if user:
                    await user.send("You are the Liar. Try to fit in.")
                else:
                    await ctx.send("Oops, error occurred. Ending the program.")
                    return

        await ctx.send('Game begins in 5')
        await asyncio.sleep(0.5)
        for i in  range(4,0,-1):
            await ctx.send(i)
            await asyncio.sleep(0.5)

        await ctx.send("Start talking! Everyone has to talk something about the word once each round. there will be two rounds!")
        await ctx.send("Citizens, describe vaguely about the word so the liar can't guess the word!")
        await ctx.send("Liar, you need to guess the word and fit in")
        await ctx.send('type "!done" when the second round is over.')
        return

@client.command()
async def done(ctx):
    global mems
    global dict
    global inputs
    global word

    vlist = []
    await ctx.send("Who is the liar?")
    #take a poll
    #sends out options to vote
    for uid in range(len(mems)):
        user = client.get_user(mems[uid])
        if user:
            await ctx.send(f"Option{uid + 1}: {user.name}")
            inputs.update({user.name : 0})
        else:
            await ctx.send("Oops, error occurred. Ending the program.")
            return
    await ctx.send('Type in corresponding option number of the suspect (1,2,3...) to vote. Anything else will be ignored.')

    def cformat(m):
        if m.content.isdigit() and m.author.id not in vlist\
        and int(m.content, base = 10) - 1 < len(mems)\
        and int(m.content, base = 10) > 0:
            vlist.append(m.author.id)
            return True

    for uid in mems:
        mes = await client.wait_for('message', check = cformat)
        user = client.get_user(mems[int(mes.content, base = 10) - 1])
        if user:
            inputs.update({user.name: inputs[user.name] + 1})
        else:
            await ctx.send("Oops, error occurred. Ending the program.")
            return

    winner = client.get_user(mems[0])
    winner_id = mems[0]
    for x in range(1,len(inputs)):
        user = client.get_user(mems[x])
        if user:
            if inputs[user.name] > inputs[winner.name]:
                winner = user
                winner_id = mems[x]
        else:
            await ctx.send("Oops, error occurred. Ending the program.")
            return

    def format(m):
        return m.author.id == winner_id

    print(inputs)

    if dict[winner_id] == "Liar": #if the winner is liar
        await ctx.send(f"{winner.name} was the liar. Liar, what's the word?")
        ans = await client.wait_for('message', check = format)
        if ans.content == word:
            await ctx.send("Liar won!")
            return
        else:
            await ctx.send("Citizens won!")
            return
    else:
        for member in dict:
            if dict[member] == "Liar":
                user = client.get_user(member)
                await ctx.send(f"Liar won! The liar was {user.name}")
                return

client.run('put your bot token here')
