# -*- coding: cp1252 -*-

accented ="ÀàÂâçÉÊÈËéêèë€ÎîÔôÛûù&<>\"'" + chr(0x92)+chr(0x91)+chr(0x94)+chr(0x93) + "\n ?" # 0x92 is the ' vers le haut droite; 0x91 c'est le symetrique, puis les memes en double quote
accented += chr(0xa0) # espace insecable
accented += chr(0xab) # opening braces
accented += chr(0xbb) # closing braces

htmlled = [
        "&Agrave;",
        "&agrave;",
        "&Acirc;",
        "&acirc;",
        "&ccedil;",
        
        "&Eacute;",
        "&Ecirc;",
        "&Egrave;",
        "&Euml;",
        
        "&eacute;",
        "&ecirc;",
        "&egrave;",
        "&euml;",
        
        
        "&euro;",

        "&Icirc;",
        "&icirc;",
        
        "&Ocirc;",
        "&ocirc;",

        "&Ucirc;",
        "&ucirc;",
        "&ugrave;",

        
        # ne pas mettre d'accent a partir de la. cf accented_first_no_accent (beurk)
        "&amp;",
        "&lt;",
        "&gt;",
        "&quot;",
        "&#39;",
        
        "&#39;",
        "&#39;",
        
        "&quot;",
        "&quot;",

        "%0D%0A",                        
        "%20",
        "%3F",
        "%20",
        "&quot;",
        "&quot;"
    ]
                
accented_first_no_accent = htmlled.index("&amp;")
                
def print_hexa_code():
    print("accented = [")
    for i in range(len(accented)):
        c = accented[i]
        print("    0x%x, # %s" % (ord(c),htmlled[i]))
        
    
if __name__ == "__main__":
    print_hexa_code()