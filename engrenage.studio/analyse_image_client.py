import cv2
import requests


def send_image_to_analyse( filename_img ):
    print( "INF: analyse_image_client: send_image_to_analyse: results:" )

    # Non c'est le binaire tel quel qu'il faut envoyer
    if 0:
        image_bytes = cv2.imread( filename_img )
        if image_bytes is None:
            print( "ERR: send_image_to_analyse: can't open '%s'" % filename_img )
            return 
        success, encoded = cv2.imencode(".jpg", image_bytes)  # ou alors le reencoder en jpg, mais c'est dommage
    
    with open( filename_img, "rb" ) as f:
        image_bytes = f.read()
        

    
    headers = {
        "X-Image-Filename": filename_img,
        "X-User-Id": "tester",
        "Content-Type": "application/octet-stream",
    }

    url = "https://engrenage.studio:45003/anaimg"
    response = requests.post( url, data=image_bytes, headers=headers )


    if response.status_code != 200:
        print("ERREUR SERVEUR:", response.status_code)
        print(response.text)
        return

    result = response.json()
    
    print(result)

    description = result["description"]
    keywords = result["keywords"]
    text = result["text"]
    peoples = result["peoples"]
    
    print( "INF: analyse_image_client: send_image_to_analyse: results:" )
    print( "description: %s" % description )
    print( "keywords: %s" % keywords )
    print( "text: %s" % text )
    print( "peoples: %s" % peoples )
    
    
def test():
    names = ["20260906_210413_small","WA_corto_niko_et_myr","WA_famille_regarde_film"]
    for name in names[2:]:
        fn = "../test/%s.jpg" % name
        ret = send_image_to_analyse( fn )
        print( "ret: %s" % ret )
        #~ break


if __name__ == "__main__":
    test()
    
