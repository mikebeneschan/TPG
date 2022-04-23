import random
import numpy as np
import psycopg2
import discord
import datetime as dt

#connect to postgres server
conn = psycopg2.connect(
    host="localhost",
    database="SPG",
    user="postgres",
    password="hahaohhimark")
cur = conn.cursor()

"""
Tier percentages (for now):
    B = 60% (0 to 0.6)
    A = 24% (0.6 to 0.84)
    S = 12% (0.84 to 0.96)
    SS = 3% (0.96 to 0.99)
    SSS = 1% (0.99 to 1)
"""

"""
https://popsql.com/learn-sql/postgresql/how-to-modify-arrays-in-postgresql
https://popsql.com/learn-sql/postgresql/how-to-insert-data-into-an-array-in-postgresql
"""

#function that finds the card
def gacha(author):
    #get random number
    x = np.random.uniform(0,1)

    #cases for each tier (cant use match because this is like python 3.8.8 lmao)
    if 0<=x<=0.6:
         tier="B"
    elif 0.6<x<=0.84:
        tier="A"
    elif 0.84<x<=0.96:
        tier="S"
    elif 0.96<x<=0.99:
        tier="SS"
    else: #0.99 <= x <= 1
        tier="SSS"   
    
    #determine pity rolls    
    cur.execute("SELECT pity_s, pity_ss, pity_sss FROM USERS WHERE DISCID=%s",(author,))
    row=cur.fetchone()
    pityS=row[0]
    pitySS=row[1]
    pitySSS=row[2]
    
    #pity roll activates
    if pityS==5:
        pityS=0
        tier="S"
        print("S pity roll activated")
    if pitySS==10:
        pitySS=0
        tier="SS"
        print("SS pity roll activated")
    if pitySSS==20:
        pitySSS=0
        tier="SSS"
        print("SSS pity roll activated")

    if tier !="S":
        pityS +=1
    else:
        pityS = 0
    if tier !="SS":
        pitySS +=1
    else:
        pitySS = 0
    if tier != "SSS":
        pitySSS +=1
    else:
        pitySSS=0
    
    #pick a random card based on the given rarity (accounting for pity rolls)
    cur.execute("SELECT image,title,CID,rarity,pet FROM CARDS WHERE RARITY=%s ORDER BY RANDOM() LIMIT 1",(tier,))
    row = cur.fetchone()
    filename = row[0]
    cardtitle = row[1]
    cardid = str(row[2])
    rarity = row[3]
    pet = row[4]
    pull_date = str(dt.date.today())
    msg2 = discord.Embed(title=cardtitle, 
                             description="**Card ID:** "+cardid+"\n**Tier: **"+rarity+"\n**Pet: **"+pet, 
                             color=0xdddddd)
    msg2.set_image(url=filename)
    #update the pull_list db with the new card
    cmd = ("insert into pull_list"
       "(image,title,cid,rarity,pet,pulled_by,pull_date,owner)" 
       "values('"+filename+"',"
       " '"+cardtitle+"',"
       " '"+cardid+"',"
       " '"+rarity+"',"
       " '"+pet+"',"
       " '"+author+"',"
       " '"+pull_date+"',"
       " '"+author+"')"
       )    
    cur.execute(cmd)
    conn.commit()

    #update pity roll info and next_pull info in users db
    next_pull = str(dt.datetime.now()+dt.timedelta(hours=24))
    cur.execute("update users set pity_s=%s,pity_ss=%s,pity_sss=%s,next_pull=%s WHERE discid=%s",(pityS,pitySS,pitySSS,next_pull,author))
    conn.commit()
    

    return msg2

#function that returns the list
def gachalist(author):
    msg = ""
    index = 1
    cur.execute("select collection from users where discid=%s",(author,))
    clist = cur.fetchone()
    clist = clist[0]
    for i in clist:
        cur.execute("select title from cards where cid=%s",(str(i),))
        ctitle = cur.fetchone()
        ctitle = ctitle[0]
        msg = msg + str(index) + ": " + ctitle + "\n"
        index += 1
    return msg

#gets the info for a specific card in the author's collection
def view(author,val):
    cur.execute("select collection from users where discid=%s",(author,))
    collection = cur.fetchone()
    val = val-1
    collection=collection[0]
    cid = int(collection[val])
    
    cur.execute("SELECT image,title,CID,rarity,pet FROM CARDS WHERE cid=%s",(cid,))
    row = cur.fetchone()
    filename = row[0]
    cardtitle = row[1]
    cardid = str(row[2])
    rarity = row[3]
    pet = row[4]
    
    msg2 = discord.Embed(title=cardtitle, 
                             description=
                             "**Card ID:** "+cardid+
                             "\n**Tier: **"+rarity+
                             "\n**Pet: **"+pet, 
                             color=0xdddddd)
    msg2.set_image(url=filename)
    return msg2

#checks the time and figures out if a pull is allowed based on discord username
def timecheck(author):
    return "allowed"
    cur.execute("select next_pull from users where discid=%s",(author,))
    next_pull_time = cur.fetchone()
    next_pull_time = next_pull_time[0]
    next_pull_time = dt.datetime.strptime(next_pull_time,'%Y-%m-%d %H:%M:%S.%f')

    time_now = dt.datetime.now()
    if next_pull_time < time_now:
        return "allowed"
    else:
        diff = next_pull_time - time_now
        h = diff.seconds//3600
        m = (diff.seconds//60)%60
        msg=(", your next pull isn't allowed for another **"+str(h)+" hours "
              "and "+str(m)+" minutes**")
        return msg

#function to test the randomization. make sure that the tiers look right
def gacha100():
    Blist=Alist=Slist=SSlist=SSSlist=0
    
    for i in range(100):
        j=np.random.uniform(0,1)
        if 0<=j<=0.6:
            Blist +=1
        elif 0.6<j<=0.84:
            Alist +=1
        elif 0.84<j<=0.96:
            Slist +=1
        elif 0.96<j<=0.99:
            SSlist +=1
        else: #0.99 <= j <= 1
            SSSlist +=1 
    print("This is a test of the RNG\n"+
          "B tier: "+str(Blist)+
          "\nA tier: "+str(Alist)+
          "\nS tier: "+str(Slist)+
          "\nSS tier: "+str(SSlist)+
          "\nSSS tier: "+str(SSSlist))
    
