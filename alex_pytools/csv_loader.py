import sys

def openWithEncoding( filename, mode, encoding, errors = 'strict' ):
    if sys.version_info[0] < 3:
        import io
        return io.open( filename, mode, encoding=encoding, errors=errors )
    return open( filename, mode, encoding=encoding, errors=errors )

def load_csv(filename):
    bVerbose=1
    bVerbose=0
    data = []
    enc = 'utf-8'    
    try:
        file = openWithEncoding(filename, "rt", encoding = enc)
    except:
        return data
        
    #~ line = file.readline() # skip first line
    
    while 1:
        line = file.readline()
        if len(line)<1:
            break
        if bVerbose: print("DBG: load_csv: line: '%s'" % line )
        if line[-1] == '\n': line = line[:-1] # erase last \n
        fields = line.split(';')
        for i in range(len(fields)):
            if bVerbose: print("DBG: load_csv: fields[i]: '%s'" % fields[i] )
            if fields[i][0] == '"' and fields[i][-1] == '"':
                fields[i] = fields[i][1:-1]
            else:
                # TODO: handle array
                if '.' in fields[i]:
                    fields[i] = float(fields[i])
                else:
                    fields[i] = int(fields[i])
        data.append(fields)
    return data
    
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
            