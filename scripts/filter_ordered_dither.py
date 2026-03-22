# -*- coding: utf-8 -*-

"""
Applique un vieux filtre de dither sur une image (inspir" du projet photosmile)
"""
import cv2
import numpy as np
import sys

# 4x4 Bayer matrix
bayer4_vectorized = np.array([
    [0,  8,  2, 10],
    [12, 4, 14,  6],
    [3, 11,  1,  9],
    [15, 7, 13,  5]
], dtype=np.float32)

bayer4_vectorized = (bayer4_vectorized + 0.5) / 16.0  # normalize thresholds

def ordered_dither_vectorized(img, tile_vectorized):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    img = img / 255.0
    h, w = img.shape
    
    size_tile = tile_vectorized.shape[0]

    # tile Bayer matrix to image size
    tiled = np.tile(tile_vectorized, (h // size_tile + 1, w // size_tile + 1))[:h, :w]

    # threshold comparison (vectorized)
    dithered = img > tiled
    
    img = cv2.cvtColor((dithered * 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
    
    return img
    
    
def filter_ordered_on_image( filename_src, filename_dst, ratio = 3 ):
    """
    - ratio: permettre d'agrandir le motif de croix (degrade l'image)
    """
    print( "INF: filter_ordered_on_image: '%s' => '%s'" % ( filename_src, filename_dst ) )
    assert( filename_src != filename_dst )
    im = cv2.imread( filename_src )
    
    im = cv2.resize(im,(0,0),fx= 1/ratio, fy = 1/ratio )
    im = ordered_dither_vectorized( im, bayer4_vectorized )
    im = cv2.resize(im,(0,0), fx=ratio, fy = ratio )
    
    cv2.imwrite( filename_dst, im )
    
if __name__ == "__main__":
    if len( sys.argv ) < 3:
        print( "syntaxe: %s <filename_src> <filename_dst> [ratio rezoom, default:3]" )
        exit(0)
    ratio = 3
    if len( sys.argv ) > 3:
        ratio = int( sys.argv[3] )
    print( "Using ratio %d" % ratio )
    filter_ordered_on_image( sys.argv[1], sys.argv[2], ratio )