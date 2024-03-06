"""
The goal is to embed a file in a C/C++ program, eg an arduino.
The file is compressed and will be uncompressed on the fly in ram
"""
import unishox2
# to have it:
# git clone https://github.com/tweedge/unishox2-py3.git
# then into the repo:
# git clone it clone https://github.com/siara-cc/Unishox2
#  (to get the source in c to generate pypi)
# then python setup.py install

import os
import sys

def outputToSrc( data, dest_template_name, n_original_size = -1 ):
    """
    Generate a C/C++ source file embedding some binary datas
    - n_original_size: if -1: data aren't compressed
    """
    strH = '#ifndef __%s__"' % dest_template_name.upper()
    strH = '#define __%s__"' % dest_template_name.upper()
    strCpp = '#include "%s.h"' % dest_template_name
    
    strDestName = dest_template_name + ".h"
    print("INF: Writing to '%s'" % strDestName )
    f = open(strDestName, "wt")
    f.write(strH)
    f.close()
    
    strDestName = dest_template_name + ".cpp"
    print("INF: Writing to '%s'" % strDestName )
    f = open(strDestName, "wt")
    f.write(strCpp)
    f.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print( "syntax: scriptname <file> [filename]");
        print( "eg: scriptname index.html will generate data_index_html.h and data_index_html.cpp");
        exit(-1)
        
        
    strDataFilename = sys.argv[1]
    
    if len(sys.argv) > 2:
        template_name = sys.argv[2]
    else:
        strDataFilenameBase = os.path.basename( strDataFilename )
        template_name = strDataFilenameBase.replace( ".", "_" )
        
    
    print("INF: opening '%s'" % strDataFilename )
    f = open(strDataFilename)
    buf = f.read()
    compressed, original_size = unishox2.compress(buf)
    print("INF: size before: %d, after: %d, gain: %5.2f%%" % (original_size,len(compressed),100*(1-(float(len(compressed))/original_size))) )
    
    bOutputCompressed = 0
    #~ bOutputCompressed = 1
    if bOutputCompressed:
        outputToSrc( compressed, template_name, original_size )
    else:
        outputToSrc( buf,template_name )
    



