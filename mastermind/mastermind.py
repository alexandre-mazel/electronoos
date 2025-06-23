import json
import os
import random
import time

# Define the colors (you can adjust them as you prefer)
COLOR_PALETTE = [
    (255, 0, 0),   # Red
    (0, 0, 255),   # Blue
    (0, 255, 0),   # Green
    (255, 255, 0), # Yellow
    (255, 165, 0), # Orange
    (128, 0, 128), # Purple
    (255, 255, 255), # White
    (0, 0, 0)      # Black
]

def draw_mastermind_plate(screen, color_lists, position=(50, 50), peg_radius=20, spacing=30):
    """
    Draws a plate for the Mastermind game on the given screen.
    
    :param screen: The pygame screen object to draw on.
    :param color_lists: List of lists, each containing integers that represent colors.
    :param position: The (x, y) position to start drawing from.
    :param peg_radius: The radius of each peg (circle).
    :param spacing: The distance between pegs in each row.
    """
    x, y = position
    
    # Iterate over each list in the color_lists
    for row in color_lists:
        for i, color_index in enumerate(row):
            if 0 <= color_index < len(COLOR_PALETTE):
                pygame.draw.circle(screen, COLOR_PALETTE[color_index], (x + i * spacing, y), peg_radius)
        y += spacing  # Move to the next row
        
def getAvailableRam():
    #~ GB=1024*1024*1024.
    try:
        import psutil
        infomem = psutil.virtual_memory()
        avail = infomem.available
        tot = infomem.total
        #~ avail = tot-avail # seems like it's reverted at least on raspberry [but not exactly !?!]
    except BaseException as err:
        #~ print("ERR: %s" % err)
        import os
        avail = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_AVPHYS_PAGES') 
        tot = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') 
    return avail,tot
    

def compute_goodbad( guess, solution ):
    """
    Compute good bad for a guess
    """
    good = 0
    bad = 0
    for idx,n in enumerate(guess):
        if n == solution[idx]:
            good += 1
        else:
            try:
                idxfound = solution.index(n)
                if idxfound != -1 and solution[idxfound] != guess[idxfound]:
                    bad += 1
            except ValueError as err:
                continue # not in list
                
    return good, bad
    
def compute_goodbad_compacted( guess, solution ):
    good = 0
    bad = 0
    for idx,n in enumerate(guess):
        if n == solution[idx]:
            good += 1
        else:
            try:
                idxfound = solution.index(n)
                if idxfound != -1 and solution[idxfound] != guess[idxfound]:
                    bad += 1
            except ValueError as err:
                continue # not in list
    return good*16+bad # assume less than 16 color
        
def compute_allgoodbad( board, solution ):
    """
    compute all good bad for a board and a given solution
    """
    out = []
    for guess in board:
        out.append( compute_goodbad(guess,solution) )
    return out
        
def compute_next_shot( board, listgoodbad, nbr_choice, nbr_color ):
    """
    Decide what is the best guess to play
    """
"""
    print("DBG: compute_next_shot: board: %s, listgoodbad: %s" % ( str(board), str(listgoodbad) ) )
    possible_colors = [] # for each choice, probability of each color
    for i in range(nbr_choice):
        possible_colors.append([])
        for j in range(nbr_color):
            possible_colors[-1].append(1)
    print("possible_colors:", possible_colors)
    
    for i in range(len(board)):
        guess = board[i]
        good,bad = listgoodbad[i]
        proba = (bad / nbr_choice) + 3*(good / nbr_choice)
        for n in guess:
            for j in range(nbr_choice):
                possible_colors[j][n] *= proba
        
    # based on proba, pick one color for each choice
    print("possible_colors (2):", possible_colors)
    cpt_same = 0
    prev_guess = []
    while 1:
        new_guess = []
        for i in range(nbr_choice):
            s = sum(possible_colors[i])
            pick = random.random()*s
            cnt = 0
            for j in range(nbr_color):
                cnt += possible_colors[i][j]
                print("pick: ", pick, ", cnt:", cnt )
                if pick <= cnt:
                    color = j
                    print("play color:", color )
                    new_guess.append(color)
                    break
            else:
                assert(0)
        print("DBG: compute_next_shot: new guess tentativ: ", new_guess, "possible_colors: ", possible_colors )
        if not new_guess in board:
            break
        print("was in board:", board )
        if new_guess == prev_guess:
            cpt_same += 1
            if cpt_same > 100:
                print("NEW GUESS LOCKED, exiting")
                print("rappel: compute_next_shot: board: %s, listgoodbad: %s" % ( str(board), str(listgoodbad) ) )
                #time.sleep(10)
                break
        else:
            prev_guess = new_guess
            
    return new_guess
"""

"""
def simulate_play( shot, solution, board, nbr_choice, nbr_color ):
    print("\nDBG: simulate_play: shot: %s, solution: %s, board: %s" % (str(shot), str(solution), str(board)) ) 
    good,bad = compute_goodbad( shot, solution )
    if good == nbr_choice:
        return 1
    if solution in board:
        return 0 # should be stopped before
    board.append( shot )
    listgoodbad = compute_allgoodbad(board,solution)
    next_shot = compute_next_shot( board, listgoodbad, nbr_choice, nbr_color )
    return 1+simulate_play( next_shot, solution, board[:], nbr_choice, nbr_color )
"""
    
class MasterMindAI:
    def __init__( self ):
        pass
        
    def start_new_game( self, nbr_choice = 4, nbr_color = 8 ):
        
        self.nbr_choice = nbr_choice
        self.nbr_color = nbr_color
        self.possible_answers = []
        
        self.next_guesses = [] # all guess to follow, when no more, compute them on the fly
        if 1:
            # hard coding first guess
            self.next_guesses.append( [] )
            for i in range( self.nbr_choice ):
                self.next_guesses[-1].append( i % self.nbr_color )
            
            # optim: mettre le premier en double ?
            #~ self.next_guesses[-1][1] = self.next_guesses[-1][0]
            
            self.next_guesses[-1] = tuple(self.next_guesses[-1])
        
        for i in range(self.nbr_color**self.nbr_choice):
            answer = []
            for j in range(self.nbr_choice):
                answer.append(i%self.nbr_color)
                i //= self.nbr_color
            self.possible_answers.append( tuple(answer) )
        print( "DBG: MasterMindAI.start_new_game: possible_answers: ", self.possible_answers )
        print( "DBG: MasterMindAI.start_new_game: possible_answers: len: ", len(self.possible_answers) )
        print( "DBG: MasterMindAI.start_new_game: next_guesses: ", self.next_guesses ) # 4096 for 4 choice in 8 colors
        
        print( "DBG: generating resultGuessAnswer...")
        time_begin = time.time()
        ram_begin, _ = getAvailableRam()
        
        # a dict for each guess: for each answer, the associated goodbad
        
        strPrecalcFilename = "ai_precalc_guess_answer_%d_%d.dat" % (self.nbr_choice,self.nbr_color)
        if os.path.isfile( strPrecalcFilename ) and 0:
            # ca marche pas, on ne peut pas sauver un dict de tuple, et c'est long a convertir en paire, il faudrait refaire toute l'ia en ne pas sauvant des tuples, mais des chaines de combinaisons
            # bref, ca ne m'amuse pas trop...
            print( "DBG: MasterMindAI.start_new_game: Using precalc from '%s'" % strPrecalcFilename )
            f = open( strPrecalcFilename, "rt" )
            json.load(f)
            f.close()
        else:
            self.resultGuessAnswer = {}
            
            for guess in self.possible_answers:
                d = {}
                for answer in self.possible_answers:
                    goodbad = compute_goodbad_compacted( guess, answer )
                    d[answer] = goodbad
                self.resultGuessAnswer[guess] = d
            if 0:
                # save to precalc file
                print( "DBG: MasterMindAI.start_new_game: Saving precalc to '%s'" % strPrecalcFilename )
                f = open( strPrecalcFilename, "wt" )
                #~ dict_not_using_tuple_as_key = [ {'key': k, 'value': v} for k, v in self.resultGuessAnswer.items() ]
                #~ dict_not_using_tuple_as_key = [ (k, v) for k, v in self.resultGuessAnswer.items() ]
                #~ print(dict_not_using_tuple_as_key)
                json.dump(self.resultGuessAnswer,f)
                f.close()
            
        print( "DBG: generating resultGuessAnswer: takes %.2fs" % (time.time() - time_begin) ) # mstab7: for 4,8: 26s
        ram_end, _ = getAvailableRam()
        print( "DBG: generating resultGuessAnswer: takes %.3fGB RAM" % ( (ram_begin-ram_end)/(10**9) ) ) # mstab7: for 4,8: 1.7GB  - storing 1 int instead of a pair => 0.6GB
        
    def get_next_guess( self ):
        if len( self.next_guesses) > 0:
            guess = self.next_guesses.pop(0)
            return guess
        # compute on the fly
        # dumb guess: the first possible
        print("WARNING: get_next_guess: we should never goes here")
        time.sleep(3)
        return self.possible_answers[0]
        
    def update_result_of_last_guess( self, guess, goodbad ):
        # remove from all possible answer
        # WRN: goodbad need to be a tuple
        
        goodbad = goodbad[0] * 16 + goodbad[1]
        
        time_begin = time.time()
        
        print( "DBG: update_result_of_last_guess: starting...")
        
        # Reduce impossible answer
        i = 0
        while i < len( self.possible_answers ):
            this_goodbad = compute_goodbad_compacted( guess, self.possible_answers[i] )
            #~ print( "DBG: update_result_of_last_guess: for answer: ", self.possible_answers[i], ", this_goodbad: ", this_goodbad, ", refgoodbad:", goodbad )
            if  this_goodbad != goodbad or guess == tuple(self.possible_answers[i]):
                # remove this guess from the guess/max_number
                del self.resultGuessAnswer[self.possible_answers[i]]
                # remove this possible answer
                del self.possible_answers[i]
                
            else:
                i += 1
        print( "DBG: MasterMindAI.update_result_of_last_guess: possible_answers: %d: %s" % ( len( self.possible_answers ), self.possible_answers ) )
        
        
        # return # returning here will take the first possible_answer (fast but not optimal)
        
        
        print( "DBG: MasterMindAI.update_result_of_last_guess: computing minmax..." )
        
        # reduce dictionnary
        dictGuessMaxNumberSameGoodBad  = {}
        for guess, answergoodbad in self.resultGuessAnswer.items():
            # remove deleted answer
            for answer in list(answergoodbad.keys()):
                if answer not in self.possible_answers:
                    del self.resultGuessAnswer[guess][answer]
            # group answer giving same score
            dictGoodBadAnswer = {}
            for answer, goodbad in answergoodbad.items():
                if goodbad not in dictGoodBadAnswer:
                    dictGoodBadAnswer[goodbad] = 1
                else:
                    dictGoodBadAnswer[goodbad] += 1
            valmax = max(dictGoodBadAnswer.values())
            dictGuessMaxNumberSameGoodBad[guess] = valmax
            
        # find key with the least maxvalue (the one which in the worst case of unknowing with solution it is will be the smaller)
        val_min = 2**64
        guess_min = None
        for guess,val in dictGuessMaxNumberSameGoodBad.items():
            if val_min > val:
                val_min = val
                guess_min = guess
                
        print( "DBG: update_result_of_last_guess: finishing with guess: %s (val_min: %d)" % (str(guess_min), val_min) )
        self.next_guesses.append(guess_min)
        
        print( "DBG: MasterMindAI.update_result_of_last_guess: takes %.2fs" % (time.time() - time_begin) )
        
# MasterMindAI - end
        

class MasterMindGame:
    def __init__( self, nbr_choice = 4, nbr_color = 8 ):
        """
        the color are 0..nbr_color-1
        """
        self.nbr_choice = nbr_choice
        self.nbr_color = nbr_color
        self.reset()
        
    def reset( self ):
        self.board = []    # a list of a each guesses at each turn
        self.goodbad = [] # for each turn, the number of well placed and misplaced
        self.solution = [] # the good solution
        
    def render_plate( self ):
        print("-"*8)
        for num_guess, guess in enumerate(self.board):
            print(guess, ", well placed: ", self.goodbad[num_guess][0], ", misplaced: ", self.goodbad[num_guess][1] )
        print("-"*8)
        
    def render_solution( self ):
        print(self.solution, "solution" )
        
    def generate_random_solution( self ):
        for i in range(self.nbr_choice):
            color = random.randint(0,self.nbr_color-1)
            self.solution.append( color )
            
    def human_guess_play( self, guess ):
        """
        return True if shot is correct
        """
        if len(guess) != self.nbr_choice:
            return False
            
        self.board.append([])
        for c in guess:
            self.board[-1].append(int(c))
        return True
            
    def compute_goodbad( self ):
        """
        Return True when human last guess is all correct
        """
        
        if len(self.goodbad) == len(self.board):
            return self.goodbad[0] == self.nbr_choice
            
        good,bad = compute_goodbad( self.board[-1], self.solution )


        self.goodbad.append([good,bad])
        
        return good == self.nbr_choice
        
    def get_last_goodbad( self ):
        return tuple(self.goodbad[-1])
        
    def computer_guess( self ):
        """
        based only on previous guess and goodbad, the compute need to pick a choice
        """
    """
        #~ if len(self.board) == 0:
            #~ return [0,1,2,3]
        #~ if len(self.board) == 1:
            #~ return [4,5,6,7]
            
        #~ possible_combination = []
        #~ for i in range(self.nbr_choice):
            #~ possible_combination.append([])
            #~ for j in range(self.nbr_color):
                #~ possible_combination[-1].append(j)
        #~ print(possible_combination)
        
        # compute all possible combination
        all_possible = []
        for i in range(self.nbr_color**self.nbr_choice):
            choice = []
            for j in range(self.nbr_choice):
                choice.append(i%self.nbr_color)
                i //= self.nbr_color
            all_possible.append(choice)
        print( "all_possible:", all_possible )
        
        min_total = 10**10
        min_guess = None
        
        for guess in all_possible:
            total_nbr_shot = 0
            for possible_solution in all_possible:
                nbr_shot = simulate_play( guess, possible_solution, self.board[:], self.nbr_choice, self.nbr_color )
                print("nbr_shot for guess %s: %d (with solution %s)\n" % (str(guess), nbr_shot, str(possible_solution) ) )
                total_nbr_shot += nbr_shot
            if total_nbr_shot < min_total:
                min_total = total_nbr_shot
                min_guess = guess
        
        print( "INF: min_guess: ", min_guess )
        
        return min_guess
    """
        
    def human_guess_run_game( self, forced_solution = [] ):
        
        self.reset()
        if forced_solution == []:
            self.generate_random_solution()
        else:
            self.solution = forced_solution
        
        #~ self.render_solution()
        self.render_plate()
        
        nbr_turn = 0
        while 1:


            while 1:
                if nbr_turn == 0:
                    guess = "0123"
                    guess = "0023"
                else:
                    guess = input("your choice(eg: 0123) ?\n")
                if self.human_guess_play(guess):
                    break
                print("Bad input, try again!")
            
            is_finished = self.compute_goodbad()
            
            if nbr_turn > 9:
                self.render_solution()
                
            self.render_plate()
            
            nbr_turn += 1
            
            if is_finished:
                break
                
        print( "Game finished in %d turn(s)" % nbr_turn )
        
        
    def cpu_guess_run_game( self, human_solution = [] ):
        """
        The computer need to guess the correct solution.
        human_solution: the combination made by the human or [] to pick a random one
        """
        self.reset()
        self.render_plate()
        
        if human_solution == []:
            self.generate_random_solution()
        else:
            self.solution = human_solution
            
            
        ai = MasterMindAI()
        ai.start_new_game( self.nbr_choice, self.nbr_color )
        
        nbr_turn = 0
        while 1:
            guess = ai.get_next_guess()
            if guess == None:
                print("Computer abort")
                break
            self.board.append(guess)
        
            is_finished = self.compute_goodbad()
            
            self.render_solution()
                
            self.render_plate()
            
            nbr_turn += 1
            
            if is_finished:
                break
                
            ai.update_result_of_last_guess( guess, self.get_last_goodbad() )
                
        print( "Game finished by computer in %d turn(s)" % nbr_turn )
        
        if 1:
            print( "# Best: %d turn(s) # " % nbr_turn, end="" )
            for guess in self.board:
                print(guess, end=", ")
            print("")
            
        return nbr_turn
        
            
# class MasterMindGame - end

def main():
    time_begin = time.time()
    
    if 1:
        # joue contre l'ordinateur
        game = MasterMindGame()
        forced_solution = []
        forced_solution = [3,2,0,2]
        game.human_guess_run_game(forced_solution)
        exit(1)
    
    #~ game.cpu_guess_run_game([2,4,6,4])
    
    if 0:
        game = MasterMindGame(2,3)
        game.cpu_guess_run_game([2,0])
    elif 0:
        game = MasterMindGame(2,3)
        game.cpu_guess_run_game([1,2]) # Best: 3 turn(s) # (0, 1), (2, 0), (1, 2), 
    elif 1:
        game = MasterMindGame(4,8)
        solution = [2,4,6,4] # Best: 5 turns # (0, 1, 2, 3), (5, 2, 4, 4), (4, 2, 7, 6), (6, 4, 4, 2), (2, 4, 6, 4), 
        #~ solution = [2,4,4,4] # Best: 4 turns # (0, 1, 2, 3), (5, 2, 4, 4), (4, 2, 6, 4), (2, 4, 4, 4)
        #~ solution = [4,4,4,4] # Best:  5 turns # (0, 1, 2, 3), (6, 5, 4, 4), (5, 5, 7, 4), (6, 5, 5, 5), (4, 4, 4, 4), 
        #~ solution = [6,5,4,3] # Best: 4 turn(s) # (0, 1, 2, 3), (5, 1, 4, 4), (0, 4, 6, 4), (6, 5, 4, 3), 
        #~ solution = [3,2,1,0] # Best: 2 turn(s) # (0, 1, 2, 3), (3, 2, 1, 0), 
        #~ solution = [3,2,0,1] # Best: 4 turn(s) # (0, 1, 2, 3), (3, 2, 1, 0), (2, 3, 1, 0), (3, 2, 0, 1), 
        solution = [3,2,0,2] # Best: 4 turn(s) # (0, 1, 2, 3), (3, 2, 0, 0), (3, 2, 4, 0), (3, 2, 0, 2),
        game.cpu_guess_run_game( solution )
    else:
        # fait un petit bench avec des combinaisons differentes
        nbr_choice = 4
        nbr_color = 5 # shouldn't be less than nbr_choice
        game = MasterMindGame(nbr_choice,nbr_color)
        solutions = []
        for i in range(nbr_color**nbr_choice):
            answer = []
            for j in range(nbr_choice):
                answer.append(i%nbr_color)
                i //= nbr_color
            solutions.append( tuple(answer) )
        nbr_total_turn = 0
        for s in solutions:
            nbr_total_turn += game.cpu_guess_run_game( s )
        print("# nbr_total_turn: for %d,%d: %s" % (nbr_choice, nbr_color, nbr_total_turn) )
        # nbr_total_turn: for 4,4: 981
        # nbr_total_turn: for 4,4: 917 # (doubling the second at first)
        # nbr_total_turn: for 4,5: 2592 403sec
        # nbr_total_turn: for 4,5: 2548  # (doubling the second at first)
        
        print("total duration for all combination: %.1f" % (time.time()-time_begin))
        
if __name__ == "__main__":
    main()