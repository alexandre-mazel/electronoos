

def index(req):
    o = """<!DOCTYPE html><html>
    <head><meta charset='cp1252'/>
    <title>AlmaTools EI</title>
    <link rel="shortcut icon" href="favicon.ico">
    <style>
    .divelem{
    font-size:20px;
    border:1px solid #333;
    }
    .imgelem{
    width:320px;
    }
    </style>
    </head>
    <body>
    <br>
    <center>
    <img src='logo_at.png' width=300>
    <br>
    <br>
    <br>
    <font size=+3>
    Prestation de conseil et développement
    </font>
    <br>
    <br>
    <br>
    <div style='display:flex;flex-direction: row;justify-content:space-around;border:1px solid #333;width:100%'>
        <div class='divelem'>
            <img class=imgelem src="logo_at.png"><br>
            Robotique et embarqué
        </div>
        <div  class='divelem'>
            <img class=imgelem src="embed"><br>
            Agent virtuel, Jeu vidéo et<br>Intelligence Artificielle
        </div>
        <div class='divelem'>
            <img class=imgelem src="embed"><br>
            Site web et serveur
        </div>
    </div>
    <br>
    <a href='tarif.htm'>tarifs</a>
    </body>
    </html>
    """
    
    return o
    

def autotest():
    print(index(None))
    
if __name__ == "__main__":
    autotest()