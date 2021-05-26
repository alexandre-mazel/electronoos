# coding: cp1252

#~ https://discord.com/api/oauth2/authorize?client_id=839853679459696730&permissions=199744&scope=bot

import asyncio
import discord
import os
import random
import threading
import time

import sys
sys.path.append("../alex_pytools/")
import misctools
import stringtools

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
        print("DBG: loadLocalEnv: add '%s' => '%s'" % (key,data) )
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
    
def pickElem( aList ):
    return aList[random.randint(0,len(aList)-1)]
    
    
def getRandomSeCoucherMoinsBete():
    page=misctools.getWebPage( "https://secouchermoinsbete.fr/random" ) # warning, need to change the signature of the opener in request.py: in OpenerDirector: around line 436: client_version =
    #~ page=misctools.getWebPage( "https://engrenage.studio" ) 
    #~ print(page.encode(sys.stdout.encoding, errors='replace'))
    strFirst = """a pas de complément" class="metadata details off"></a>
                <a href="/"""
    strFirst1 = "a pas de compl"
    strFirst1 = 'class="metadata details off"'
    strFirst2 = '<a href="/'

    page=stringtools.findSubString(page,strFirst1)
    addr=stringtools.findSubString(page,strFirst2, '"')
    #~ addr="29572-la-nouvellezelande-pays-du-mouton"
    print(addr)
    
    page=misctools.getWebPage( "https://secouchermoinsbete.fr/" + addr )
    strTitle = stringtools.findSubString(page,"<title>","</title>")
    strFirst1='"anecdote">'
    strFirst2='<p class="summary">'
    strEnd2 = '</p>'
    page=stringtools.findSubString(page,strFirst1)
    strAnecdote=stringtools.findSubString(page,strFirst2,strEnd2)

    
    out = "**" + strTitle + "**" + "\n" + strAnecdote +"\nC'est dingue non?"
    
    out = out.replace("&#039;", "'")
    return out
    
#~ print("random secoucher:" + getRandomSeCoucherMoinsBete())
#~ exit(1)
    
class ChatBot:
    def __init__( self ):
        pass
        
    def randomBoring( self ):
        return rand
        
    def receive( self, strMessage, strAuthor ):
        """
        receive a text from an author and reply to it
        return the text to reply
        """
        msg = strMessage.lower()
        strReply = ""
        if "hello" in msg:
            strReply = "Hello!"
        elif "pourquoi" in msg:
            strReply = "parce que!"
        elif "comment" in msg:
            strReply = "Je ne sais pas, et toi ?"
        elif "combien" in msg:
            strReply = str(random.randint(0,3333)) + pickElem( [", surtout le matin...", ", enfin je crois.", ""])
        else:
            strReply = "C'est cui qui dit qui l'est!"
        return strReply
        
    def update( self ):
        """
        call it from time to time, if sth is to be said, it will return it
        """
        h,m,s = misctools.getTime()
        if h==19 and m < 1:
            return "C'est l'heure de la fin du cours!"
        if random.random()>0.94:
            return pickElem( ["Je m'ennuie...", "Il fait beau non?", "Tu n'as pas un jeu a me proposer?", "Pardon, j'étais parti au toilettes, j'ai raté un truc?"] )
        if random.random()>0.97:
            return getRandomSeCoucherMoinsBete()
        return ""


client = discord.Client()
clientLastChannel = None
chatBot = ChatBot()

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
    
    
    strReply = chatBot.receive(msg.content,msg.author )
    if strReply != "":
        print("INF: replying: %s" % strReply )
        await msg.channel.send(strReply)
    global clientLastChannel 
    clientLastChannel = msg.channel
    
    
#~ def updater():
    #~ while 1:
        #~ print(".")
        #~ strReply=chatBot.update()
        #~ print(strReply)
        #~ print(clientLastChannel)
        #~ if strReply != "" and clientLastChannel != None:
            #~ print("INF: replying (from update): %s" % strReply )
            #~ clientLastChannel.send(strReply)
        #~ time.sleep(6) #burk
        
async def my_background_task():
    try:
        await client.wait_until_ready()
        print("INF: my_background_task: started")
        while not client.is_closed():
            #~ print(".")
            strReply=chatBot.update()
            if strReply != "":
                #~ strReply = "/tts\n" + strReply
                print( "INF: after update, sending: %s" % strReply )
                for server in client.guilds:
                    for channel in server.channels:
                        #~ print(dir(channel))
                        if channel.name == "salon-de-test": #ecrire certains message dans tout les channel de type ecriture: type, typing, topic,permissions_for, members, _state
                            await channel.send(strReply)
                #~ if clientLastChannel != None:
                    #~ await client.send_message(clientLastChannel, strReply)
            await asyncio.sleep(6) # task runs every 6 seconds
        print("INF: my_background_task: stopped")
    except BaseException as err:
        print("ERR: my_background_task, err: %s" % str(err) )
        

    
strToken = getEnv("TOKEN")
#~ print( strToken)


#~ update_thread = threading.Thread(target=updater, name="Updater", args="")
#~ update_thread.start()

client.loop.create_task(my_background_task())

client.run(strToken)