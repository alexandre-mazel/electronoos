# -*- coding: utf-8 -*- 

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
}

def test_perf_embed( strModelName ):
	"""
	return results of one model
	"""
	time_begin = time.time()
	print( "" )
	computeMaximum( strModelName )
	coef_normalise = getNormalisation( strModelName )
	dummy = llama3_embedding( "text", strModelName )
	print( "INF: test_perf_embed: model '%s' has size %d" % ( strModelName, len( dummy ) ) )
	
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
		print( "%s => %s" % ( question, str(res) ) )
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
	return grand_total, duration

def run_bench():
	# cf https://ollama.com/library?sort=newest
	strModelToCompare = ["granite-embedding:30m", "granite-embedding:278m", "snowflake-arctic-embed2:568m", "snowflake-arctic-embed:335m",
	"snowflake-arctic-embed:110m", "snowflake-arctic-embed:22m", "bge-large:335m", 
	"paraphrase-multilingual:278m","bge-m3:567m", "nomic-embed-text","mxbai-embed-large:335m", "all-minilm:22m", "all-minilm:33m",
	# "mistral-large:123b",   Require 73 GiB
	"mistral-small:24b", 
	# "r1-1776:671b", # model requires more system memory (444.5 GiB) than is available (61.3 GiB)
	"openthinker:32b","olmo2:13b","olmo2:7b", "llama3.3:70B",
	"deepseek-r1:671b", "deepseek-r1:70b","deepseek-r1:8b", "deepseek-r1:1.5b",
	"qwen2.5-coder:32b", "qwen2.5-coder:0.5b",
	"olmo2:13b", "olmo2:7b","command-r7b:7b",
	]

	conclusion = []
	for mod in strModelToCompare:
		ret = test_perf_embed( mod )
		conclusion.append( (mod,*ret) )
		
	conclusion = sorted( conclusion, key = lambda x: x[1], reverse = True )
		
	print( "" )
	for mod,perf,t in conclusion:
		print( "%s: %.2f, %.2fs" % (mod,perf,t) )
		
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
"""