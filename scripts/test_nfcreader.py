# -*- coding: cp1252 -*-

# test nfc reader ACR122U-A9
# from https://github.com/Flowtter/py-acr122u/tree/master
# cf doc http://downloads.acs.com.hk/drivers/en/API-ACR122U-2.02.pdf

# device present dans devicemanager: USB smart card reader

import py122u # pip install py122u
from py122u import nfc

import smartcard # pip install pyscard

import time


def readContinuously(reader):
    while 1:
        try:
            reader.connect()
            data = reader.get_uid()
            print("data: " + str(data))
            #~ reader.print_data(data)
            reader.info()
            
            #~ dataread = read(reader, 0x01, 0x20)
            #~ print("read: %s" % str(dataread))
        except py122u.error.NoCommunication as err:
            #~ print("DBG: py122u.error.NoCommunication: %s" % str(err) )
            pass
        except smartcard.Exceptions.NoCardException:
            pass
        except smartcard.Exceptions.CardConnectionException:
            pass
            
        except py122u.error.InstructionFailed as err:
            print("DBG: py122u.error.InstructionFailed: %s" % str(err) )
        time.sleep(1)
        
"""
*** Mon mobile:

data: [0, 0, 0, 0]
50 00 00 00 00 00 00 00 00 80 81 45
00 00
Card Name: 
	T0 True
	T1 True
	T1 False

ou

data: [8, 49, 110, 118]


Card Name: 
	T0 True
	T1 True
	T1 False


*** Les cartes blanches livrées avec:

data: [73, 68, 170, 121]
80 4F 0C A0 00 00 03 06 03 00 01 00 00 00 00
00 01
Card Name: MIFARE Classic 1K
	T0 True
	T1 True
	T1 False

"""

"""
from so: https://stackoverflow.com/questions/74038986/write-password-to-ntag213-using-python-and-acr122u

from smartcard.System import readers
from smartcard.CardConnection import CardConnection
from smartcard.scard import SCARD_SHARE_DIRECT

reader = readers()[0]
connection = reader.createConnection()
connection.connect()

def createPseudoAPDU(payload, nBytes):
    #nBytes+0x2 to add the 0xd4 and 0x42 two bytes
    return np.concatenate(([0xff, 0x00, 0x00, 0x00, nBytes+0x2,0xd4,0x42], payload), axis=0).tolist() 


setPwd = createPseudoAPDU([0xa2, 0x2b,0x32,0x30,0x32,0x32],0x06)
setPack = createPseudoAPDU([0xa2, 0x2c,0x00,0x00,0x00,0x00],0x06)

setAuthLimAndProt = createPseudoAPDU([0xa2, 0x2a,0x00,0x05,0x00,0x00],0x06)

setauth0 = createPseudoAPDU([0xa2, 0x29,0x04,0x00,0x00,0x00],0x06)

r, sw1, sw2 = connection.transmit(setPwd)
print(r)
print(sw1)
print(sw2)

r, sw1, sw2 = connection.transmit(setPack)
print(r)
print(sw1)
print(sw2)

r, sw1, sw2 = connection.transmit(setAuthLimAndProt)
print(r)
print(sw1)
print(sw2)

r, sw1, sw2 = connection.transmit(setauth0)
print(r)
print(sw1)
print(sw2)
"""


def write(r, position, number, data):
    while number >= 16:
        write_16(r, position, 16, data)
        number -= 16
        position += 1


def write_16(r, position, number, data):
    r.update_binary_blocks(position, number, data)


def read(r, position, number):
    result = []
    while number >= 16:
        result.append(read_16(r, position, 16))
        number -= 16
        position += 1
    return result


def read_16(r, position, number):
    return r.read_binary_blocks(position, number)
    
def writeOnceCardIsOn(reader):
    reader.connect()
    #~ reader.mute_buzzer() # remove buzzer sound
    reader.unmute_buzzer()
    reader.load_authentication_data(0x01, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    reader.authentication(0x00, 0x61, 0x01)
    #~ write(reader, 0x01, 0x20, [i for i in range(16)])
    print(read(reader, 0x01, 0x20))






if __name__ == "__main__":
    reader = nfc.Reader()
    #~ readContinuously(reader)
    writeOnceCardIsOn(reader)