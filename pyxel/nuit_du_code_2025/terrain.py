"""
format: one string per line of terrain

    [0..5[   : herbe
    [5..A[   : murs 
    [A..Z[   : A: fire
    [a..z[    : porte vers un autre monde (a: monde0, z: monde25)
    [!]        : objet speciaux (!: le slip magique, objet de quete, fin du jeu)

"""

kTypeGrass = 0
kTypeWall = 5
kTypeFire = 10
kTypeDoor = 36
kTypeSlip = 100

terrains = [

# terrain 0
[
    "55555555",
    "500000c5",
    "50000005",
    "50000005",
    "50000005",
    "50000005",
    "500000b5",
    "55555555",
],

# terrain 1
[
    "555555555555555555555555",
    "5a0000005000005000000005",
    "500000000000000000000005",
    "500005000005000050000005",
    "500005000005000050000005",
    "500005000005000050000005",
    "500000000005000050000005",
    "500005000005000050000005",
    "500005000005000050000005",
    "555555555555000055555555",
    "500000000000000000000005",
    "500000000000000000000005",
    "500000000000000555555555",
    "500000000000000500000005",
    "5000000000000005000c0005",
    "500000000000000000000005",
    "555555555555555555555555",
],


# terrain2
[
    "555555555555555555555555",
    "500a00000000000000000005",
    "500000000000000000000005",
    "50000500AAAAAAA000000005",
    "500005000000000000000005",
    "500005000000000000000005",
    "500005000000000000000005",
    "500005000000000000000005",
    "500005000000000000000005",
    "500005000000000000000005",
    "500005000000000000000005",
    "500005000000000000000005",
    "500005000000000000000005",
    "500005000000000555555555",
    "50000555555555550b000005",
    "5000000000000000000000d5",
    "555555555555555555555555",
],

# terrain3
[
    "555555555555555555555555",
    "500a00000000000000000005",
    "500000000000000000000005",
    "500005000000000000000005",
    "500005000000000000000005",
    "555555555555555555555055",
    "500005000000000000000005",
    "500000000000000000000005",
    "555055555555555555555055",
    "500005000000000000000005",
    "500005000000000000000005",
    "500005000000000000000005",
    "500005000000000000000005",
    "500005000000000555555555",
    "50000555555555550b000005",
    "5c00000000000000000000!5", # le c fait boucler sur lui meme: jeu infini !
    "555555555555555555555555",
]

] # terrains


def get_terrain( num_terrain ):
    """
    Return the data of one terrain
    """
    assert( num_terrain >= 0 )
    assert( num_terrain < len(terrains) )
    ter =  terrains[num_terrain]
    # convertit to int (discutable, mais au moins ca optimise le rendu)
    # et pas besoin d'enchainer avec un deepcopy
    out = []
    for j in range(len(ter)):
        out.append([])
        for i in range(len(ter[j])):
            
            case = ter[j][i]
            
            if case == '!':
                out[-1].append( kTypeSlip )
                continue
            
            val = ord(case)-ord('0')
            if val <= 9:
                # 0-9
                out[-1].append( val )
                continue
                
            val = ord(case)-ord('A')
            if val < 26:
                # A-Z
                out[-1].append( kTypeFire+val )
                continue
                
            val = ord(case)-ord('a')
            if val < 26:
                # a-z
                print("DBG: get_terrain: val: %s" % val )
                out[-1].append( kTypeDoor+val )
                #~ out[-1].append( kTypeDoor+3 ) # force sur tout le temps le meme terrain pour en tester un specifiquement
                continue
                
                
    return out
    