from microbit import *
import neopixel

nbr_leds = 16*16;
leds = neopixel.NeoPixel(pin1, nbr_leds)

def setpix( x, y, color ):
    coef = 4
    color = (color[0]//coef,color[1]//coef,color[2]//coef)  # dimming
    if y % 2 == 1:
        leds[x+y*16] = color
    else:
        leds[(15-x)+y*16] = color
        
"""
The font data from ASCII codes 32 to 126. Index padded by 32.
Format (bit 0 = lowest bit):
  bits 0 to 2:  width of character (max = 5)
  bits 3 to 7:  column 0 (bit 3 = row 0, bit 4 = row 1, etc.)
  bits 8 to 27 (if any): column 1 to 4
  on 5 lines maximum
"""
fontData = [

    "1", "185", "24603", "92102485", "19655237", "216566685", "170063685", "25",
    "4466", "3722", "85189717", "34858021", "6274", "34636837", "129", "25795",
    "119155", "7954", "186771", "87435", "2353764", "79291", "79219", "32011",
    "87379", "120211", "81", "6786", "145310757", "86592085", "34687629", "21771",
    "158839157", "248307", "87547", "143731", "119291", "144891", "9723", "110963",
    "255227", "147339", "127299", "222459", "135419", "260604669", "8159996", "119155",
    "17915", "252275", "214523", "79251", "16139", "258299", "63547", "65067069",
    "222427", "64571", "161227", "4602", "197659", "8074", "49459", "135299",
    "522", "234563", "70907", "169027", "259139", "170595", "48675", "236195",
    "197883", "209", "7554", "166139", "4218", "202573029", "197859", "70723",
    "35571", "248355", "34019", "6818", "171555", "233571", "102499", "104927333",
    "166051", "121011", "5842", "147235", "249", "40843", "35684901"
    ]
    

def render_char(x,y,c,color=(255,255,255)):
    """
    render the char c.
    Return his number of column
    """
    print(len(fontData))
    idx = ord(c) - 32
    dat = int(fontData[idx])
    print("DBG: render_char: idx: %s, dat: %s" % (idx,dat) )
    w = dat&0x07
    print("DBG: render_char: w: %s" % w )
    dat >>=3
    num_col = 0
    while dat != 0:
        # 5 bit per column
        col = dat & 0x1F
        num_line = 0
        while col:
            if col & 0x1:
                setpix(x+num_col,y+num_line,color)
            col >>= 1
            num_line += 1
        dat >>= 5
        num_col += 1
    return w
    
def render_text(x,y,s,color=(255,255,255)):
    offset = 0
    for idx,c in enumerate(s):
        offset += render_char(offset+x,0+y,c) + 1
        
        
def draw_tetris():
    lblue = (80,80,255)
    yellow = (255,255,40)
    red = (255,0,0)
    purple = (255,0,255)
    dpurple = (4,0,4)
    
    setpix(8,15,lblue)
    setpix(8,14,lblue)
    setpix(8,13,lblue)
    setpix(8,12,lblue)
    
    setpix(9,15,yellow)
    setpix(10,15,yellow)
    setpix(9,14,yellow)
    setpix(10,14,yellow)
    
    setpix(11,15,red)
    setpix(11,14,red)
    setpix(12,14,red)
    setpix(12,13,red)

            
    setpix(9,5,dpurple)
    setpix(10,5,dpurple)
    setpix(11,5,dpurple)
    setpix(10,4,dpurple)
    
    setpix(9,6,purple)
    setpix(10,6,purple)
    setpix(11,6,purple)
    setpix(10,5,purple)


    
    
    #render_text(0,0,"Tetris")
    render_text(0,0,"63")
    
    
    
leds.fill((0,0,3)) # Toutes en bleue
leds[0] = (63, 63, 0) # la premiere en fuchia
leds.show()

sleep(700)

leds.fill((0,0,0)) # raz
setpix(6,0,(255,0,255))
setpix(6,1,(255,0,255))
leds.show()
sleep(700)

leds.fill((0,0,0)) # raz
draw_tetris()
leds.show()

display.show(Image.FABULOUS)
