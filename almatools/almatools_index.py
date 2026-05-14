# -*- coding: cp1252 -*-

def index(req):
    o = """<!DOCTYPE html><html>
    <head><meta charset='cp1252'/>
    <title>AlmaTools EI</title>
    <link rel="shortcut icon" href="/almatools/icon_at.png">
    <style>
    .divelem{
    font-size:20px;
    border:0px solid #333;
    }
    .imgelem{
    width:320px;
    border-radius: 8px;
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
    <img src='/almatools/logo_at.png' width=300>
    <br>
    <br>
    <br>
    <font size=+3>
    Prestation de conseil et d&eacute;veloppement
    </font>
    <br>
    <br>
    <br>
    <br>
    <br>
    <div style='display:flex;flex-direction: row;justify-content:space-evenly;border:0px solid #333;width:100%'>
        <div class='divelem'>
            <img class=imgelem src="/almatools/illus_robotics.png"><br>
            <div class=txtelem>Robotique et embarqu&eacute;</div>
        </div>
        <div  class='divelem'>
            <img class=imgelem src="/almatools/illus_agent.png"><br>
            <div class=txtelem>Agent virtuel, Jeu vid&eacute;o et<br>Intelligence Artificielle</div>
        </div>
        <div class='divelem'>
            <img class=imgelem src="/almatools/illus_web.png"><br>
            <div class=txtelem>Site web et serveur</div>
        </div>
    </div>
    <br>
    <br>
    <a href='/almatools/tarifs_almatools.pdf'>Tarifs</a>
    <!--<a href="javascript:viewPdf('/almatools/tarifs_almatools.pdf')">Tarifs</a>-->
    <div id='pdf_viewer'></div>
    <br>
    <br>
    <div style='vertical-align: middle;'>
    <img src='/almatools/adr_email_at.svg' height=15px>
    </div>
    </body>
    </html>
    """
    
    return o
    

def autotest():
    print(index(None))
    
if __name__ == "__main__":
    autotest()
