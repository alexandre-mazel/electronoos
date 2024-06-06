

def getIdxInAlpha(c):
    return ord(c)-ord('a')
    
def crypt_vigenere(txt,key):
    o = ""
    for i in range(len(txt)):
        letter = txt[i]
        if letter < 'a' or letter > 'z':
            o += letter
            continue
        k = key[i%len(key)]
        idx_crypted_letter = ( getIdxInAlpha(letter) + getIdxInAlpha(k) ) % 26
        crypted_letter = chr(idx_crypted_letter + ord('a'))
        #~ print("%s => %s" % (letter,crypted_letter))
        o += crypted_letter
    return o
    
    
    
print(crypt_vigenere("coucou le chat.","allo"))

print(crypt_vigenere("a nous le gouter!","optionia"))