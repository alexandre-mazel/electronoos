

def index(req):
    o = """<!DOCTYPE html><html>
    <head><meta charset='cp1252'/>
    <title>AlmaTools EI</title>
    <link rel="shortcut icon" href="icon_at.png">
    <style>
    .divelem{
    font-size:20px;
    border:0px solid #333;
    }
    .imgelem{
    width:320px;
    }
    .txtelem{
    padding:10px;
    }
    </style>
    
    <script>
    function viewPdf(filename)
    {
        let e = document.getElementById('pdf_viewer');
        e.innerHTML = "<embed width=100% height=90% src='"+filename+"'#toolbar=0&navpanes=0&scrollbar=0&statusbar=0&messages=0&scrollbar=0' type='application/pdf'>"
    }
    </script>
    
    </head>
    <body style="font-family: sans-serif">
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
    <br>
    <br>
    <div style='display:flex;flex-direction: row;justify-content:space-evenly;border:0px solid #333;width:100%'>
        <div class='divelem'>
            <img class=imgelem src="illus_robotics.png"><br>
            <div class=txtelem>Robotique et embarqué</div>
        </div>
        <div  class='divelem'>
            <img class=imgelem src="illus_agent.png"><br>
            <div class=txtelem>Agent virtuel, Jeu vidéo et<br>Intelligence Artificielle</div>
        </div>
        <div class='divelem'>
            <img class=imgelem src="illus_web.png"><br>
            <div class=txtelem>Site web et serveur</div>
        </div>
    </div>
    <br>
    <br>
    <a href='tarifs_almatools.pdf'>Tarifs</a>
    <!--<a href="javascript:viewPdf('tarifs_almatools.pdf')">Tarifs</a>-->
    <div id='pdf_viewer'></div>
    <br>
    <br>
    <div style='vertical-align: middle;'>
    <img src='adr_email_at.svg' height=15px>
    </div>
    </body>
    </html>
    """
    
    return o
    

def autotest():
    print(index(None))
    
if __name__ == "__main__":
    autotest()
