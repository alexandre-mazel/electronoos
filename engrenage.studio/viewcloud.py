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
        return thumb_filename

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

            subprocess.run(
                [
                    "ffmpeg",
                    "-loglevel", "error",
                    "-y",
                    "-i", src_filename,
                    "-ss", "1",
                    "-frames:v", "1",
                    "-vf", "scale=320:240:force_original_aspect_ratio=decrease,pad=320:240:(ow-iw)/2:(oh-ih)/2",
                    thumb_filename
                ],
                check=True
            )

        else:
            return None

    except Exception as err:

        print("ERR generate_thumbnail:", err)

        return None

    print( "INF: generate_thumbnail: generating OK to '%s'" % thumb_filename )

    return thumb_filename

def build_file_entry(fullname,thumbname):

    st = os.stat(fullname)

    relthumb = os.path.relpath(thumbname, ROOT_DIR).replace("\\", "/")

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
        "thumbnail": URL_PREFIX + urllib.parse.quote(relthumb);
        "url": URL_PREFIX + urllib.parse.quote(fullname)
    }


def scan():

    files = []

    total_size = 0

    for root, dirs, names in os.walk(ROOT_DIR):

        dirs.sort(reverse=True)
        names.sort(reverse=True)

        for name in names:

            fullname = os.path.join(root, name)

            ext = os.path.splitext(name)[1].lower()

            if ext not in IMAGE_EXT and ext not in VIDEO_EXT:
                continue
                
            if 1:
                # generate thumbnail
                thumbname = generate_thumbnail(fullname,"/thumb/","/files/")
            else:
                thumbname = fullname

            try:
                entry = build_file_entry(fullname,thumbname)
                files.append(entry)
                total_size += entry["size"]
            except Exception as err:
                print( "ERR: scan: err: %s" % str(err) )
                
            if len(files) > 20:
                print( "DBG: scan: exiting after 20 files...")
                break
                
                
        if len(files) > 20:
            print( "DBG: scan: exiting after 20 files... (2)")
            break


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
    
    

    if req.args == "list":        
        return send_json(scan())

    return send_json({
        "success": False,
        "error": "unknown command"
    })


if __name__ == "__main__":
    index()