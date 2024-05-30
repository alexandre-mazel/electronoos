import os
import sys

if sys.version_info[0] >= 3:
    current_dir_name = os.path.dirname(__file__)
    if current_dir_name == "": current_dir_name = './'
    sys.path.append(current_dir_name + "/../../../obo/vitrine/")
else:
    sys.path.append("/var/www/html/vitrine")
    sys.path.append("/var/www/html/spider")

    
import common_vitrine

def index(req):

    dArg = common_vitrine.analyseArgs(req.args, "")
    print("DBG: dArg: %s" % str(dArg))
    
    s = """<html>
    <body><h>Bienvenue dans la page de test du TP special de l'option IA de Juin 2024</h><br><br>\n"""
    
    bLogInfo = False
    try:
        if dArg["l"] != "" and dArg["p"] != "":
            bLogInfo = True
    except KeyError as err:
        pass
        
    if not bLogInfo:
        s += "Enter your credentials:<br>"
        s += "<br>"
        s += """<form action="tp_connect.py">
  <label for="fname">Login:</label><br>
  <input type="text" id="l" name="l" value=""><br>
  <label for="lname">Password:</label><br>
  <input type="text" id="p" name="p" value=""><br><br>
  <input type="submit" value="Submit">
</form>"""

    else:
        login = dArg["l"]
        password = dArg["p"]
        s += "Checking credentials '%s' with '%s'\n" % (login,password)
        if password == 'sous-marin':
            s += "<br>Connection Success!<br>"
            s += "<br> L'information capitale est celle ci: 'Bravo a toi, tu recois un bonbon en cadeau!'<br>"
        else:
            s += "<br>Connection Failed!<br>"

    s += "</body></html>"""
    
    return s
    
    
if __name__ == "__main__":
    # pour tester en ligne de commande: 

    import sys
    
    login = ""
    password = ""
    
    if 1:
        login = "test"
        password = "caca"
    
    if len(sys.argv) > 1:
        login = sys.argv[1]
    if len(sys.argv) > 2:
        password = sys.argv[2]

    req = type('', (), {})()
    req.args = "l=%s" % (login)
    req.args += "&p=%s" % (password)
    print(index(req))