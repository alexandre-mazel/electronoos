# https://mensuel.framapad.org/p/djd1ai3arq-a7rq
listWords = [
    "maman",
    "Maman",
    "Papa",
    "gamin",
    "cheval",
    "oui",
    "non",
    "peut-etre",
    "manger",
    "bouger",
    "antifatigue",
    "python",
    "cours",
    "sous-marin",
    "bateau",
    "tank"
    "acheter",
    "toucher",
    "couler"
]


def crypt_rot(w):
    #~ print("DBG: crypt_rot: encrypting '%s'" % w )
    o = ""
    for c in w:
        numChar = ord(c)-ord('A')
        numChar += 12
        numChar = numChar % 26
        o += chr(numChar+ord('A'))
    return o
    
def crypt_rotdec(w):
    #~ print("DBG: crypt_rot: encrypting '%s'" % w )
    o = ""
    for i,c in enumerate(w):
        numChar = ord(c)-ord('A')
        numChar += 12+i*7
        numChar = numChar % 26
        o += chr(numChar+ord('A'))
    return o
    
    
if __name__ == "__main__":
    print("seq1:")
    print("test:")
    print(crypt_rot(listWords[0]))
    print("realseq1:")
    for i in [6,9,11]:
        print(crypt_rot(listWords[i]))
    
    print("\nseq2:")
    print("test:")
    print(crypt_rotdec(listWords[0]))
    print("realseq2:")
    for i in [7,12,13]:
        print(crypt_rotdec(listWords[i]))