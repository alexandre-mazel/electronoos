

def analyseFile( filename ):
    """
    analyse a file and try to find repetition
    """
    print( "analysing '%s'" % filename )
    file = open( filename, "rt" );
    buf = file.read();
    file.close();
    
    lines = buf.split();
    print lines;
    
    nPrev = -1;
    nCptAlternate = 0;
    nCptEqual = 0;
    nMaxAlternate = 0;
    for line in lines:
        try:
            n = int(line);
        except:
            print( "(skipping: '%s')" % line );
            continue;
        if( n != nPrev ):
            nCptAlternate += 1;
            if( nCptEqual > 15 ):
                print( "equal: %dx%d" % (nCptEqual+1,nPrev) );
            nCptEqual = 0;            
        else:
            nCptEqual += 1;
            if( nCptAlternate > 15 ):
                print( "alternate: %d" % nCptAlternate );
            nCptAlternate = 0;
            
        nPrev = n;
        
    
# analyseFile - end

analyseFile( "/home/a/tmp2/serial_no.txt" );
analyseFile( "/home/a/tmp2/serial_yes.txt" );