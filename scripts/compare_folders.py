import os
import sys

def compareFolder( path1, path2 ):
    """
    Check all folders and files in path1 are in path2 (but not the opposite).
    Return the nbr_of_total_folder_in_path1,nbr_of_total_file_in_path1, nbr_of_missing_folders, nbr_of_missing_files, nbr_different_sizes_files
    """
    nNbrFoldersTotal = 0
    nNbrFilesTotal = 0
        
    nNbrMissingFolders = 0
    nNbrMissingFiles = 0
    nNbrFilesDifferentSize = 0
    
    listFiles = sorted( os.listdir(path1) )
    for f in listFiles:
        absf1 = path1 + '/' + f
        print(absf1 + "    \r", end="")
        absf2 = path2 + '/' + f
        if os.path.isdir( absf1 ):
            nNbrFoldersTotal += 1
            if os.path.isdir( absf2 ):
                nfo, nfi, nmfo, nmfi, nfds = compareFolder( absf1, absf2 )
                nNbrFoldersTotal += nfo
                nNbrFilesTotal += nfi
                nNbrMissingFolders += nmfo
                nNbrMissingFiles += nmfi
                nNbrFilesDifferentSize += nfds
            else:
                nNbrMissingFolders += 1
            continue
        if os.path.isfile( absf1 ):
            nNbrFilesTotal += 1
            if os.path.isfile( absf2 ):
                s1 = os.path.getsize(absf1)
                s2 = os.path.getsize(absf2)
                if s1 != s2:
                    nNbrFilesDifferentSize += 1
            else:
                nNbrMissingFiles += 1
                
    lib = "GOOD"
    if nNbrMissingFolders > 0 or nNbrMissingFiles > 0 or nNbrFilesDifferentSize > 0:
        lib = "DIFF"
    print("%s: '%s' and '%s'  =>  %4d,%4d; %4d,%4d,%4d" % ( lib, path1, path2, nNbrFoldersTotal, nNbrFilesTotal, nNbrMissingFolders, nNbrMissingFiles, nNbrFilesDifferentSize) )
    return nNbrFoldersTotal, nNbrFilesTotal, nNbrMissingFolders, nNbrMissingFiles, nNbrFilesDifferentSize
                
                
if __name__ == "__main__":
    if 0:
        path1 = "e:/"
        path2 = "f:/"

        subpath = "Inria-0342_Crowdbot/"
        path1 = "e:/" + subpath
        path2 = "f:/" + subpath
        
    else:
        # info from command line
        if len(sys.argv) < 3:
            print( "Compare all file in path 1 are in path 2")
            print( "Syntax: <scriptname> path1 path2" )
            exit(-1)
        path1 = sys.argv[1]
        path2 = sys.argv[2]
        
    print("\nComparing '%s' and '%s'\n" % (path1,path2) )
    nNbrFoldersTotal, nNbrFilesTotal, nNbrMissingFolders, nNbrMissingFiles, nNbrFilesDifferentSize = compareFolder( path1, path2 )

    print( "       nNbrFoldersTotal: %d" % nNbrFoldersTotal )
    print( "       nNbrFilesTotal: %d" % nNbrFilesTotal )
    print( "       nNbrMissingFolders: %d" % nNbrMissingFolders )
    print( "       nNbrMissingFiles: %d" % nNbrMissingFiles )
    print( "       nNbrFilesDifferentSize: %d" % nNbrFilesDifferentSize )
