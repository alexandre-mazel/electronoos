# -*- coding: utf-8 -*-

import os
import time
import urllib.parse
from http.server import SimpleHTTPRequestHandler, HTTPServer,ThreadingHTTPServer
from datetime import datetime
import cgi # generate a warning deprecated in Python 3.13
import io

"""
# Server running on 9520.
# two call:
# /info post, avec nom du fichier, path, size et date, et il repond present ou pas
# /upload post, avec nom de fichier, et path, il sauve le fichier et il repond ok ou pas
# eg:
http://engrenage.studio:9520/info?filename=test&path=testdir&size=5&modified=33
"""

class ImageServer(SimpleHTTPRequestHandler):
    

    def readMultipartFile(self, body, length, field_name="file"):
        form = cgi.FieldStorage(
            fp=io.BytesIO(body),
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers.get("Content-Type"),
                "CONTENT_LENGTH": str(length),
            }
        )

        return (
            form["filename"].value,
            form.getvalue("path", ""),
            int(form["size"].value),
            form[field_name].file.read()
        )

        image_field = form["image"]

        image_bytes = image_field.file.read()

        with open(filename, "wb") as f:
            f.write(image_bytes)
        print( "INF: writeImageFromMultipartFormat: write an image of size %d in file: '%s'" % (len(image_bytes),filename) )
        return True
        
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/info":
            try:
                # Read request body
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                data = json.loads(body)

                filename = data["filename"]
                rel_path = data.get("path", "")
                expected_size = int(data["size"])
                expected_mtime = int(data["modified"])

                # Prevent path traversal
                base_dir = os.path.abspath("files")
                file_path = os.path.abspath(
                    os.path.join(base_dir, rel_path, filename)
                )
                
                print( "DBG: do_POST: /info: received file_path: '%s'" % file_path )

                if not file_path.startswith(base_dir + os.sep):
                    raise ValueError("Invalid path")

                present = False

                if os.path.isfile(file_path):
                    stat = os.stat(file_path)

                    actual_size = stat.st_size
                    actual_mtime = int(stat.st_mtime)

                    present = (
                        actual_size == expected_size and
                        actual_mtime == expected_mtime
                    )

                response = {"present": present}

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))

            except (KeyError, ValueError, json.JSONDecodeError) as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": str(e)
                }).encode("utf-8"))

            return
        # /info

        
        if parsed.path == "/upload":
            try:
                length = int(self.headers["Content-Length"])
                body = self.rfile.read(length)

                filename, rel_path, expected_size, file_bytes = self.readMultipartFile(body, length)

                # save file_bytes...
                # Build destination safely
                base_dir = os.path.abspath("files")
                dest_dir = os.path.abspath(os.path.join(base_dir, rel_path))

                if not (dest_dir == base_dir or dest_dir.startswith(base_dir + os.sep)):
                    raise ValueError("Invalid path")

                os.makedirs(dest_dir, exist_ok=True)

                dest_file = os.path.join(dest_dir, filename)

                with open(dest_file, "wb") as f:
                    f.write(file_bytes)

                success = (
                    os.path.getsize(dest_file) == expected_size
                )

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": int(success)}).encode())

            except Exception as e:
                print("Upload error:", e)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"success":0}')

            return 
        # /upload

        self.send_response(404)
        self.end_headers()

    def do_GET(self):
        limit_time_photo_sec = 30
        print( "DBG: go_GET: '%s'" % self.path )
        parsed = urllib.parse.urlparse(self.path)

            
        if 0:
            pass


        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"not found")


def main():
    port = 9520
    #~ server = HTTPServer(("0.0.0.0", port), ImageServer)
    server = ThreadingHTTPServer(("0.0.0.0", port), ImageServer) # certains appels depuis chrome bloquait le thread (car chrome ne ferme pas la connection), lancer comme ca, c'est cool, meme si un thread est bloqué, un autre prend la main !
    print( "INF: almacloud: serving on port %d" % port )
    server.serve_forever()


if __name__ == "__main__":
    main()