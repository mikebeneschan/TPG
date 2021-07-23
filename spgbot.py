import discord
#import nest_asyncio
import random
import psycopg2
import os

token = os.getenv('DISCORD_TOKEN')
client = discord.Client()
guild = discord.Guild

conn = psycopg2.connect(
    host="localhost",
    database="CARDS",
    user="postgres",
    password="password_here")
cur = conn.cursor()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
#nest_asyncio.apply()     

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if (message.content=="spg.gacha"):
        
        cardid = str(random.randint(1,6)) 
        cur.execute("SELECT image,cardname,cardid,tier,pet FROM cards WHERE cardid=%s",(cardid,))
        row = cur.fetchone()
        filename = row[0]
        title = row[1]
        cardid = str(row[2])
        tier = row[3]
        pet = row[4]
        msg = "**Title: "+title+"**\n**ID: "+cardid+"**\n**Tier: "+tier+"**\n**Pet: "+pet+"**"
        await message.channel.send(content=msg, file=discord.File(filename))
        
    if (message.content=="spg.new"):
        cmd="INSERT INTO users(discord) VALUES ('"+str(message.author)+"')"
        cur.execute(cmd)
        conn.commit()
        await message.channel.send("successfully added to user database")
client.run(token)
#nest_asyncio.apply()      

cur.close()
conn.close()
