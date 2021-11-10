from Crypto.PublicKey import RSA # pip install pycrypto

def testKeyImportExport():
    key = RSA.generate(2048)
    encoded_key = key.exportKey('DER')
    key2 = RSA.importKey(encoded_key)
    assert( key == key2 )
    
    public_key = key.publickey()
    encoded_key = public_key.exportKey('DER')
    public_key2 = RSA.importKey(encoded_key)
    assert( public_key == public_key2 )
    
    key = RSA.generate(1024)
    encoded_key = key.exportKey('PEM')
    key2 = RSA.importKey(encoded_key)
    assert( key == key2 )
    
    print("INF: encrypt.testKeyImportExport: test PASS" )
#testKeyImportExport - end
    
def generateKeys():
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()
    ex_prv  = private_key.exportKey(format='PEM')
    ex_pub = public_key.exportKey(format='PEM')

    file = open("key.prv", "wt")
    file.write(str(ex_prv))
    file.close()

    file = open("key.pub", "wt")
    file.write(str(ex_pub))
    file.close()
    
class Encryptor:
    
    def __init__( self, strFilenamePublicKey = "key.pub", strFilenamePrivateKey = "key.prv" ):
        self.strFilenamePublicKey = strFilenamePublicKey
        self.strFilenamePrivateKey = strFilenamePrivateKey
        self.privateKey = None
        self.publicKey = None
        
    @staticmethod
    def _loadKey( strFilename ):
        with open(strFilename,'r') as fk:
            data = fk.read()
        fk.close()
        print(len(data))
        #~ print("key: " + str(data) )
        key = RSA.importKey(eval(data))
        return key            
        
    def encodeData( self, data ):
        if self.publicKey == None:
            self.publicKey = Encryptor._loadKey( self.strFilenamePublicKey )
        encrypted = self.publicKey.encrypt( data, 32 )
        return encrypted
        
    def decodeData( self, data ):
        if self.privateKey == None:
            self.privateKey = Encryptor._loadKey( self.strFilenamePrivateKey )
        decoded = self.privateKey.decrypt( data )
        return decoded
        
# class Encryptor - end

def autoTest():
    testKeyImportExport()
    generateKeys()
    
    enc = Encryptor()
    
    data = b"0123456789"
    print("data: '%s'" % str(data) )
    
    encoded = enc.encodeData(data)
    print("encoded: '%s'" % str(encoded) )
    
    data2 = enc.decodeData(encoded)
    print("data2: '%s'" % str(data2) )
    

if( __name__ == "__main__" ):
    autoTest()

