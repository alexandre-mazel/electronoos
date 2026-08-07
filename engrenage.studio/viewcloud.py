#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import urllib.parse
import mimetypes
from datetime import datetime

ROOT_DIR = "/home/pi/media"
ROOT_DIR = "/home/na/dev/git/electronoos/engrenage.studio/files/"
URL_PREFIX = "/files/"


IMAGE_EXT = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff",
    ".heic"
}

VIDEO_EXT = {
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".wmv",
    ".webm",
    ".m4v",
    ".3gp"
}

import os
import subprocess
from PIL import Image, ImageOps

IMAGE_EXT = {
    ".jpg", ".jpeg", ".png", ".bmp",
    ".gif", ".webp", ".tif", ".tiff", ".heic"
}

VIDEO_EXT = {
    ".mp4", ".avi", ".mov", ".mkv",
    ".wmv", ".webm", ".m4v", ".3gp"
}


def generate_thumbnail(src_filename, thumb_root, src_root):
    """
    Generate a thumbnail for an image or a video.

    Parameters
    ----------
    src_filename : str
        Absolute filename of the source image/video.

    thumb_root : str
        Root directory where thumbnails are stored.

    src_root : str
        Root directory of the media library.

    Returns
    -------
    str
        Absolute thumbnail filename.
    """

    #~ rel = os.path.relpath(src_filename, src_root)

    #~ thumb_filename = os.path.join(
        #~ thumb_root,
        #~ os.path.splitext(rel)[0] + ".jpg"
    #~ )
    
    thumb_filename = src_filename.replace(src_root,thumb_root)
    thumb_filename = os.path.splitext(thumb_filename)[0] + ".jpg"

    if os.path.exists(thumb_filename):
        return thumb_filename, False

    os.makedirs(os.path.dirname(thumb_filename), exist_ok=True)

    ext = os.path.splitext(src_filename)[1].lower()

    try:

        if ext in IMAGE_EXT:
            
            print( "INF: generate_thumbnail: generating from IMG for '%s'" % src_filename )

            with Image.open(src_filename) as img:

                img = ImageOps.exif_transpose(img) # rotate based on exif flags
                img = img.convert("RGB")
                img.thumbnail((320, 240), Image.LANCZOS)
                img.save(thumb_filename, "JPEG", quality=88)

        elif ext in VIDEO_EXT:
            
            print( "INF: generate_thumbnail: generating from VIDEO for '%s'" % src_filename )

            result = subprocess.run(
                [
                    "ffmpeg",
                    "-loglevel", "verbose",
                    "-y",
                    "-ss", "1",
                    "-i", src_filename,
                    "-frames:v", "1",
                    "-vf", "scale=320:240:force_original_aspect_ratio=decrease,pad=320:240:(ow-iw)/2:(oh-ih)/2",
                    thumb_filename
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            print("ffmpeg return:", result.returncode)

            if result.stdout:
                print("STDOUT:")
                print(result.stdout)

            if result.stderr:
                print("STDERR:")
                print(result.stderr)

            if result.returncode != 0:
                raise RuntimeError("ffmpeg failed")

        else:
            print("ERR: generate_thumbnail: unknown type" )
            return "",False

    except Exception as err:

        print("ERR: generate_thumbnail:", err)

        return "", False

    print( "INF: generate_thumbnail: generating OK to '%s'" % thumb_filename )

    return thumb_filename, True

def build_file_entry(fullname,thumbname):

    st = os.stat(fullname)

    relthumb = os.path.relpath(thumbname, ROOT_DIR).replace("\\", "/")
    relreal = os.path.relpath(fullname, ROOT_DIR).replace("\\", "/")

    ext = os.path.splitext(fullname)[1].lower()

    if ext in VIDEO_EXT:
        media_type = "video"
    else:
        media_type = "image"

    return {
        "name": os.path.basename(fullname),
        "folder": os.path.dirname(fullname),
        "size": st.st_size,
        "date": datetime.fromtimestamp(st.st_mtime).isoformat(),
        "type": media_type,
        "thumbnail": URL_PREFIX + urllib.parse.quote(relthumb),
        "url": URL_PREFIX + urllib.parse.quote(relreal)
    }


def scan():

    files = []

    total_size = 0
    
    generated_thumbnail = 0
    
    print("DBG: viewcloud.py.scan: generated_thumbnail: %d" % (generated_thumbnail) )
    

    for root, dirs, names in os.walk(ROOT_DIR):

        dirs.sort(reverse=True)
        names.sort(reverse=True)
        
        print("DBG: viewcloud.py.scan: dirs: %s, names len: %d" % (str(dirs),len(names) ) )

        for name in names:

            fullname = os.path.join(root, name)

            ext = os.path.splitext(name)[1].lower()

            if ext not in IMAGE_EXT and ext not in VIDEO_EXT:
                continue
                
            if 1 and generated_thumbnail < 10: # on est obligé de limiter le nombre de generation pour ne pas faire ramer la page qui attend pendant ce temps...
                # generate thumbnail
                thumbname, really_generated = generate_thumbnail(fullname,"/thumb/","/files/")
                if really_generated:
                    generated_thumbnail += 1
            else:
                thumbname = fullname

            try:
                entry = build_file_entry(fullname,thumbname)
                files.append(entry)
                total_size += entry["size"]
            except Exception as err:
                print( "ERR: scan: err: %s" % str(err) )
                

    return {
        "count": len(files),
        "total_size": total_size,
        "files": files
    }


def send_json(obj):

    txt = json.dumps(obj, ensure_ascii=False)

    #~ sys.stdout.write("Content-Type: application/json\r\n")
    #~ sys.stdout.write("Cache-Control: no-cache\r\n")
    #~ sys.stdout.write("\r\n")
    #~ sys.stdout.write(txt)
    
    return txt


def index(req):

    qs = os.environ.get("QUERY_STRING", "")
    
    print("DBG: viewcloud.py.index: qs: '%s'" % qs )
    print("DBG: viewcloud.py.index: req.args: '%s'" % req.args )
    
    

    if req.args == "list&pwd=alex":        
        return send_json(scan())
        
    print( "DBG: access denied!" )

    return send_json({
        "success": False,
        "error": "unknown command"
    })


if __name__ == "__main__":
    
    if 1:
        print("Generating video file test...")
        thumbname, really_generated = generate_thumbnail("/home/na/dev/git/electronoos/engrenage.studio/files/alex/A52s/internal/DCIM/Camera/20260724_173801.mp4","/thumb/","/files/")
        import time
        time.sleep(180) # time for subprocess to start and finished...
        exit(0)
        
    from types import SimpleNamespace

    req = SimpleNamespace()
    req.args = "list"
    index(req)