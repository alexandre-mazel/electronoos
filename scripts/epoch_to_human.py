import os
import sys
strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools

epoch = float(sys.argv[-1])
print("%s => %s" % (epoch,misctools.convertEpochToSpecificTimezone(epoch)))