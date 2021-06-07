#so right now the bot responds with a randomly selected entry from a sql table
#the sql table is from a postgresql database hosted locally on your comp 
import discord
#import nest_asyncio
import random
import psycopg2
#import os

#token = os.getenv('DISCORD_TOKEN')
client = discord.Client()
guild = discord.Guild

#this part connects to the postgresql database
conn = psycopg2.connect(
    host="localhost",
    database="whatever your db name is",
    user="postgres",
    password="idk your password lmao")
#the cursor is the thing that executes sql queries on the postgresql database
cur = conn.cursor()

#bootup for the discord bot (just to make sure it started)
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
#nest_asyncio.apply()     

#discord bot listens for the command
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("spg.gacha"):
        #lmao so i ended up using a string because i couldn't figure out how to pass an integer into the postgresql query but i mean it still works???
        cardid = str(random.randint(1,10)) 
        cur.execute("SELECT cardname,cardid FROM cards WHERE cardid=%s",(cardid,))
        #technically cur.fetchone() only gets the first result from a sql query. but we're assuming that these queries only have 1 result, so this is fine
        row = cur.fetchone()
        await message.channel.send(row)

client.run("token")
#nest_asyncio.apply()      

#close the cursor and the postgresql connection
cur.close()
conn.close()
