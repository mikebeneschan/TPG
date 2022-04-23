import discord
import nest_asyncio
import psycopg2
#import numpy as np
from rng2 import gacha
from rng2 import gachalist
from rng2 import view
from rng2 import timecheck
#import os

#token = os.getenv('DISCORD_TOKEN')
client = discord.Client()
guild = discord.Guild

conn = psycopg2.connect(
    host="localhost",
    database="SPG",
    user="postgres",
    password="hahaohhimark")
cur = conn.cursor()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='spg.help'))
nest_asyncio.apply()     

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if (message.content=="spg.gacha"):
        try:
            tcheck = timecheck(str(message.author))
            if tcheck!="allowed":
                tcheck = "Hi "+str(message.author.display_name)+tcheck
                await message.channel.send(tcheck)
            else:
                msg2 = gacha(str(message.author))
                msg2.set_author(name=message.author.display_name,
                                icon_url=message.author.avatar_url)
                await message.channel.send(embed=msg2)
        except Exception:
            await message.channel.send(":0 it looks like you're not in the database yet. use command **spg.new** to add yourself")
        
    if (message.content=="spg.new"):
        try:
            cmd="INSERT INTO users(discid, pity_s, pity_ss, pity_sss) VALUES ('"+str(message.author)+"',0,0,0)"
            cur.execute(cmd)
            conn.commit()
            await message.channel.send("successfully added to user database")
        except Exception:
            await message.channel.send(":0 you're already in the user database")
            
    if (message.content=="spg.list"):
        msg = "**Hi "+str(message.author.display_name)+"! You own the following cards:**\n"
        msg2 = gachalist(str(message.author))
        msg2 = msg + msg2
        await message.channel.send(msg2)
        
    if (message.content=="spg.help"):
        await message.channel.send("Hi! I am **Squid Pet Gacha**. Right now these are the commands I know:\n"
                                   "**spg.help** - gives list of commands\n"
                                   "**spg.new** - adds your discord name to the user database (you need to do this before you can start pulling cards)\n"
                                   "**spg.gacha** - gives you a new pet (pulls are on a 24hr cooldown)\n"
                                   "**spg.list** - lists the cards you currently own (this isnt fully functional right now)\n"
                                   "**spg.view [index]** - use this to view a card you already own\n")
        
    if (message.content.startswith("spg.view")):
        arr=message.content.split(" ")
        msg = view(str(message.author), int(arr[1]))
        msg.set_author(name=message.author.display_name+" is viewing...",
                        icon_url=message.author.avatar_url)
        msg.set_image(url='https://imgur.com/WosUrYk.jpeg')
        await message.channel.send(embed=msg)
        
client.run("token")
nest_asyncio.apply()      

cur.close()
conn.close()
