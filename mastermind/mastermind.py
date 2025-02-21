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

def goodbad( guess, solution ):
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
        
def allgoodbad( board, solution ):
    """
    compute all good bad for a board and a given solution
    """
    out = []
    for guess in board:
        out.append( goodbad(guess,solution) )
    return out
        
def compute_next_shot( board, listgoodbad, nbr_choice, nbr_color ):
    """
    Decide what is the best guess to play
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
                time.sleep(10)
                break
        else:
            prev_guess = new_guess
            
    return new_guess
        
def simulate_play( shot, solution, board, nbr_choice, nbr_color ):
    print("DBG: simulate_play: shot: %s, solution: %s, board: %s" % (str(shot), str(solution), str(board)) ) 
    good,bad = goodbad( shot, solution )
    if good == nbr_choice:
        return 1
    board.append( shot )
    listgoodbad = allgoodbad(board,solution)
    next_shot = compute_next_shot( board, listgoodbad, nbr_choice, nbr_color )
    return 1+simulate_play( next_shot, solution, board[:], nbr_choice, nbr_color )

class Game:
    def __init__( self, nbr_choice = 4, nbr_color = 8 ):
        """
        the color are 0..nbr_color-1
        """
        self.nbr_choice = nbr_choice
        self.nbr_color = nbr_color
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
            
        good,bad = goodbad(self.board[-1], self.solution)


        self.goodbad.append([good,bad])
        
        return good == self.nbr_choice
        
    def computer_guess( self ):
        """
        based only on previous guess and goodbad, the compute need to pick a choice
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
        
    def human_guess_run_game( self ):
        self.generate_random_solution()
        
        #~ self.render_solution()
        self.render_plate()
        
        nbr_turn = 0
        while 1:


            while 1:
                if nbr_turn == 0:
                    guess = "0123"
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
        self.render_plate()
        
        if human_solution == []:
            self.generate_random_solution()
        else:
            self.solution = human_solution
        
        nbr_turn = 0
        while 1:
            guess = self.computer_guess()
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
                
        print( "Game finished by computer in %d turn(s)" % nbr_turn )
        
            
# class Game - end

def main():
    #~ game = Game()
    #~ game.human_guess_run_game()
    #~ game.cpu_guess_run_game([2,4,6,4])
    
    game = Game(2,3)
    game.cpu_guess_run_game([2,0])
        
if __name__ == "__main__":
    main()