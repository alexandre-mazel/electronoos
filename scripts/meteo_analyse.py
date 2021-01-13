import panda as pd


def getNbrHourWind( strFile ):
    df = pd.read_csv(strFile, compression='gzip', header=0, sep=' ', quotechar='"', error_bad_lines=False)
    
# getNbrHourWind - end
    
strName = "C:/Users/amazel/perso/docs/creativeV/meteodata/"
print("getNbrHourWind: %s" % getNbrHourWind(strName) )