#from https://www.youtube.com/watch?v=SPTfmiYiuok
#~ https://discord.com/api/oauth2/authorize?client_id=839853679459696730&permissions=199744&scope=bot

import discord
import os

client = discord.Client()

@client.event
async def on_ready():
    print("INF: we are logged as " + str(client.user) + ", detail: " + str(client) )
    
    
@client.event
async def on_message(msg):
    print("DBG: message: " + str(msg) )
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
    
strToken = "ODM5ODUzNjc5NDU5Njk2NzMw.YJPssA.VEOFVEXPkc_-3f_lll_IT571c2U"
client.run(strToken)