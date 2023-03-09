import time
import sentence_transformers
#~ from scipy.spatial.distance import cdist
#~ import numpy as np

print("INF: sentence_transformers: loading distiluse...")
print("WRN: don't know where is locally stored the used base!!!")
timeBegin = time.time()
model = sentence_transformers.SentenceTransformer('distiluse-base-multilingual-cased')
print("INF: sentence_transformers: loading distiluse - end (loaded in %.2fs)" % (time.time()-timeBegin))


def camEmbed(s):
    o = model.encode(s, show_progress_bar=False)
    #~ print("DBG: camEmbed: '%s' => %s" % (s,str(o)))
    # transform the nd_array en list:
    #~ print(type(o))
    #~ print(type(o[0]))
    #~ print(type(o[0][0]))
    
    o = o.tolist()
    
    #~ print("apres:")
    #~ print(type(o))
    #~ print(type(o[0]))
    #~ print(type(o[0][0]))

    return o

def camEmbedList(list_s):
    #~ o = model.encode(s, show_progress_bar=False)
    #~ print("DBG: camEmbed: '%s' => %s" % (s,str(o)))
    #~ return o
    return camEmbed(list_s)