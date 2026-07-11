"""
A lancer en local sur REE ainsi le fichier des temperature est toujours a jour...
"""

import os
import sys

sys.path.append("..")

sys.path.append("../../../obo/spider/") # pour common
import temperature_office_analyse


def compute_stat():
    """
    compute last temperature measured, (min,max sur les x dernieres)
    """
    
    strFilename = "/home/na/save/office_temperature.txt"
    if os.name == "nt":
        # pour debugger, je prend un fichier local
        strFilename = "C:/Users/alexa/dev/git/electronoos/meteo/data/office_temperature.txt"
    datas = temperature_office_analyse.decode_file_sonde(strFilename)
    
    vals =  datas[("armoire","temp")]
    return vals[-1]
    
def format_record( r ):
    """
    generate a nice html code to output a record: y,mo,d,h,m,s,temperature
    """
    y,mo,d,h,m,s,temp = r
    return "%.1f°" % temp

def index():
    verbose = 1
    #~ verbose = 0
    r_last = compute_stat()
    if verbose:
        print( "r_last:" + r_last )
    
    s = format_record( r_last )
    print( "<html><body>" +  s + "</body></html>" )
    
    
if __name__ == "__main__":
    #~ stats = compute_stat()
    print( index() )