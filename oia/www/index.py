# l'indx pour oia

def outputJs():
    return """
    <script>
    function viewPdf(filename)
    {
        let e = document.getElementById('pdf_viewer');
        e.innerHTML = "<embed width=100% height=90% src='"+filename+"'#toolbar=0&navpanes=0&scrollbar=0&statusbar=0&messages=0&scrollbar=0' height=600 type='application/pdf'>"
    }
    </script>
    """

def generateCodeToViewPdf(strPdfFilename, strCaption):
    linkTemplate = """
    <a href="%s"
    style="color:cyan"
   onclick="window.open(this.href,'_blank',
                                   `toolbar=no,
                                    location=no,
                                    status=no,
                                    menubar=no,
                                    scrollbars=yes,
                                    resizable=yes,
                                    width=800,
                                    height=600,
                                    screenX=50,
                                    screenY=50,
                                    `);
     return false;">%s</a>
     """
     
    bNotAndroid = 1
     
    if bNotAndroid:
        linkTemplate = """
        <a href="javascript:viewPdf('%s')">%s</a>
        """
    else:
        # none of that works!
        linkTemplate = """
        <a href="https://docs.google.com/gview?embedded=true&url=%s">%s</a>
        """   
        linkTemplate = """
        <a href="https://docs.google.com/viewerng/viewer?url=%s">%s</a>
        """ 

    o = linkTemplate % (strPdfFilename, strCaption)
    
    if 1:
        pass
    return o
 
def index(req):
    # get_basic_auth_pw
    strOut = ""
    strOut += "<html>"
    strOut += "<header>"
    strOut += "<link rel='shortcut icon' type='image/png' href=../img/ico_engrenage2.png>"
    strOut += outputJs()
    strOut += "</header>"
    strOut += "<body>"
    strOut += "Bienvenue sur l'espace de l'option IA<br>"
    strOut += "<br>Rappels de syntaxes / Python Cheat Sheets: &nbsp; %s &nbsp;  <a href='OIA_Python_CheatSheets.pdf'>T&eacute;l&eacute;charger</a>" % generateCodeToViewPdf("OIA_Python_CheatSheets.pdf","Consulter en ligne")
    strOut += "<br>"
    strOut += "<br>Exercices pour les plus avancés: %s  &nbsp;  <a href='OIA_Cycle1_et_2_exercices_bonus.pdf'>T&eacute;l&eacute;charger</a>" % generateCodeToViewPdf("OIA_Cycle1_et_2_exercices_bonus.pdf","Consulter en ligne")
    strOut += "<br>"
    strOut += "<br><a href='src/'>Les sources de base</a>"
    strOut += "<br>"
    
    strOut += "<br>"
    #~ strOut += "<embed width=100% height=90% src='OIA_Python_CheatSheets.pdf#toolbar=0&navpanes=0&scrollbar=0&statusbar=0&messages=0&scrollbar=0' height=600 type='application/pdf'>"
    strOut += "<div id='pdf_viewer'></div>"
    strOut += "</body></html>"    
    return strOut

