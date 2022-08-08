import io
import os
import sys

def openWithEncoding( filename, mode, encoding, errors = 'strict' ):
    if sys.version_info[0] < 3:
        import io
        return io.open( filename, mode, encoding=encoding, errors=errors )
    return open( filename, mode, encoding=encoding, errors=errors )
    
def looksLikeNumber(s):
    if s == "":
        return False
    for c in s:
        if not c.isdigit() and c != '.':
            return False
    return True

def load_csv_multiline(filename, sepa = ';', bSkipFirstLine = 0, encoding =  'utf-8', bVerbose=0 ):
    """
    load a csv where some field can contain \n.
    so a real end of record is marked as ";\n"
    """
    data = []
    try:
        file = openWithEncoding(filename, "rt", encoding = encoding)
    except:
        return data
        
    if bSkipFirstLine:
        line = file.readline() # skip first line
    buf = file.read()
    file.close()
    idx = 0
    idx_start = 0
    fields = []
    while 1:
        bMustQuit = idx >= len(buf)
        if bVerbose: print("DBG: load_csv_multiline: idx_start: %d, idx: %d,  is_sepa: %d, bMustQuit: %d, char: '%s'" % (idx_start,idx,bMustQuit or buf[idx] == sepa,bMustQuit, bMustQuit or buf[idx]) )
        if bMustQuit or buf[idx] == sepa:
            s = buf[idx_start:idx]
            if len(s)>1 and s[0] == '"' and s[-1] == '"':
                s = s[1:-1]
            elif looksLikeNumber(s):
                # TODO: handle array
                if '.' in s:
                    s = float(s)
                else:
                    s = int(s)
            fields.append(s)
            idx_start = idx+1
            if bMustQuit or buf[idx+1] == "\n":
                idx += 1
                idx_start += 1
                if not bMustQuit or (len(fields)>0 and fields != ['']):
                    data.append(fields)
                fields = []
        if bMustQuit:
            break
        idx += 1
    return data
    
def load_csv(filename, sepa = ';', bSkipFirstLine = 0, encoding =  'utf-8', bVerbose=0 ):

    data = []
    try:
        file = openWithEncoding(filename, "rt", encoding = encoding)
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
        if fields[-1] == "":
            del fields[-1]
        for i in range(len(fields)):
            if sys.version_info[0]<3 and isinstance(fields[i],unicode):
                fields[i] = fields[i].encode(encoding, 'replace')
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
    if bVerbose: print("DBG: load_csv: before \"\" matching, data: " + str(data))
    nNumLine = 0
    while 1:
        if bVerbose: print("DBG: nNumLine: %s" % nNumLine )
        if nNumLine >= len(data):
            break
        if isinstance(data[nNumLine][-1], str) and (data[nNumLine][-1].count('"') %2)  == 1:
            # looks like this string continued on next line:
            numField = 0
            numLineInc = 1
            while 1:
                if bVerbose: print("DBG: loop start, nNumLine: %d, numLineInc: %d, numField: %d, data: %s" % (nNumLine,numLineInc,numField,data) )
                if nNumLine+numLineInc >= len (data):
                    break
                if numField >= len(data[nNumLine+numLineInc]):
                    numLineInc += 1
                    continue
                bContainsEnd = isinstance(data[nNumLine+numLineInc][numField], str) and (data[nNumLine+numLineInc][numField].count('"') %2)  == 1
                data[nNumLine][-1] += "\n"+ data[nNumLine+numLineInc][numField]
                if data[nNumLine][-1][0] == '"' and data[nNumLine][-1][-1] == '"':
                    data[nNumLine][-1] = data[nNumLine][-1][1:-1]
                del data[nNumLine+numLineInc][numField]
                if len(data[nNumLine+numLineInc]) == 0:
                    del data[nNumLine+numLineInc]
                    if bVerbose: print("del")
                    continue
                    
                if bContainsEnd:
                    #~ print("DBG: contains end, nNumLine: %d, numLineInc: %d, numField: %d" % (nNumLine,numLineInc,numField) )
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
    
def load_datas_from_xlsx_exploded_for_python27( filename, encoding = 'utf-8', bVerbose = 0 ):
    dOut = dict()
    fi = io.open(filename + "__index.csv","rt", encoding=encoding)
    while 1:
        tabname = fi.readline().replace("\n","")
        if len(tabname)<2:
            break
        print( "INF: load_datas_from_xlsx_exploded_for_python27: tabname: '%s'" % tabname )
        fntab = filename+"__"+tabname+".csv"
        if 1:
            #~ data = load_csv( fntab, encoding=encoding )
            data = load_csv_multiline( fntab, encoding=encoding )
        else:
            f = io.open( fntab, "rt", encoding=encoding)
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
                if sys.version_info[0]<3 and isinstance(data[i][j],unicode):
                    data[i][j] = data[i][j].encode(encoding, 'replace')
        dOut[tabname]=data
    
    fi.close()
    print("DBG: load_datas_from_xlsx_exploded_for_python27: dOut: %s" % str(dOut) )
    return dOut
    
def load_datas_from_xlsx( filename, encoding = 'utf-8', bVerbose = 0 ):
    """
    return a dict indexed by tab name then lines (without handling headers)
    """
    # ce qui fonctionne pas, c'est qu'en fait il faut chercher des ; avant les "\n"
    
    #~ import xlrd # pip install xlrd 
    #~ import openpyxl # pip install openpyxl 
    try: import pandas as pd # pip install pandas
    except: print("WRN: no pandas found...") # on python2.7, it will be ok
    try: import numpy as np
    except: pass
    if os.name == "nt":
        try:
            df = pd.read_excel( filename, sheet_name=None, header=None)
        except UnboundLocalError:
            # if doesn't work with python2,  so relying on loading exploded too
            # on my windows: python2 -m pip install pandas => LookupError: unknown encoding: cp65001
            # mais en fait mon terminal etait messed up, so j'ai fait: set PYTHONIOENCODING=UTF-8
            return load_datas_from_xlsx_exploded_for_python27(filename, encoding=encoding)

    else:
        #~ import openpyxl # pip install openpyxl # to shout if missing
        #~ df = pd.read_excel( filename, sheet_name=None, header=None, engine='openpyxl' ) # bug in 1.2.0, not in 1.1.5 # pip install pandas==1.1.5 (not existing in python2)
        # rien ne fonctionne en python2.7
        #~ df = pd.read_excel( filename, sheet_name=None, header=None )
        if sys.version_info[0] < 3:
            return load_datas_from_xlsx_exploded_for_python27(filename, encoding=encoding)

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
                    
    if  sys.version_info[0] >= 3 and os.name != "nt":
        # generate one cvs per tab, so you can read them back with python2.7
        fIndex = io.open(filename+"__index.csv", "wt", encoding="cp1252")
        for k,content in dOut.items():
            fn = filename+"__"+k+".csv"
            print("INF: writing to independant csv: %s" % fn )
            f = io.open(fn,"wt", encoding=encoding)
            for line in content:
                for nfield,field in enumerate(line):
                    #~ print("field: %s" % field )
                    f.write( str(field))
                    # change: we always want to finish a line with a ; so a ;\n is a real end of record
                    if nfield+1 < len(line) or 1:
                        f.write(";")
                f.write("\n")
            f.close()
            fIndex.write(k+"\n")
        fIndex.close()
    
    return dOut
    
#~ load_datas_from_xlsx( r"C:\Users\alexa\dev\git\obo\www\chatbot\OBO_Recruitement_dialog.xlsx")
    
def save_csv(filename, data, bForceEndingBySeparator=True):
    sepa = ';'
    file = open(filename, "wt")
    for fields in data:
        s = ""
        for i in range(len(fields)):
            if i != 0 and not bForceEndingBySeparator: s += sepa
            if type(fields[i]) == type('s'):
                s += '"%s"' % fields[i]
            else:
                s+= '%s' % fields[i]
            if bForceEndingBySeparator:
                s += sepa
        file.write(s+"\n")
    file.close()
    
    
def autotest():
    loadmethods = [load_csv,load_csv_multiline]
    loadmethods = [load_csv_multiline]
    for loadmethod in loadmethods:
        print("\nINF: Testing method: %s" % loadmethod )
        datas = [ [12,"toto", 3.5], [13,"tutu", 0.0, ""] ]
        save_csv("/tmp/tmp.dat", datas)
        datas2 = loadmethod("/tmp/tmp.dat")
        print("DBG: datas : %s" % str(datas) )
        print("DBG: datas2: %s" % str(datas2) )
        assert(datas==datas2)

        datas = [ [12,"toto\ntutu\ntiti", 3.5], [13,"tutu", 0.0, ""] ] # ok
        datas = [ [12,"toto\ntutu\ntiti", 3.5], [13,"tutu", 0.0, ""], ['tutu\n\n\ntata', 'toto\ntonton', 3], [4] ] # ok now
        save_csv("/tmp/tmp.dat", datas)
        datas2 = loadmethod("/tmp/tmp.dat",bVerbose=1)
        print("DBG: datas : %s" % str(datas) )
        print("DBG: datas2: %s" % str(datas2) )
        assert(datas==datas2)

        datas = [ ["Bonjour,\nComment Allez vous?\n\nAdieu"] ] # ok
        save_csv("/tmp/tmp.dat", datas)
        datas2 = loadmethod("/tmp/tmp.dat",bVerbose=1)
        print("DBG: datas : %s" % str(datas) )
        print("DBG: datas2: %s" % str(datas2) )
        assert(datas==datas2)
    
    print("INF: autotest passed [GOOD]")
    
if __name__ == "__main__":
    autotest()
            