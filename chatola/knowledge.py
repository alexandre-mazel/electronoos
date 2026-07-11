import json
import numpy
import os
import pure_http_embedding_httpclient
import sys
import time

class Knowledge:
    
    def __init__( self ):
        self.infos = [] # a list of informations
        self.details = {} # an info => txt: a long texte about the infos. (info is seen as a summary of infos)
        self.vects = [] # embedding related to each informations
        self.model = "nomic-embed-text" # resultat bof, mais rapide (565MB) (rapide: 13s for 106 sentence)
        self.model = "qwen3-embedding" # (7GB for 8K context) (plus long: 144s for 106 sentence)
        self.host = "localhost"
        self.port = 11434
        
        if os.name == "nt":
            self.host = "obo-world.com"
            self.port = 11434
            
        self.savefile = "datas/precomputed.dat"
        self._loadPrecalc()
        
    # TODO: move all precalc method to purehttpembedding (else it helps even for students)
            

    def _savePrecalc(self) -> None:
        if not self.must_save:
            return
            
        print( "INF: EmbedScore._save: starting..." )
        time_begin = time.time()
        
        """Save dictionary of vectors to a JSON file."""
        with open(self.savefile, "w", encoding="utf-8") as f:

            json.dump(self.sentencesToVector, f, indent=2)
            print( "INF: EmbedScore._save: saved to '%s': OK" % (self.savefile) )
            self.must_save = False
            duration = time.time() - time_begin
            print( "INF: EmbedScore._save: %d precomputed sentence(s) saved in %.2fs" % ( len(self.sentencesToVector), duration ) )

    def _loadPrecalc(self) -> None:
        """Load dictionary of vectors from a JSON file."""
        time_begin = time.time()
        
        print( "INF: EmbedScore._load: starting..." )
        try:
            with open(self.savefile, "r", encoding="utf-8") as f:
                data = json.load(f) # 15s sur 17s
                
            print( "INF: EmbedScore._load: converting..." ) # 2s sur 17s

            # Optional: validate that values are lists of numbers
            self.sentencesToVector = {
                str(k): [float(x) for x in v]
                for k, v in data.items()
                if isinstance(v, list)
            }
        except BaseException as err:
            print( "WRN: EmbedScore._load: err: %s" % (err) )
            self.sentencesToVector = {}
            
        duration = time.time() - time_begin
        self.must_save = False
        print( "INF: EmbedScore._load: %d precomputed sentence(s) loaded in %.2fs" % ( len(self.sentencesToVector), duration ) )

            
        
    def _get_embed( self, sentence ):
        try:
            v = self.sentencesToVector[sentence]
            if len(v) > 10:
                return v
        except KeyError:
            pass
            
        v =  pure_http_embedding_httpclient.get_embedding( sentence, model = self.model, host = self.host, port = self.port )
        self.sentencesToVector[sentence] = v
        self.must_save = True
        return v
        
    def addKnowlegdeFromTxtOneLiner( self, filename ):
        """
        Add knowledge from a txt file: one line contains information about one thing.
        eg: dataset_paris_16_rue_jean_richepin.txt
        """
        f  = open( filename, "rt", encoding = "utf-8" )
        data = f.read()
        lines = data.split("\n")
        for line in lines:
            print( "DBG: addKnowlegdeFromTxtOneLiner: '%s'" % line )
            self.infos.append( line )
            
    def addKnowlegdeFromXlsX( self, filename ):
        """
        Format: URL, Titre, Contenus
        eg: Actus WKDO - The Clinic.xlsx
        pb: la zone contenus peut contenir des retours chariots !!!
        """
        print( "INF: addKnowlegdeFromXlsX: Loading '%s'" % filename )
        sys.path.append( "../alex_pytools/" )
        import csv_loader
        dic = csv_loader.load_datas_from_xlsx( filename, replace_eol = ". ", bVerbose = 0 )
        print("DBG: addKnowlegdeFromXlsX: keys: %s" % str(dic.keys() ) )
        datas = dic[list(dic.keys())[0]]
        for data in datas[1:]: # skip headers
            #~ print(data)
            #~ print(len(data))
            url, title, contents = data
            print( title )
            #~ self.infos.append( title + ";" + contents )
            self.infos.append( title )
            self.details[title] = contents
            # TODO: comparer le vecteur d'un titre et du contenu ? (c'est tellement long le calcul du contenu que ca fait hésiter)
        #~ exit(1)
        
        
            
    def computeEmbedding( self ):
        """
        (re)compute the embedding of each info
        """
        self.vects = []
        timeBegin = time.time()
        for info in self.infos:
            print( "INF: computeEmbedding: '%s'" % info )
            self.vects.append( self._get_embed( info ) )
        print( "INF: computeEmbedding: %d sentence(s), duration: %.1fs" % (len(self.infos), (time.time() - timeBegin) ) )
        self._savePrecalc()
        
    def getKnowledgeForQuestion( self, question, max=12, verbose = False ):
        """
        return the max best sentence related to a current question
        """
        v = self._get_embed( question )
        assert( len(self.infos) == len(self.vects) )
        res = []
        for i in range( len( self.vects) ):
            simi = numpy.dot( self.vects[i], v )
            res.append( ( simi, self.infos[i] ) )
            
        mosted = sorted( res, reverse=True )
        if verbose:
            print( "\nDBG: getKnowledgeForQuestion: res for question '%s'" % (question) )
            for v in mosted:
                print( v )
        
        out = []
        for idx, v in enumerate( mosted[:max] ):
            if "qwen3" in self.model and v[0] < 0.55: # sinon on pourrait mettre 0.42 si on en veut plus...
                break
            if verbose or 1:
                print( "DBG: getKnowledgeForQuestion: ending with: %d: %s (%.2f) " % (idx, v[1],v[0]) )
            out.append(v[1])
            if v[1] in self.details and v[0] > 0.65 and idx < 6: # ne pas mettre des tonnes d'infos si on n'est pas sur (sinon Hello prend 3 plombes: 150sec)
                # on a un gros texte par rapport a cette infos
                out.append(self.details[v[1]])
        return out
   
knowledge = Knowledge()      
def classic_init():
    global knowledge
    knowledge.addKnowlegdeFromTxtOneLiner( "datas/dataset_paris_16_rue_jean_richepin.txt" )
    knowledge.addKnowlegdeFromXlsX( "datas/Actus WKDO - The Clinic.xlsx" )
    knowledge.computeEmbedding()
    
def get_knowledge_related_to( question, max=12, verbose = False ):
    global knowledge
    return knowledge.getKnowledgeForQuestion( question, max=max, verbose = verbose )
    
def autotest():
    global knowledge
    classic_init()
    verbose = 1
    knowledge.getKnowledgeForQuestion( "ou manger une pizza ?", verbose=verbose ) # pas de chance rien au dessus de 0.50!
    knowledge.getKnowledgeForQuestion( "ou manger une pizza italienne?", verbose=verbose )
    knowledge.getKnowledgeForQuestion( "j'ai faim, ou aller ?", verbose=verbose )
    knowledge.getKnowledgeForQuestion( "je veux voir des sculptures de Rodin", verbose=verbose )
    knowledge.getKnowledgeForQuestion( "je veux manger libanais", verbose=verbose )
    knowledge.getKnowledgeForQuestion( "quel est la station de metro la plus proche?", verbose=verbose )
    knowledge.getKnowledgeForQuestion( "Hello", verbose=verbose )
    knowledge.getKnowledgeForQuestion( "Parle moi des exosomes", verbose=verbose )
    
    # timing pour 12 questions avec details de la clinique (long) (J'ai dépasse les 8k token):  
    # "total_duration":456310328028,"load_duration":3331023098,"prompt_eval_count":8192,"prompt_eval_duration":450818778459,"eval_count":12,"eval_duration":1603491810
    # => 456 sec soit 7.6min
    
if __name__ == "__main__":
    autotest()
    
        