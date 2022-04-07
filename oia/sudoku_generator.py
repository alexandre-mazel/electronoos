
def initializeGrid(dim, empty_value = 0):
    """
    generate empty grid.
    Return the generated grid
    """
    grid = []
    for i in range(dim):
        grid.append([empty_value]*dim)
        
    # NB: alternate simplified writing : grid = [[empty_value]*dim]*dim
    return grid

def fillOneLine(grid,num_line):
    """
    fill one line of a grid.
    num_line in [0..8]
    """
    # todo: real code
    grid[num_line][num_line] = 3 # to see it filled

def eraseOneLine(grid,num_line):
    """
    clear one line
    num_line in [0..8]
    """
    dim = len(grid) # assume grid is square
    grid[num_line] = [0]*dim
    
def printGrid(grid):
    """
    obvious
    """
    for line in grid:
        print(line)
    print() # empty line
    
def existantGridIsFeasible(grid):
    """
    check if the filled line of the grid are valid
    Return True if it is
    """
    # todo: real code
    import random
    return random.random()>0.4
    
def generateFilledGrid(dim=9):
    """
    main function to generate a filled grid.
    Return the grid
    - dim: dimension of the grid
    """
      
    grid = initializeGrid(dim)
    printGrid(grid)

    num_line = 0
    while 1:
        print("DBG: filling line %d" % num_line)
        fillOneLine(grid,num_line)
        printGrid(grid)
        if not existantGridIsFeasible(grid):
            eraseOneLine(grid,num_line)
            print("DBG: erased line %d" % num_line)
            printGrid(grid)
        else:
            num_line += 1
            if num_line >= dim:
                break

            
    return grid
    
generateFilledGrid()
    
        
    