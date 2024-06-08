

def getIdxInAlpha(c):
    return ord(c)-ord('a')
    
def crypt_vigenere( txt, key, bDecrypt=False ):
    """
    - bDecrypt: to prevent cut&paste, this is internally the same method to crypt or decrypt
    """
    o = ""
    
    sign = 1
    if bDecrypt: sign = -1
    
    for i in range(len(txt)):
        letter = txt[i]
        if letter < 'a' or letter > 'z':
            o += letter
            continue
        k = key[i%len(key)]
        idx_crypted_letter = ( getIdxInAlpha(letter) + sign*getIdxInAlpha(k) ) % 26
        crypted_letter = chr(idx_crypted_letter + ord('a'))
        #~ print("%s => %s" % (letter,crypted_letter))
        o += crypted_letter
    return o
    
def decrypt_vigenere( txt, key ):
    return crypt_vigenere( txt, key, bDecrypt=True )
    
    
    
print(crypt_vigenere("coucou le chat.","allo"))



print(crypt_vigenere("a nous le gouter!","optionia"))

print(decrypt_vigenere("o gwif ls zwigmr!","optionia"))