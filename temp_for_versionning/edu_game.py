import sys
sys.path.append("../../aruco_global/")
import aruco_def

import random

class EduGame:
    
    def __init__( self ):
        self.setLang("fr")
        self.loadPossible()

        
    def setLang( self, strNewLang ):
        self.strCurrentLang = strNewLang 
        
    def loadPossible( self ):
        self.listPossible = []
        for k,d in aruco_def.dictDesc.items():
            self.listPossible.append(d[self.strCurrentLang])
        
        
    def pickElement( self ):
        self.nIdxElement = random.randint(0, len(self.listPossible)-1)
        
    def chooseNextQuestion( self ):
        self.kFirstLetter = 0
        self.kJustShow = 1
        listQuestion = [
            # by first letter
            { 
                "fr": "montre moi quelquechose qui commence par un '%s'",  
            },
            # montre une carte
            { 
                "fr": "montre moi des %s",  
            }
        ]
        self.nQuestionMode = random.randint(0, len(listQuestion)-1)
        self.pickElement()
        self.strQuestion = listQuestion[self.nQuestionMode][self.strCurrentLang]
        strElement = self.listPossible[self.nIdxElement]
        if self.nQuestionMode == self.kFirstLetter:
            self.strQuestion = self.strQuestion % strElement[0]
        elif self.nQuestionMode == self.kJustShow:
            self.strQuestion = self.strQuestion % strElement
        self.strCorrectAnswer = strElement
        self.strHint = "you like that"
        
    def getQuestion( self ):
        return self.strQuestion
        
    def getHint( self ):
        return self.strHint
        
    def getCorrectAnswer( self ):
        return self.strCorrectAnswer

        
    def handleAnswer(self, strAnswer ):
        """
        return what to say
        """
        print( "DBG: handleAnswer: handling: '%s'" % strAnswer )
        
        bCorrect = False
        
        if self.nQuestionMode == self.kFirstLetter:
            bCorrect = strAnswer[0].lower() == self.strCorrectAnswer[0].lower()
        elif self.nQuestionMode == self.kJustShow:
            bCorrect = strAnswer.lower() == self.strCorrectAnswer.lower()
                
        if bCorrect:
            dAnswer = {
                                "fr": "Super!/Parfait!/Bravo!/C'est tout a fait ssa!",
                                "en": "Great!/Awesome!/Perfect!",
                            }
        else:
            dAnswer = {
                                "fr": "Essaye encore!/Presque",
                                "en": "Try again!",
                            }    
        li = dAnswer[self.strCurrentLang].split("/")
        idx = random.randint(0, len(li)-1)
        return li[idx]
        
eduGame = EduGame()


def autoTest():
    for i in range(10):
        print("============")
        eduGame.chooseNextQuestion()
        print("question: " + eduGame.getQuestion() )
        print("hint: " + eduGame.getHint() )
        print("answer: " + eduGame.handleAnswer("Carotte") )
        print("answer: " + eduGame.handleAnswer(eduGame.getCorrectAnswer()) )
    
    
    
if __name__ == '__main__':
    autoTest()
