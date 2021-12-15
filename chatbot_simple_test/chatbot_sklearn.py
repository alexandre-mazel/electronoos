# simple chatbot exploration for education purpose
# started from https://medium.com/analytics-vidhya/building-a-simple-chatbot-in-python-using-nltk-7c8c8215ac6e

# later look at: https://chatbotslife.com/how-to-create-an-intelligent-chatbot-in-python-c655eb39d6b1
# https://www.tophebergeur.com/blog/projet-chatbot-python/
# https://towardsdatascience.com/how-to-create-a-chatbot-with-python-deep-learning-in-less-than-an-hour-56a063bdfc44

import nltk # pip install nltk
import numpy as np
import random
import re
import string # to process standard python strings

if 0:
    nltk.download('punkt') # first-time use only
    nltk.download('wordnet') # first-time use only

f=open('chatbot.txt','r',errors = 'ignore')
raw=f.read()
raw=raw.lower()# converts to lowercase

# rough preprocessing.
raw=raw.replace("...", ".")
raw=raw.replace("..", ".")
raw=raw.replace("[4]", "")
#raw = re.sub("[\(\[].*?[\)\]]", "", raw) # replace [23] et (blabla)
raw = re.sub("[\[].*?[\]]", "", raw) # replace [23] 


sent_tokens = nltk.sent_tokenize(raw)# converts to list of sentences 
word_tokens = nltk.word_tokenize(raw)# converts to list of words

lemmer = nltk.stem.WordNetLemmatizer()

#WordNet is a semantically-oriented dictionary of English included in NLTK.
def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]
remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))
    
GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]

def greeting(sentence): 
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)
            
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

global_strPrev = None
def response(user_response):
    global global_strPrev
    robo_response=''
    sent_tokens.append(user_response)    
    print("sent_tokens:%s" % sent_tokens )
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    print("vals:%s" % vals )
    idx=vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]    

    if(req_tfidf==0):
        #~ print( "user_response: %s" % user_response )
        if user_response == global_strPrev:
            robo_response = robo_response+"Do you expect a different answer by repeating yourself?"
        else:
            if "what" in user_response or "who" in user_response or "how" in user_response:
                robo_response = robo_response+"I don't know, sorry!"
            else:
                robo_response = robo_response+"I am sorry! I don't understand you"
    else:
        if user_response == global_strPrev:
            robo_response += "I've told you before: "
        robo_response = robo_response+"I Know " + sent_tokens[idx]
    global_strPrev = user_response
    return robo_response
        
flag=True
print("ROBO: My name is Robo. I will answer your queries about Chatbots. If you want to exit, type Bye!")
while(flag==True):
    user_response = input()
    user_response=user_response.lower()
    if(user_response!='bye'):
        if(user_response=='thanks' or user_response=='thank you' ):
            flag=False
            print("ROBO: You are welcome..")
        else:
            if(greeting(user_response)!=None):
                print("ROBO: "+greeting(user_response))
            else:
                print("ROBO: ",end="")
                print(response(user_response))
                sent_tokens.remove(user_response)
    else:
        flag=False
        print("ROBO: Bye! take care..")
        
# current warning:
# d:\Python38-32\lib\site-packages\sklearn\feature_extraction\text.py:383: UserWarning: 
# Your stop_words may be inconsistent with your preprocessing. 
# Tokenizing the stop words generated tokens ['ha', 'le', 'u', 'wa'] not in stop_words.
#   warnings.warn('Your stop_words may be inconsistent with '
        

# only rare word will be looked in the sentence, and the bots will find for sentence containing them and display them

# try question like:
#~ what is a chatbot?
#~ what is eliza?
#~ describe chatbot design
# what is a text-to-speech? # will give you the chatbot definition, unless you explain explicitly what is a text to speech.