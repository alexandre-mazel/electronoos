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
    return data
    
def load_datas_from_xlsx( filename ):
    """
    return a dict tab name then lines (without handling headers)
    """
    import xlrd # pip install xlrd 
    import openpyxl # pip install openpyxl 
    import pandas as pd
    import numpy as np
    df = pd.read_excel( filename, sheet_name=None, header=None )
    print(len(df))
    print(df)
    print(df.keys())
    dOut = {}
    for sheet_name,sheet_data in df.items():
        print("\nDBG: load_datas_from_xlsx: sheet_name: '%s', line(s): %d" % (sheet_name,len(sheet_data) ) )
        listLine = []
        sheet_data = sheet_data.fillna(value='nan')
        for data in sheet_data.itertuples(index=False):
            print(str(data))
            #~ listLine.append(data[:])
            for col in data:
                if col == 'nan':
                    break
                listLine.append(col)

        dOut[sheet_name] = listLine
    if 1:
        print( "\nDBG: load_datas_from_xlsx: output:" )
        for sheet_name,sheet_data in dOut.items():
            print("\nDBG: load_datas_from_xlsx: sheet_name: '%s', line(s): %d" % (sheet_name,len(sheet_data) ) )
            for line in sheet_data:
                print("")
                for col in line:
                    print("   '%s'" % col)
    
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
    
if __name__ == "__main__":
    autotest()
            