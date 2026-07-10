import os
import time
import urllib.parse
from http.server import SimpleHTTPRequestHandler, HTTPServer
from datetime import datetime
import cgi # generate a warning deprecated in Python 3.13
import io

# upload page: http://ip:8000/upload_photo.html?id=x
# eg: http://10.0.126.73:8000/upload_photo.html?id=1
# upload file: /upload?id=1
# to retrieve last img : /get_image?id=1
# eg: http://10.0.126.73:8000/get_image?id=6
# to retrieve just filename of last img: /get_image_filename?id=1

# served at rpi5 through avec ce script qui tourne dans un screen. Acces par:
# http://thenardier.fr:9500/upload_photo.html?id=6
# http://thenardier.fr:9500/get_image?id=6
# 

# reseaux public: caves du louvre (wistro) bonjour ?

class ImageServer(SimpleHTTPRequestHandler):
    

    def writeImageFromMultipartFormat( self, data, filename, length ):
        form = cgi.FieldStorage(
            fp=io.BytesIO(data),
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers.get("Content-Type"),
                "CONTENT_LENGTH": str(length),
            }
        )

        image_field = form["image"]

        image_bytes = image_field.file.read()

        with open(filename, "wb") as f:
            f.write(image_bytes)
        print( "INF: writeImageFromMultipartFormat: write an image of size %d in file: '%s'" % (len(image_bytes),filename) )
        return True
        
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        
        if parsed.path == "/upload":
            query = urllib.parse.parse_qs(parsed.query)
            image_id = query.get("id", ["1"])[0]
            print("do_POST: 1:upload apres query")

            if image_id is None or not image_id.isdigit() or not 0 <= int(image_id) <= 8:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"invalid id")
                print("do_POST: invalid id: %s", image_id)
                return

            print("do_POST: 2")
            folder = f"upload_{image_id}"
            os.makedirs(folder, exist_ok=True)

            length = int(self.headers.get("Content-Length", 0))
            data = self.rfile.read(length)
            
            print("do_POST: 3")

            filename = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".jpg"
            filepath = os.path.join(folder, filename)
            
            self.writeImageFromMultipartFormat( data, filepath, length )

            print("do_POST: 4")

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
            return

        self.send_response(404)
        self.end_headers()

    def do_GET(self):
        limit_time_photo_sec = 30
        print( "DBG: go_GET: '%s'" % self.path )
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/get_image":
            query = urllib.parse.parse_qs(parsed.query)
            image_id = query.get("id", [None])[0]

            if image_id is None or not image_id.isdigit() or not 1 <= int(image_id) <= 8:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"invalid id")
                return

            folder = f"upload_{image_id}"

            if os.path.exists(folder):
                files = [
                    os.path.join(folder, file)
                    for file in os.listdir(folder)
                    if os.path.isfile(os.path.join(folder, file))
                ]

                if files:
                    latest_file = max(files, key=os.path.getmtime)

                    if time.time() - os.path.getmtime(latest_file) < limit_time_photo_sec:
                        self.send_response(200)
                        self.send_header("Content-Type", "image/jpeg") # TODO: change selon extension du fichier!
                        self.end_headers()

                        with open(latest_file, "rb") as file:
                            self.wfile.write(file.read())
                        print( "INF: get_image: image sent..."  )
                        return
                    else:
                        # on l'efface (on en efface un de temps en temps, ca libere le disque)
                        print( "INF: erasing old file: '%s'" % latest_file )
                        os.unlink( latest_file )

            print( "INF: get_image: no img"  )
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"noimg")
            return
                
        if parsed.path == "/get_image_filename":
            query = urllib.parse.parse_qs(parsed.query)
            image_id = query.get("id", [None])[0]

            if image_id is None or not image_id.isdigit() or not 1 <= int(image_id) <= 8:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error":"invalid_id"}')
                return

            folder = f"upload_{image_id}"

            latest_file = None

            if os.path.exists(folder):
                files = [
                    file for file in os.listdir(folder)
                    if os.path.isfile(os.path.join(folder, file))
                    and file.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp"))
                ]

                if files:
                    latest_file = max(
                        files,
                        key=lambda file: os.path.getmtime(os.path.join(folder, file))
                    )

                    if time.time() - os.path.getmtime(os.path.join(folder, latest_file)) >= limit_time_photo_sec:
                        latest_file = None

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            if latest_file:
                response = f'{{"image":"{latest_file}"}}'
            else:
                response = '{"image":null}'

            self.wfile.write(response.encode())
            return
            
        if 1:
            # serve other files
            filepath = parsed.path.lstrip("/")
            query = urllib.parse.parse_qs(parsed.query)
            
            print( "DBG: file: '%s'" % filepath )
            print( "DBG: query: %s" % query )

            if filepath and os.path.isfile(filepath):
                self.send_response(200)

                if filepath.endswith(".jpg") or filepath.endswith(".jpeg"):
                    self.send_header("Content-Type", "image/jpeg")
                elif filepath.endswith(".png"):
                    self.send_header("Content-Type", "image/png")
                elif filepath.endswith(".txt"):
                    self.send_header("Content-Type", "text/plain")
                elif filepath.endswith(".html"):
                    self.send_header("Content-Type", "text/html")
                else:
                    self.send_header("Content-Type", "application/octet-stream")

                self.end_headers()

                with open(filepath, "rb") as file:
                    self.wfile.write(file.read())
                    
                print("INF: Replyed file...")
                return
            
            print( "WRN: not found file: '%s'" % filepath )

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"not found")


def main():
    port = 9500
    server = HTTPServer(("0.0.0.0", port), ImageServer)
    print( "INF: img_server: serving on port %d" % port )
    server.serve_forever()


if __name__ == "__main__":
    main()