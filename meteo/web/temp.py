# -*- coding: utf-8 -*-

"""
A lancer en local sur REE ainsi le fichier des temperature est toujours a jour...
Sur REE c'est un apache2 qui tourne.
"""

import os
import sys

sys.path.append("..")
sys.path.append("/home/na/dev/git/electronoos/meteo/")

import temperature_office_analyse

import misctools

def record_to_min( r ):
    """
    convertit un y,mo,d,h,m,temp en sec since 1970 (roughly)
    """
    y,mo,d,h,m,temp = r
    sec = misctools.convertYmdHmsToEpoch( y,mo,d,h,m )
    return sec//60
    
def getMinMax( v, duration_minute ):
    """
    return le record min temp et max temp dans les duration_min derniere minute
    """
    idx_min = -1
    idx_max = -1
    avg = v[idx_min][-1]
    cpt_avg = 1
    start_minute = record_to_min(v[idx_min])
    print( "DBG: getMinMax: start_minute: %s => s%s" % (v[idx_min],start_minute))
    idx = -2
    while 1:
        r = v[idx]
        temp = r[-1]
        record_minute = record_to_min( r )
        #~ print( "DBG: getMinMax: record_minute: %s => %s" % (r,record_minute) )
        if start_minute - record_minute > duration_minute:
            print( "DBG: getMinMax: stopping at record: '%s'" % str(r) )
            break
        if v[idx_min][-1] > temp and abs(temp) > 0.01 : # si 0.0 c'est un bug
            idx_min = idx
        if v[idx_max][-1] < temp:
            idx_max = idx
        avg += temp
        cpt_avg += 1
        idx -= 1
        
    avg /= cpt_avg
    return v[idx_min], v[idx_max], avg
        


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
    
    if os.name == "nt":
        generate_temperature_graph_plotly( vals[-10000:], "generated_gfx.html" )
    
    
    r_last = vals[-1]
    
    rmin_h,rmax_h, avg_h = getMinMax( vals, 60 )
    rmin_d,rmax_d, avg_d = getMinMax( vals, 60*24 )
    rmin_7d,rmax_7d, avg_7d = getMinMax( vals, 60*24*7 )
    rmin_3m,rmax_3m, avg_3m = getMinMax( vals, 60*24*7*12 )
    return r_last, rmin_h,rmax_h,rmin_d,rmax_d,rmin_7d,rmax_7d,rmin_3m,rmax_3m, avg_h, avg_d, avg_7d, avg_3m
    
    
def generate_temperature_graph_plotly(records, output_filename="temperature_graph.html"):
    """
    records: liste de tuples
        [(y, mo, d, h, m, temp), ...]

    Génère un fichier HTML interactif.
    
    Attention: ca rame si trop de valeur et pas lisible.
    """
    print( "INF: generate_temperature_graph_plotly: generating from %d records" % len( records ) )
    
    import plotly # pip install plotly # sudo python2 -m pip install plotly
    import plotly.graph_objects as go
    from plotly.colors import sample_colorscale
    import datetime

    # Trie par date
    records = sorted(records)

    dates = []
    temps = []

    for y, mo, d, h, mi, t in records:
        dates.append(datetime.datetime(y, mo, d, h, mi))
        temps.append(float(t))

    tmin = min(temps)
    tmax = max(temps)

    # évite division par zéro
    if tmax == tmin:
        norm = [0.5] * len(temps)
    else:
        norm = [(t - tmin) / float(tmax - tmin) for t in temps]

    # Bleu -> Rouge
    colors = sample_colorscale(
        "RdBu_r",    # bleu=froid, rouge=chaud
        norm
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=temps,
            mode="lines+markers",
            line=dict(
                color="rgba(120,120,120,0.4)",
                width=2
            ),
            marker=dict(
                size=8,
                color=temps,
                colorscale="RdBu_r",
                cmin=tmin,
                cmax=tmax,
                line=dict(width=1, color="black")
            ),
            hovertemplate=
                "<b>%{y:.1f} °C</b><br>"
                "%{x|%d/%m/%Y %H:%M}"
                "<extra></extra>"
        )
    )

    fig.update_layout(
        title="Historique des températures",
        xaxis_title="Date",
        yaxis_title="Température (°C)",
        template="plotly_white",
        hovermode="closest",
        height=500,
    )

    fig.write_html(
        output_filename,
        include_plotlyjs="cdn"
    )

    return output_filename

def format_record( r, title, style = 0 ):
    """
    generate a nice html code to output a record: y,mo,d,h,m,temperature
    
    style: 0: default, 1: cold, 2: hot
    """
    if isinstance(r,list):
        y,mo,d,h,m,temp = r
        dt = "%2d/%02d/%d - %d:%02d" % (d,mo,y,h,m)
    else:
        temp = r
        dt = "&nbsp;"
    
    style_temp = "temp-value"
    if style == 1:
        style_temp = "temp-value-cold"
    elif style == 2:
        style_temp = "temp-value-hot"
    elif style == 3:
        style_temp = "temp-value-avg"
        
    return """
        <div class="temp-card">
            <div class="temp-title">%s</div>
            <div class="%s">%.1f<span class="temp-unit">°</span></div>
            <div class="temp-date">%s</div>
        </div>
        """ % (title,style_temp,temp,dt)
    
def getStyle():
    return """
<style>
.temp-container {
    display: flex;
    gap: 20px;
    justify-content: center;
    align-items: flex-start;
    flex-wrap: wrap;
}
.temp-card {
    width: 220px;
    padding: 18px 20px;
    border-radius: 18px;
    background: linear-gradient(145deg, #2f80ed, #56ccf2);
    color: white;
    font-family: "Segoe UI", Arial, sans-serif;
    text-align: center;
    box-shadow: 0 8px 20px rgba(0,0,0,.25);
}

.temp-title {
    margin-top: 1px;
    margin-bottom: 8px;
    font-size: 15px;
    font-weight: 600;
    opacity: .85;
    letter-spacing: .5px;
    color: darkblue;
}

.temp-value {
    font-size: 56px;
    font-weight: 700;
    line-height: 1;
    letter-spacing: -2px;
}

.temp-value-hot {
    font-size: 56px;
    font-weight: 700;
    line-height: 1;
    letter-spacing: -2px;
    color: red;
}

.temp-value-cold {
    font-size: 56px;
    font-weight: 700;
    line-height: 1;
    letter-spacing: -2px;
    color: blue;
}

.temp-value-avg {
    font-size: 56px;
    font-weight: 700;
    line-height: 1;
    letter-spacing: -2px;
    color: orange;
}

.temp-unit {
    font-size: 28px;
    vertical-align: top;
}

.temp-date {
    margin-top: 10px;
    font-size: 15px;
    font-weight: 700;
    opacity: .85;
    letter-spacing: .5px;
}
</style>
"""

def index():
    data = misctools.cacheOnDisk.getData( "web_temp_last_data", 60*3 )
    if data != None and 1:
        return data
        
    verbose = 1
    #~ verbose = 0
    if 1:
        r_last, r_min_h,r_max_h,r_min_d,r_max_d,r_min_7d,r_max_7d,r_min_3m,r_max_3m, avg_h, avg_d, avg_7d, avg_3m = compute_stat()
    else:
        r_last = [2026, 7, 11, 11, 15, 28.6]
        r_min_h = [2026, 7, 11, 11, 15, 22.6]
        r_max_h = [2026, 7, 11, 11, 15, 28.6]
        r_min_d = [2026, 7, 11, 11, 15, 14.6]
        r_max_d = [2026, 7, 11, 11, 15, 28.6]
        r_min_7d = [2026, 7, 11, 11, 15, 12.6]
        r_max_7d = [2026, 7, 11, 11, 15, 38.6]
        r_min_3m = [2026, 2, 11, 11, 15, 2.6]
        r_max_3m = [2026, 1, 11, 11, 15, 38.6]
    if verbose:
        print("<!--")
        print( "r_last: " + str(r_last) )
        print( "r_min_h: " + str(r_min_h) )
        print( "r_max_h: " + str(r_max_h) )
        print( "r_min_d: " + str(r_min_d) )
        print( "r_max_d: " + str(r_max_d) )
        print( "r_min_7d: " + str(r_min_7d) )
        print( "r_max_7d: " + str(r_max_7d) )
        print("-->")
    
    ss = []
    ss.append( format_record( r_last, "derni&egrave;re mesure" ) )
    
    ss.append( format_record( r_min_h, "minimum derni&egrave;re heure", 1 ) )
    ss.append( format_record( avg_h, "moyenne derni&egrave;re heure", 3 ) )
    ss.append( format_record( r_max_h, "maximum derni&egrave;re heure", 2 ) )
    
    ss.append( format_record( r_min_d, "minimum derni&egrave;r jour", 1 ) )
    ss.append( format_record( avg_d, "moyenne derni&egrave;r jour", 3 ) )
    ss.append( format_record( r_max_d, "maximum derni&egrave;r jour", 2 ) )

    ss.append( format_record( r_min_7d, "minimum derni&egrave;re semaine", 1 ) )
    ss.append( format_record( avg_7d, "moyenne derni&egrave;re semaine", 3 ) )
    ss.append( format_record( r_max_7d, "maximum derni&egrave;re semaine", 2 ) )

    ss.append( format_record( r_min_3m, "minimum 3 derniers mois", 1 ) )
    ss.append( format_record( avg_3m, "moyenne 3 derniers mois", 3 ) )
    ss.append( format_record( r_max_3m, "maximum 3 derniers mois", 2 ) )
    
    out =  "<html><head><meta charset='UTF-8'><title>Temperature chez nous</title>" + getStyle() + "</head><body>"
    out += "<div class='temp-container'>"
    for i,s in enumerate(ss):
        out += s
        if i == 0 or ( i-1 ) % 3 == 2:
            out += "</div><br><div class='temp-container'>"
    out += "</body></html>"
    if verbose:
        print("<!--")
        print( "out: " + str(out) )
        print("-->")
        
    misctools.cacheOnDisk.saveData( "web_temp_last_data", out )
    return out
    
    
if __name__ == "__main__":
    import time
    #~ stats = compute_stat()
    t_begin = time.time()
    s=index()
    f = open("debug.html","wt")
    f.write(s)
    f.close()
    print("duration: %.2fs" % (time.time()-t_begin) )