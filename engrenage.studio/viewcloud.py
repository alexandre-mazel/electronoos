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
URL_PREFIX = "/media/"


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


def build_file_entry(fullname):

    st = os.stat(fullname)

    rel = os.path.relpath(fullname, ROOT_DIR).replace("\\", "/")

    ext = os.path.splitext(fullname)[1].lower()

    if ext in VIDEO_EXT:
        media_type = "video"
    else:
        media_type = "image"

    return {
        "name": os.path.basename(fullname),
        "folder": os.path.dirname(rel),
        "size": st.st_size,
        "date": datetime.fromtimestamp(st.st_mtime).isoformat(),
        "type": media_type,
        "thumbnail": URL_PREFIX + urllib.parse.quote(rel)
    }


def scan():

    files = []

    total_size = 0

    for root, dirs, names in os.walk(ROOT_DIR):

        dirs.sort()
        names.sort()

        for name in names:

            fullname = os.path.join(root, name)

            ext = os.path.splitext(name)[1].lower()

            if ext not in IMAGE_EXT and ext not in VIDEO_EXT:
                continue

            try:
                entry = build_file_entry(fullname)
                files.append(entry)
                total_size += entry["size"]
            except Exception:
                pass

    return {
        "count": len(files),
        "total_size": total_size,
        "files": files
    }


def send_json(obj):

    txt = json.dumps(obj, ensure_ascii=False)

    sys.stdout.write("Content-Type: application/json\r\n")
    sys.stdout.write("Cache-Control: no-cache\r\n")
    sys.stdout.write("\r\n")
    sys.stdout.write(txt)


def index(req):

    qs = os.environ.get("QUERY_STRING", "")

    if qs == "list":

        send_json(scan())
        return

    send_json({
        "success": False,
        "error": "unknown command"
    })


if __name__ == "__main__":
    index()