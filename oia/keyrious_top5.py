import os
    
def save_top5(top5,filename="score.txt"):
  """
  Sauve le top5.
  Le fichier sera du type:
SCORE1, NOM1
SCORE2, NOM2
SCORE3, NOM3
  """
  file = open(filename,"w")
  for score, name in top5:
    file.write("%s,%s\n"%(score,name))
  file.close()
  
def load_top5(filename="score.txt"):
  """Charge le top5
  Retourne un tableau avec des paires score,nom
  par exemple: [[18,"Alex"],[17,"toto"]]
  """
  if not os.path.isfile(filename):
    return []
  file = open(filename,"r")
  top5 = []
  while 1:
      line = file.readline().replace('\n','')
      print("DBG: load_top5 read readline: " + str(line) )
      if len(line)<2:
          break
      datas = line.split(',')
      datas[0] = int(datas[0]) # convert score from str to int
      top5.append(datas)
  file.close()
  return top5

    
def find_rank(top5,new_score):
  """Cherche dans le top5 la place de score
  Retourne la place entre 0 et 4, ou 100 si pas dans le top5
  """
  i = 0
  while i < len(top5):
    score,name = top5[i]
    if new_score > score:
      print("DBG: find_rank: found better at rank: " + str(i))
      return i
    i += 1
        
  if len(top5)<5:
    return len(top5)
        
  return 100
    
def update_rank(top5,new_score,new_name):
  position = find_rank(top5,new_score)
  new_top5 = top5[:4]
  new_top5.insert(position,[new_score,new_name])
  print("DBG: update_rank, top5 is now:" + str(new_top5) )
  return new_top5

def run_unit_test():
  filename_test = "test.txt"
  # erase the file: to start with a fresh configuration
  try: 
      os.unlink(filename_test) 
  except FileNotFoundError: pass
  top5 = load_top5(filename_test)
  assert(top5 == [])
  r = find_rank(top5,10)
  print(r)
  assert(r==0)
  top5=update_rank(top5,10,"Alex")
  assert(find_rank(top5,10)==1)
  assert(find_rank(top5,12)==0)
  top5=update_rank(top5,13,"Toto")
  top5=update_rank(top5,3,"John")
  top5=update_rank(top5,6,"Pat")
  top5=update_rank(top5,8,"Greg")
  top5=update_rank(top5,12,"Gg")
  
  assert(top5==[[13, 'Toto'], [12, 'Gg'], [10, 'Alex'], [8, 'Greg'], [6, 'Pat']])
    
  assert(find_rank(top5,10)==3)
  assert(find_rank(top5,5)==100)    
    
  save_top5(top5,filename_test)
  loaded_top5 = load_top5(filename_test)
  print(top5)
  print(loaded_top5)  
  assert(top5==loaded_top5)


def run_game():                
    filename = "score.txt"
    score = game()

    top5 = load_top5(filename)

    rank_num = find_rank(top5,score)

    if idx < 5:
        name = input("bravo, tu es dans le top 5, entre ton nom")
        top5=update_rank(top5,score,name)
        save_top5(top5,filename)


run_unit_test()
#~ run_game()

