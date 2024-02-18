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