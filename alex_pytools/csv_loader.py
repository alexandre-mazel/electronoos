import io
import os
import sys

def openWithEncoding( filename, mode, encoding, errors = 'strict' ):
    if sys.version_info[0] < 3:
        import io
        return io.open( filename, mode, encoding=encoding, errors=errors )
    return open( filename, mode, encoding=encoding, errors=errors )
    
def looksLikeNumber(s):
    for c in s:
        if not c.isdigit() and c != '.':
            return False
    return True

def load_csv(filename, sepa = ';',bSkipFirstLine = 0, bVerbose=0 ):

    data = []
    enc = 'utf-8'    
    try:
        file = openWithEncoding(filename, "rt", encoding = enc)
    except:
        return data
        
    if bSkipFirstLine:
        line = file.readline() # skip first line
    
    while 1:
        line = file.readline()
        if len(line)<1:
            break
        if bVerbose: print("DBG: load_csv: line: '%s'" % line )
        if line[-1] == '\n': line = line[:-1] # erase last \n
        fields = line.split(sepa)
        for i in range(len(fields)):
            if bVerbose: print("DBG: load_csv: fields[%d]: '%s'" % (i,fields[i]) )
            if bVerbose: print("DBG: load_csv: field %d: '%s',type: %s" % (i, fields[i],type(fields[i]) ) )
            if len(fields[i])>1 and fields[i][0] == '"' and fields[i][-1] == '"':
                fields[i] = fields[i][1:-1]
            #~ elif not isinstance(fields[i], str):
            elif looksLikeNumber(fields[i]):
                # TODO: handle array
                if '.' in fields[i]:
                    fields[i] = float(fields[i])
                else:
                    fields[i] = int(fields[i])
        data.append(fields)
        
    # concatenate line with some " and unclosing " (eg a \n is in the text)
    nNumLine = 0
    while 1:
        print("DBG: nNumLine: %s" % nNumLine )
        if nNumLine >= len(data):
            break
        if isinstance(data[nNumLine][-1], str) and (data[nNumLine][-1].count('"') %2)  == 1:
            # looks like this string continued on next line:
            numField = 0
            numLineInc = 1
            while 1:
                bContainsEnd = isinstance(data[nNumLine+numLineInc][numField], str) and (data[nNumLine+numLineInc][numField].count('"') %2)  == 1
                data[nNumLine][-1] += "\n"+ data[nNumLine+numLineInc][numField]
                del data[nNumLine+numLineInc][numField]
                if len(data[nNumLine+numLineInc]) == 0:
                    del data[nNumLine+numLineInc]
                    continue
                    
                if bContainsEnd:
                    print("DBG: contains end, nNumLine: %d, numLineInc: %d, numField: %d" % (nNumLine,numLineInc,numField) )
                    if data[nNumLine][-1][0] == '"' and data[nNumLine][-1][-1] == '"':
                        data[nNumLine][-1] = data[nNumLine][-1][1:-1]
                    data[nNumLine].extend(data[nNumLine+numLineInc][numField:])
                    del data[nNumLine+numLineInc]
                    # il faudra alors continuer depuis cette ligne car la suite contient peut etre des champs cut
                    nNumLine -= 1
                    break
                numField += 1
                if numField >= len(data[nNumLine+numLineInc]):
                    numField = 0
                    numLineInc += 1
                if nNumLine+numLineInc >= len(data):
                    print("WRN: load_csv: unfinished opened double quote, something wrong...")
                    break
            nNumLine += numLineInc
        else:
            nNumLine += 1
            
        
    return data
    
def load_datas_from_xlsx_exploded_for_python27( filename, bVerbose ):
    dOut = dict()
    fi = io.open(filename + "__index.csv","rt", encoding="cp1252")
    while 1:
        tabname = fi.readline().replace("\n","")
        if len(tabname)<2:
            break
        print( "INF: load_datas_from_xlsx_exploded_for_python27: tabname: '%s'" % tabname )
        f = io.open(filename+"__"+tabname+".csv", "rt", encoding="cp1252")
        buf = f.read() # we could have decided to read line per line, but...
        data = buf.split("\n")
        for i in range(len(data)):
            data[i]=data[i].split(";")
            last = data[i][-1]
            if last == "" or last == "\n":
                del data[i][-1]
        if data[i] == []:
            del data[i]
        f.close()
        
        # conversion
        for i in range(len(data)):
            for j in range(len(data[i])):
                data[i][j] = data[i][j].encode("cp1252", 'replace')
        dOut[tabname]=data
    
    fi.close()
    print("DBG: load_datas_from_xlsx_exploded_for_python27: dOut: %s" % str(dOut) )
    return dOut
    
def load_datas_from_xlsx( filename, bVerbose = 0 ):
    """
    return a dict indexed by tab name then lines (without handling headers)
    """
    # ce qui fonctionne pas, c'est qu'en fait il faut chercher des ; avant les "\n"
    
    #~ import xlrd # pip install xlrd 
    #~ import openpyxl # pip install openpyxl 
    try: import pandas as pd
    except: pass # on python2.7, it will be ok
    try: import numpy as np
    except: pass
    if os.name == "nt":
        df = pd.read_excel( filename, sheet_name=None, header=None)
    else:
        #~ import openpyxl # pip install openpyxl # to shout if missing
        #~ df = pd.read_excel( filename, sheet_name=None, header=None, engine='openpyxl' ) # bug in 1.2.0, not in 1.1.5 # pip install pandas==1.1.5 (not existing in python2)
        # rien ne fonctionne en python2.7
        #~ df = pd.read_excel( filename, sheet_name=None, header=None )
        if sys.version_info[0] < 3:
            return load_datas_from_xlsx_exploded_for_python27(filename, bVerbose)

        df = pd.read_excel( filename, sheet_name=None, header=None )
    
    if bVerbose: print(len(df))
    if bVerbose: print(df)
    if bVerbose: print(df.keys())
    dOut = {}
    for sheet_name,sheet_data in df.items():
        if bVerbose: print("\nDBG: load_datas_from_xlsx: sheet_name: '%s', line(s): %d" % (sheet_name,len(sheet_data) ) )
        listLine = []
        sheet_data = sheet_data.fillna(value='nan')
        for data in sheet_data.itertuples(index=False):
            if bVerbose: print(str(data))
            #~ listLine.append(data[:])
            oneLine = []
            for col in data:
                if bVerbose: print("col: %s" % col)
                if col == 'nan':
                    break
                oneLine.append(col)
            listLine.append(oneLine)

        dOut[sheet_name] = listLine
    if bVerbose:
        print( "\nDBG: load_datas_from_xlsx: output: %s" % dOut )
        print( "\nDBG: load_datas_from_xlsx: output:" )
        for sheet_name,sheet_data in dOut.items():
            print("\nDBG: load_datas_from_xlsx: sheet_name: '%s', line(s): %d" % (sheet_name,len(sheet_data) ) )
            for line in sheet_data:
                print("")
                for col in line:
                    print("   '%s'" % col)
                    
    if 1:
        # generate one cvs per tab, so you can read them back with python2.7
        fIndex = io.open(filename+"__index.csv", "wt", encoding="cp1252")
        for k,content in dOut.items():
            fn = filename+"__"+k+".csv"
            print("INF: writing to independant csv: %s" % fn )
            f = io.open(fn,"wt", encoding="cp1252")
            for line in content:
                for field in line:
                    #~ print("field: %s" % field )
                    f.write( str(field) + ";")
                f.write("\n")
            f.close()
            fIndex.write(k+"\n")
        fIndex.close()
    
    return dOut
    
#~ load_datas_from_xlsx( r"C:\Users\alexa\dev\git\obo\www\chatbot\OBO_Recruitement_dialog.xlsx")
    
def save_csv(filename, data):
    file = open(filename, "wt")
    for fields in data:
        s = ""
        for i in range(len(fields)):
            if i != 0: s += ";"
            if type(fields[i]) == type('s'):
                s += '"%s"' % fields[i]
            else:
                s+= '%s' % fields[i]
        file.write(s+"\n")
    file.close()
    
    
def autotest():
    datas = [ [12,"toto", 3.5], [13,"tutu", 0.0, ""] ]
    save_csv("/tmp/tmp.dat", datas)
    datas2 = load_csv("/tmp/tmp.dat")
    assert(datas==datas2)

    datas = [ [12,"toto\ntutu\ntiti", 3.5], [13,"tutu", 0.0, ""] ] # ok
    datas = [ [12,"toto\ntutu\ntiti", 3.5], [13,"tutu", 0.0, ""], ['tutu\ntata', 'toto\ntonton', 3], [4] ] # ok now
    save_csv("/tmp/tmp.dat", datas)
    datas2 = load_csv("/tmp/tmp.dat",bVerbose=1)
    print("DBG: datas : %s" % str(datas) )
    print("DBG: datas2: %s" % str(datas2) )
    assert(datas==datas2)
    
if __name__ == "__main__":
    autotest()
            