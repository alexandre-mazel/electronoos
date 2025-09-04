import os



def svg_to_png_folder( path ):
    
    files = sorted( os.listdir( path ) )
    
    dst_path = path + "export\\"
    try:
        os.makedirs( dst_path )
    except FileExistsError: pass
        
    for f in files:
        absf = path + f
        
        if os.path.isdir( absf ):
            continue
            
        if ".svg" not in f:
            continue
                
        print( "INF: svg_to_png_folder: converting '%s'" % f )
        path_inkscape = 'C:/Program Files/Inkscape/bin/'
        src = absf
        dst = dst_path + f.replace(".svg",".jpg")
        if 0:
            cmd_line = "\"%sinkscape.exe\" %s --export-type=jpg --export-filename=%s" % (path_inkscape, src,dst)
            print( "DBG: svg_to_png_folder: cmd_line '%s'" % cmd_line )
            os.popen( cmd_line ) # error: unexcepted fatal error encoutered, aborting
        else:
            import ctypes
            os.add_dll_directory("C:/Program Files/Tesseract-OCR")
            my_dll = ctypes.CDLL("libcairo-2.dll")
            import cairosvg  # pip install cairosvg
            cairosvg.svg2png( url=src, write_to=dst, scale=4.0 )
    
# svg_to_png_folder - end


if __name__ == "__main__":
    svg_to_png_folder( "C:\\Users\\alexa\\dev\\git\\ensadlab\\misbkit_v2\\dev_web\\icons\\" )
    
    
    