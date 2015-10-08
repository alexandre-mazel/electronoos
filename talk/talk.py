

def talk():
    while( 1 ):
        s = raw_input( "Humain: " );
        s = s.lower();
        ans = "je n'ai pas compris!"
        if( "bonjour" in s ):
            ans = "salut"
        if( "au revoir" in s ):
            ans = "bye"
            
        print "Ordinateur: " + ans
        
        if( ans == "bye" ):
            break;
    
    
    
talk();