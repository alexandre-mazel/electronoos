from crypt_words import listWords


def bruteForceTable(listCryptedWords):
    """
    Receive a list for crypted words find a good conversion.
    Return convTable, listDecodedWords.
        convTable: table of conversion for decoding crypt=>uncrypt
        listDecodedWords: 
    """
    for cw in listCryptedWords:
        print(cw)
        

# bruteforce - end
    
    
    
ret = bruteForceTable(listCleanWords, ["FGF","TGMYWJ","HQLZGF"])
print(ret)