#from https://www.youtube.com/watch?v=SPTfmiYiuok
#~ https://discord.com/api/oauth2/authorize?client_id=839853679459696730&permissions=199744&scope=bot

import discord
import os

def loadLocalEnv(strLocalFileName = ".env"):
    """
    load variable from a local file, typically .env
    """
    dictNewEnv = {}
    f = open(strLocalFileName,"rt")
    while 1:
        li = f.readline()
        if len(li) < 1:
            break
        if li[0] =='#':
            continue
        elems = li.split("=")
        key = elems[0]
        data = elems[1]
        if data[0] == '"' and data[-1] == '"':
            data = data[1:-1]
        dictNewEnv[key] = data
        print("DBG: loadLocalEnv: add '%s'=>'%s'" % (key,data) )
    f.close()
    return dictNewEnv
        

def getEnv(strName, strDefault = None ):
    """
    get a value from local env, then from environnement
    """
    dLocal = loadLocalEnv()
    try:
        return dLocal[strName]
    except:
        pass
    retVal = os.getenv(strName)
    if retVal == None:
        retVal = strDefault
    return retVal


client = discord.Client()

@client.event
async def on_ready():
    print("INF: we are logged as " + str(client.user) + ", detail: " + str(client) )
    
    
@client.event
async def on_message(msg):
    #~ print("DBG: message: " + str(msg) )
    print("DBG: on_message: salon: '%s', author: '%s', message: '%s'" % (msg.channel.name,msg.author,msg.content) )
    if msg.author == client.user:
        return
    if msg.channel.name != 'salon-de-test':
        return
        
    print("INF: received: %s" % msg.content )
    
    strReply = ""
    if "hello" in msg.content.lower():
        strReply = "Hello!"
    if "pourquoi" in msg.content.lower():
        strReply = "parce que!"
    if "comment" in msg.content.lower():
        strReply = "Je ne sais pas, et toi ?"
    if strReply != "":
        print("INF: replying: %s" % strReply )
        await msg.channel.send(strReply)
    
strToken = getEnv("TOKEN")
#~ print( strToken)
client.run(strToken)