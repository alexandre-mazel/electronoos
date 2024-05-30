

def findPythonErrorBigTable(filename):
    """
    analyse a file in the form of
    tab = [
        [1,2],
        [1,2],
    ]

    and find a line not valid for interpretation.
    
    eg:
    
INF: findPythonErrorBigTable, file '../../obo/www/job_table.py'
INF: starting...

LINE: ["procurement_specialist","Procurement specialist","Sp&eacutecialiste des achats",
ERR: unexpected EOF while parsing (<string>, line 1)

LINE: ["purchasing_manager","Purchasing manager","Responsable des achats",
ERR: unexpected EOF while parsing (<string>, line 1)

LINE: ["nursery_assistant","Nursery assistant","Assistant(e) de pu&eacute;riculture",
ERR: unexpected EOF while parsing (<string>, line 1)

INF: 668 line(s) analysed, 3 error(s) found
>Exit code: 0

    """

    print("INF: findPythonErrorBigTable, file '%s'" % filename )
    print("INF: starting...\n")

    
    f = open(filename,"rt")
    buf = f.read()
    f.close()
    lines = buf.split("\n")
    
    nNumTested = 0
    nNumError = 0
    
    for line in lines:
        # print(line)
        line = line.strip()
        if("= [" in line or "]" == line):
            continue
            
        nNumTested += 1
        try:
            exec(line)
        except SyntaxError as err:
            print("LINE: %s" % line)
            print("ERR: %s\n" % str(err))
            nNumError += 1
        
    print("INF: %d line(s) analysed, %d error(s) found" % (nNumTested,nNumError) )
    
    
findPythonErrorBigTable( "../../obo/www/job_table.py")
