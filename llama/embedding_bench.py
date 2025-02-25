# -*- coding: utf-8 -*- 

import embedtools

from embedtools import *

dictSentencesTuples = {
	"J'ai faim": ("Je souhaiterai me sustenter", "y a til un restauran dans coin?" ),
	"J'ai envie de faire pipi!":  ("ou sont les toilettes?", "ou se trouve les ptit coin"),
	"Qui est le président de la france?": ( "Miterrand a été le président de la france entre 1981 et 1995", "Macron dirige notre pays a ce jour"),
	 "Qui est le président des états unis?": ( "Trump is the american president", "Trump est le président americain")
}

def test_perf_embed( strModelName ):
	"""
	return results of one model
	"""
	print( "" )
	computeMaximum( strModelName )
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
	for question, v1 in listQuestion:
		res = []
		for s2,v2 in listSolution:
			simi = compare_two_vect( v1,v2 )
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
		
	


strModelToCompare = ["granite-embedding:30m", "granite-embedding:278m", "snowflake-arctic-embed2", "bge-large", "paraphrase-multilingual","bge-m3",
"nomic-embed-text","mxbai-embed-large"]

for mod in strModelToCompare:
	test_perf_embed( mod )