
# test nfc reader ACR122U-A9

import py122u # pip install py122u
from py122u import nfc

import smartcard # pip install pyscard

import time


reader = nfc.Reader()
while 1:
    try:
        reader.connect()
        data = reader.get_uid()
        print("data: " + str(data))
        #~ reader.print_data(data.decode("ascii"))
        reader.info()
    except smartcard.Exceptions.NoCardException:
        pass
    except py122u.error.NoCommunication:
        pass
    except py122u.error.InstructionFailed as err:
        print("DBG: py122u.error.InstructionFailed: %s" % str(err) )
    time.sleep(1)
