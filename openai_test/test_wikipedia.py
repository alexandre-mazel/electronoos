# -*- coding: cp1252 -*-

import os
import sys
strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import stringtools


import wikipedia # pip install wikipedia

wikipedia.set_lang("fr")

if 0:
    ret = wikipedia.summary("francois miterrand", sentences=1)
    print(stringtools.removeAccentString(ret))

ny = wikipedia.page("New York")
print("title: " + ny.title)
print("url: " + ny.url)
print(stringtools.removeAccentString(ny.content))
print("link: " + stringtools.removeAccentString(str(ny.links)))