# -*- coding: cp1252 -*-

class Student:
    def __init__( self, id ):
        self.id = id
        self.name = "e" + str(id)
        self.score = 500
        
    def __str__(self):
        s = ""
        s += "  id: %s\n" % self.id
        s += "  name: %s\n" % self.name
        s += "  score: %s" % self.score
        return s
        
class Tournoi:
    def __init__( self, nbr_student = 10 ):
        self.students = []
        for i in range(nbr_student):
            self.students.append(Student(i))
    
    def __str__(self):
        s = ""
        for e in self.students:
            s += str(e) + "\n\n"
        return s
        
    def findById(self,id):
        for e in self.students:
            if e.id == id:
                return e
        return -1
        
    def choose2player(self):
        return self.students[0],self.students[1] # todo better choice!
        
    def receive_new_result(self,id1,id2,pt1,pt2):
        e1 = self.findById(id1)
        e2 = self.findById(id2)
        print("INF: receive_new_result: %s contre %s: score: %d/%d" % (e1.name,e2.name,pt1,pt2))
        diff = pt1-pt2
        e1.score += diff
        e2.score -= diff
        
    
    
def tournoi_run():
    tournoi = Tournoi()
    while 1:
        print(tournoi)
        e1,e2 = tournoi.choose2player()
        print("%s rencontre %s" % (e1.name,e2.name) )
        score = input("donne moi les scores de chacun séparé par un /\npar exemple 1/0\n a toi: " )
        if score == "":
            break
        score1, score2 = score.split('/')
        score1 = int(score1)
        score2 = int(score2)
        tournoi.receive_new_result(e1.id,e2.id,score1,score2)
        
    
    
tournoi_run()
print("\nBye!")
