from crypt_words import listWords


def bruteForceTable(listWords,listCryptedWords):
    """
    Receive a list of crypted words and find a possible conversion.
    Return convTable, listDecodedWords.
        - convTable: table of conversion for decoding crypt=>uncrypt
        - listDecodedWords: list of decoded words using our produced table
    """
    # ALL UPPERCASE
    
    # iterate all possible combination crypted words => real currently to
    idx_combi = 0
    nw = len(listWords)
    nNbrTotalWordCombi = pow(nw,len(listCryptedWords))
    nNumCombi = 0
    while 1:
        # construct the combination 
        combi = []
        c = nNumCombi
        for i in range(len(listCryptedWords)):
            combi.append(c%nw)
            c //= nw
        print("\ncombi: %s" % combi)
        
        
        nNumCombi += 1
        if nNumCombi >= nNbrTotalWordCombi:
            break
        
        """
                s = ""
                s += "a"
                s += "b"
                => s vaut "ab"
        """
    
        # now we test if this combi is possible
        convTable = [-1]*26
        # ieme crypted letter => ieme decoded, eg si convTable[0] = 3 => the crypted letters 'A' is given the decoded one 'C'
        
        for idx_crypted,idx_clear in enumerate(combi):
            wc, w = listCryptedWords[idx_crypted],listWords[idx_clear].upper()
            print("Comparing %s and %s" % (wc,w) )
            # adding to table
            if len(wc) != len(w):
                print("diff len")
                break
            bIncompatible = False
            for i in range(len(wc)):
                numCrypted = ord(wc[i])-ord('A')
                numUncrypted = ord(w[i])-ord('A')
                decode = convTable[numCrypted]
                if decode != -1:
                    if decode != numUncrypted:
                        print("incompat letter num: %s" % i )
                        bIncompatible = True
                        break
                else:
                    # store this char
                    convTable[numCrypted] = numUncrypted
                    
            if bIncompatible:
                break
        else:
            print("Found!")
            return
            
    #~ for cw in listCryptedWords:
        #~ print(cw)
        
    print("NOT FOUND!")
        

# bruteforce - end
    
    
    
ret = bruteForceTable(listWords, ["FGF","TGMYWJ","HQLZGF"])
ret = bruteForceTable(listWords, ["HDAGUFBGA","UNAEM","KNAFUNIGEQ"])
print(ret)