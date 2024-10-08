import os

import sys

def rename_all_files_in_folder( strPath, strBefore, strAfter ):
    files = os.listdir(strPath)
    cpt = 0
    for f in files:
        absf = strPath+f
        newf = strPath+f.replace(strBefore, strAfter)
        if absf == newf:
            continue
        print("INF: rename_all_files_in_folder: %s => %s" % (absf,newf) )
        if 1:
            os.rename(absf,newf)
        cpt += 1
    print("INF: rename_all_files_in_folder: %s file(s) renammed" % cpt )
    
    
    
rename_all_files_in_folder("./", "__2024_10_07__from_fashion", "__2024_10_07__from_fairmont")