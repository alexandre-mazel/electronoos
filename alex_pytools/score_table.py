import csv_loader
import datetime

class ScoreTable:
    """
    a score table.
    Saved ordered from best to less best
    """
    def __init__( self, strGameName, bMinimumIsBest = False, encoding="utf-8" ):
        self.strGameName = strGameName
        self.bMinimumIsBest = bMinimumIsBest
        self.load( encoding = encoding )
        
    def reset(self):
        self.listScore = [] # list of pair (score,name,date and time)
        
    def load( self, encoding="utf-8"):
        self.listScore = csv_loader.load_csv( "/tmp/score_%s.dat" % self.strGameName,encoding=encoding)
        
    def save( self ):
        csv_loader.save_csv( "/tmp/score_%s.dat" % self.strGameName, self.listScore )
        
    def add_score(self, score, name):
        datetimeObject = datetime.datetime.now()
        strTimeStamp = datetimeObject.strftime( "%Y/%m/%d: %Hh%Mm%Ss" )
        for i in range(len(self.listScore)):
            if \
                    ( self.bMinimumIsBest and score < self.listScore[i][0] ) \
                or \
                    ( not self.bMinimumIsBest and score > self.listScore[i][0] ) \
            :
                self.listScore.insert(i,[score,name,strTimeStamp]) # we store [] and not (), as csv will reload []
                break
        else:
            self.listScore.append([score,name,strTimeStamp])
        
        
    def get_best( self ):
        """
        return score,name of the best
        """
        if len(self.listScore) < 1:
            if self.bMinimumIsBest: return 9999,"Unknown"
            else: return -1,"Unknown"
        return self.listScore[0]
        
    def get_rank(self,score):
        """
        return rank 0..n
        """
        for i in range(len(self.listScore)):
            if \
                    ( self.bMinimumIsBest and score < self.listScore[i][0] ) \
                or \
                    ( not self.bMinimumIsBest and score > self.listScore[i][0] ) \
            :
                return i
        return len(self.listScore)
                
    def get_results( self, nLimitTo = -1 ):
        s = ""
        nRank = 1
        if self.bMinimumIsBest:
            strScoreFormat = "%5.3f"
        else:
            strScoreFormat = "%d"
        
        for scorepair in self.listScore:
            strTimeStamp = ""
            #~ print("scorepair: %s" % str(scorepair))
            if len(scorepair)>2:
                strTimeStamp = "(" + scorepair[2] + ")"
            strFormat = "\t%3d: SCORE_FORMAT - %s \t\t%s\n".replace("SCORE_FORMAT",strScoreFormat)
            s += strFormat % ( nRank, scorepair[0], scorepair[1], strTimeStamp )
            if nLimitTo != -1 and nRank >= nLimitTo:
                break
            nRank += 1
        return s

# ScoreTable - end

def autotest():
    st = ScoreTable("autotest")
    st.reset()
    st.add_score(10,"Alex")
    st.add_score(12,"JP")
    st.add_score(3,"Pat")
    assert(st.get_best()[:2] == [12,"JP"])
    st.save()
    
    st2 = ScoreTable("autotest")
    
    s1 = st.get_results()
    s2 = st2.get_results()
    print("s1:\n%s" % s1 )
    print("s2:\n%s" % s2 )
    assert(s1==s2)
    print("s1 best: %s" % str(st.get_best()) )
    print("s2 best: %s" % str(st2.get_best()) )
    assert(str(st.get_best()) == str(st2.get_best()))
    
    stmin = ScoreTable("autotest_min", bMinimumIsBest = True)
    stmin.reset()
    stmin.add_score(10,"Alex")
    stmin.add_score(12,"JP")
    stmin.add_score(3,"Pat")
    assert(stmin.get_best()[:2] == [3,"Pat"])

    
if __name__ == "__main__":
    autotest()