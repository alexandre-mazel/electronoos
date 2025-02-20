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
        
    def human_guess_start_new_game( self ):
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
            
    def human_guess_compute_goodbad( self ):
        """
        Return True when human has guess all correct
        """
        
        if len(self.goodbad) == len(self.board):
            return
        good = 0
        bad = 0
        for idx,n in enumerate(self.board[-1]):
            if n == self.solution[idx]:
                good += 1
            else:
                try:
                    idxfound = self.solution.index(n)
                    if idxfound != -1 and self.solution[idxfound] != self.board[-1][idxfound]:
                        bad += 1
                except ValueError as err:
                    continue # not in list

        self.goodbad.append([good,bad])
        
        return good == self.nbr_choice
        
    def human_guess_run_game( self ):
        self.human_guess_start_new_game()
        
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
            
            is_finished = self.human_guess_compute_goodbad()
            
            if nbr_turn > 7:
                self.render_solution()
                
            self.render_plate()
            
            nbr_turn += 1
            
            if is_finished:
                break
                
        print( "Game finished in %d turn(s)" % nbr_turn )
            
# class Game - end

def main():
    game = Game()
    game.human_guess_run_game()
        
if __name__ == "__main__":
    main()