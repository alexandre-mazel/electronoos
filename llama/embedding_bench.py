# -*- coding: utf-8 -*- 

"""

A lancer tel quel depuis na@azure1: python3 embedding_bench.py

lister les modeles installe:
ollama list

voir les modeles existants:
https://ollama.com/library

"""


import time

from embedtools import *

dictSentencesTuples = {
    "J'ai faim": ("Je souhaiterai me sustenter", "y a til un restauran dans coin?" ),
    "J'ai envie de faire pipi!":  ("ou sont les toilettes?", "ou se trouve les ptit coin"),
    "Qui est le président de la france?": ( "Miterrand a été le président de la france entre 1981 et 1995", "Macron dirige notre pays a ce jour"),
    "Qui est le président des états unis?": ( "Trump is the american president", "Trump est le président americain"),
    "Je veux faire de l'internet": ( "Vous pouvez vous connecter sur notre réseau", "Le code du wifi est 123"),
    "J'ai 2 enfants": ( "J'ai un fils et une fille", "Mon grand s'appelle Corto et ma petite gaia"),
    "My best friend is nammed niko": ("niko is my best pal", "I've got one BFF"),
    "It's raining": ("there's no sun in the sky", "take an umbrella!"),
    "I like to code": ("I'm fan of computer programming", "My passion is python"),
    "Je suis fatigué": ("chuis crevé", "I'm exhausted"),
    "J'ai soif": ("j'ai la gorge séche!", "I'm thirsty"),
}

def test_perf_embed( strModelName ):
	"""
	return results of one model:
	note, duration, size of model
	"""
	time_begin = time.time()
	print( "" )
	computeMaximum( strModelName )
	coef_normalise = getNormalisation( strModelName )
	dummy = llama3_embedding( "text", strModelName )
	size_vector = len( dummy )
	print( "INF: test_perf_embed: model '%s' has size %d" % ( strModelName, size_vector ) )
	
	# for each sentence its vector
	listQuestion = []
	listSolution = []
	
	for k,ans in dictSentencesTuples.items():
		v = llama3_embedding( k, strModelName )
		listQuestion.append( ( k, v ) )
		for s in ans:
			v = llama3_embedding( s, strModelName )
			listSolution.append( ( s, v ) )
			
	# for each listQuestion, sort the list of solution
	grand_total = 0
	for question, v1 in listQuestion:
		res = []
		for s2,v2 in listSolution:
			simi = compare_two_vect( v1,v2 )/coef_normalise
			res.append( (s2, simi) )
		res = sorted( res, key = lambda x: x[1], reverse = True )
		print( "%s => %s" % ( question, str(res[:4]) ) )
		# compute score:
		nbr_good_solution = len( dictSentencesTuples[question] )
		# somme des n premiers (avec n = nbr_good_solution) si c'est un bon, on ajoute les points sinon on retranche
		tot = 0
		for txt, score in res[:nbr_good_solution]:
			if txt in dictSentencesTuples[question]:
				tot += score
			else:
				tot -= score
		print( "tot: %.3f" % tot )
		grand_total += tot
	duration = time.time() - time_begin
	print( "grand_total: %.2f (%.2fs)" % ( grand_total, duration ) )
	return grand_total, duration, size_vector

def run_bench():
    # cf https://ollama.com/library?sort=newest
    strModelToCompare = ["granite-embedding:30m", "granite-embedding:278m", "snowflake-arctic-embed2:568m", "snowflake-arctic-embed:335m",
    "snowflake-arctic-embed:110m", "snowflake-arctic-embed:22m", "bge-large:335m", 
    "paraphrase-multilingual:278m","bge-m3:567m", "nomic-embed-text","mxbai-embed-large:335m", "all-minilm:22m", "all-minilm:33m",
    # "mistral-large:123b",   Require 73 GiB
    "mistral-small:24b", 
    # "r1-1776:671b", # model requires more system memory (444.5 GiB) than is available (61.3 GiB)
    "openthinker:32b","olmo2:13b","olmo2:7b", "llama3.3:70B",
    # "deepseek-r1:671b", # model requires more system memory (444.5 GiB)
    "deepseek-r1:70b","deepseek-r1:8b", "deepseek-r1:1.5b",
    "qwen2.5-coder:32b", "qwen2.5-coder:0.5b",
    "olmo2:13b", "olmo2:7b","command-r7b:7b",
    # new dec2025
    "nomic-embed-text-v2-moe", "deepseek-v3.2","qwen3-embedding","embeddinggemma",
    ]
    
    # test juste une seule
    #~ strModelToCompare = ["paraphrase-multilingual:278m"]


    conclusion = []
    for mod in strModelToCompare:
        ret = test_perf_embed( mod )
        conclusion.append( (mod,*ret) )
        
    conclusion = sorted( conclusion, key = lambda x: x[1], reverse = True )
        
    print( "" )
    for mod,perf,t,size in conclusion:
        print( "%s: %.2f, %.2fs, %d" % (mod,perf,t,size) )
        
run_bench()

"""
paraphrase-multilingual: 8.05, 1.16s
mxbai-embed-large: 6.03, 1.09s
nomic-embed-text: 3.92, 0.38s
bge-large: 3.32, 0.82s
granite-embedding:30m: 3.15, 0.65s
granite-embedding:278m: 2.32, 1.11s
bge-m3: 2.02, 1.59s
snowflake-arctic-embed2: 0.57, 1.85s

paraphrase-multilingual:278m: 9.15, 1.11s, 768
mxbai-embed-large:335m: 7.54, 2.35s, 1024
nomic-embed-text: 5.40, 0.63s, 768
bge-large:335m: 4.84, 1.13s, 1024
granite-embedding:278m: 4.00, 1.36s, 768
granite-embedding:30m: 3.43, 0.59s, 384
all-minilm:33m: 3.00, 0.39s, 384
bge-m3:567m: 2.31, 2.13s, 1024
snowflake-arctic-embed:335m: 2.00, 1.11s, 1024
all-minilm:22m: 1.79, 0.35s, 384
snowflake-arctic-embed:110m: 1.49, 0.56s, 768
snowflake-arctic-embed2:568m: 0.98, 3.31s, 1024
command-r7b:7b: 0.16, 29.50s, 4096
deepseek-r1:8b: -1.29, 30.55s, 4096
olmo2:7b: -2.22, 16.29s, 4096
olmo2:7b: -2.22, 16.21s, 4096
mistral-small:24b: -2.53, 47.98s, 5120
llama3.3:70B: -2.67, 159.01s, 8192
snowflake-arctic-embed:22m: -3.27, 0.35s, 384
deepseek-r1:1.5b: -3.34, 10.06s, 1536
olmo2:13b: -4.01, 30.84s, 5120
olmo2:13b: -4.01, 30.01s, 5120
qwen2.5-coder:32b: -4.94, 177.42s, 5120
qwen2.5-coder:0.5b: -6.03, 8.08s, 896
openthinker:32b: -6.32, 71.69s, 5120
deepseek-r1:70b: -14.00, 16.15s, 2

# ajout de j'ai soif

#result: perf, duration, size of vector

paraphrase-multilingual:278m: 7.16, 2.17s, 768
mxbai-embed-large:335m: 6.06, 2.51s, 1024
granite-embedding:278m: 2.43, 0.34s, 768
nomic-embed-text: 1.79, 1.20s, 768
bge-large:335m: 1.65, 2.50s, 1024
granite-embedding:30m: 1.59, 0.68s, 384
bge-m3:567m: 0.61, 3.78s, 1024
all-minilm:33m: 0.53, 0.42s, 384
snowflake-arctic-embed:335m: 0.18, 2.49s, 1024
snowflake-arctic-embed2:568m: -0.73, 4.52s, 1024
all-minilm:22m: -1.30, 0.37s, 384
olmo2:7b: -4.04, 18.55s, 4096
olmo2:7b: -4.04, 18.16s, 4096
deepseek-r1:8b: -4.97, 20.22s, 4096
snowflake-arctic-embed:22m: -5.28, 0.37s, 384
command-r7b:7b: -5.35, 21.58s, 4096
llama3.3:70B: -6.05, 169.22s, 8192
deepseek-r1:1.5b: -7.27, 6.72s, 1536
snowflake-arctic-embed:110m: -7.39, 0.88s, 768
olmo2:13b: -7.62, 25.33s, 5120
olmo2:13b: -7.62, 32.10s, 5120
mistral-small:24b: -7.90, 50.22s, 5120
openthinker:32b: -10.75, 40.85s, 5120
qwen2.5-coder:0.5b: -12.35, 2.55s, 896
qwen2.5-coder:32b: -13.58, 74.47s, 5120
deepseek-r1:70b: -18.00, 19.44s, 2

Meme sur paraphrase-multilingual:278m s'en sort pas trop sur j'ai soif:

'J'ai froid'  and  'je me caille'  => 2.8595345530512675
'I'm hungry'  and  'I'm starving'  => 8.466821471644218
INF: test_perf_embed: model 'paraphrase-multilingual:278m' has size 768
J'ai faim => [("I'm thirsty", 0.7923809705956506), ("I'm exhausted", 0.4834252014032695), ("j'ai la gorge séche!", 0.4214443468861655), ('y a til un restauran dans coin?', 0.4097194857729548)]
tot: -1.276
J'ai envie de faire pipi! => [("I'm thirsty", 0.6244056071941099), ('ou sont les toilettes?', 0.5259703783277306), ("I'm exhausted", 0.5194781354631381), ("j'ai la gorge séche!", 0.5023622428982034)]
tot: -0.098
Qui est le président de la france? => [('Miterrand a été le président de la france entre 1981 et 1995', 0.7446398305010291), ('Macron dirige notre pays a ce jour', 0.6515631185364261), ('Trump is the american president', 0.535406211748082), ('Trump est le président americain', 0.48915112992921356)]
tot: 1.396
Qui est le président des états unis? => [('Trump is the american president', 0.7493338340572933), ('Trump est le président americain', 0.6626388286772472), ('Macron dirige notre pays a ce jour', 0.3752802905838617), ('Miterrand a été le président de la france entre 1981 et 1995', 0.29201365479951824)]
tot: 1.412
Je veux faire de l'internet => [("I'm fan of computer programming", 0.518464281114967), ('Vous pouvez vous connecter sur notre réseau', 0.465968238648577), ('My passion is python', 0.30708735485375516), ("J'ai un fils et une fille", 0.26489765983253605)]
tot: -0.052
J'ai 2 enfants => [("J'ai un fils et une fille", 1.0169074593232685), ("Mon grand s'appelle Corto et ma petite gaia", 0.527087481403709), ("I've got one BFF", 0.4947460129958295), ("I'm exhausted", 0.42109624763046904)]
tot: 1.544
My best friend is nammed niko => [('niko is my best pal', 0.975828244601806), ("I've got one BFF", 0.45576643946085293), ("Mon grand s'appelle Corto et ma petite gaia", 0.378871708115092), ("J'ai un fils et une fille", 0.34977433746330305)]
tot: 1.432
It's raining => [('take an umbrella!', 0.7901310156989527), ("I'm thirsty", 0.48560923450108584), ("there's no sun in the sky", 0.39440805703970094), ("I'm exhausted", 0.286574000086776)]
tot: 0.305
I like to code => [("I'm fan of computer programming", 0.8877951140351171), ('My passion is python', 0.46945351077507935), ('Vous pouvez vous connecter sur notre réseau', 0.2988296985040168), ("J'ai un fils et une fille", 0.2611301787046304)]
tot: 1.357
Je suis fatigué => [("I'm exhausted", 1.0559149382119863), ("I'm thirsty", 0.6031465687296327), ("j'ai la gorge séche!", 0.5009767737447337), ("J'ai un fils et une fille", 0.36833398358574476)]
tot: 0.453
J'ai soif => [("I'm thirsty", 1.2155130592654564), ("I'm exhausted", 0.5298759541063871), ("j'ai la gorge séche!", 0.4518681150264819), ('ou sont les toilettes?', 0.38879305816375886)]
tot: 0.686
grand_total: 7.16 (0.58s)

"""