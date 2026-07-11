# -*- coding: utf-8 -*-

"""
A lancer en local sur REE ainsi le fichier des temperature est toujours a jour...
"""

import os
import sys

sys.path.append("..")

sys.path.append("../../../obo/spider/") # pour common
#~ import temperature_office_analyse


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
    generate a nice html code to output a record: y,mo,d,h,m,temperature
    """
    y,mo,d,h,m,temp = r
    dt = f"{d:02d}/{mo:02d}/{y} - {h:02d}:{m:02d}"
    
    return f"""
        <div class="temp-card">
            <div class="temp-value">{temp:.1f}<span class="temp-unit">°C</span></div>
            <div class="temp-date">{dt}</div>
        </div>
        """
    
def getStyle():
    return """
<style>
.temp-card {
    width: 220px;
    padding: 18px 20px;
    border-radius: 18px;
    background: linear-gradient(145deg, #2f80ed, #56ccf2);
    color: white;
    font-family: "Segoe UI", Arial, sans-serif;
    text-align: center;
    box-shadow: 0 8px 20px rgba(0,0,0,.25);
}}

.temp-value {
    font-size: 56px;
    font-weight: 700;
    line-height: 1;
    letter-spacing: -2px;
}

.temp-unit {
    font-size: 28px;
    vertical-align: top;
}

.temp-date {
    margin-top: 14px;
    font-size: 14px;
    opacity: .85;
    letter-spacing: .5px;
}
</style>
"""

def index():
    verbose = 1
    #~ verbose = 0
    #~ r_last = compute_stat()
    r_last = [2026, 7, 11, 11, 15, 28.6]
    if verbose:
        print( "r_last: " + str(r_last) )
    
    s = format_record( r_last )
    print( "<html><head>" + getStyle() + "</head><body>" +  s + "</body></html>" )
    
    
if __name__ == "__main__":
    #~ stats = compute_stat()
    index()