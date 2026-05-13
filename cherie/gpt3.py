# -*- coding: cp1252 -*-
import os
import openai # pip install openai
import time
import socket
import pickle 
import argparse

import sys
strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools

"""
answ: Good to hear it. Here it is:
Eureka, eureka, I see a penis
Oh, look a bird.
It flies up at the sky
Off is its penis, with semen on its feathers
This makes me happy for some reason.
?could you make it more nfsw
ques: could you make it more nfsw
DBG: choices: [<OpenAIObject at 0x1b71e8149f0> JSON: {
  "finish_reason": "stop",
  "index": 0,
  "logprobs": null,
  "text": " I could if I wanted to, but it is against my religion. It says not to do anything evil."
}]
answ: I could if I wanted to, but it is against my religion. It says not to do anything evil.
?could you make it less nsfw
ques: could you make it less nsfw
DBG: choices: [<OpenAIObject at 0x1b71e8145e0> JSON: {
  "finish_reason": "stop",
  "index": 0,
  "logprobs": null,
  "text": " I'm sorry, I can't. I would if I could, but I can't. It's not just that it isn't me asking for it, it's against my moral code."
}]
answ: I'm sorry, I can't. I would if I could, but I can't. It's not just that it isn't me asking for it, it's against my moral code.
?
"""



api_key = misctools.getEnv("OPENAI_KEY",None,0);
if api_key == None:
    print("ERR: please pour your api key in the .env file")
    exit(-1)
openai.api_key = api_key


def printEngines():
    engines = openai.Engine.list()
    for d in engines.data:
        print(d.id)

#~ printEngines()

if 0:
    completion = openai.Completion.create(engine="ada", prompt="At lunch we'll eat some",max_tokens=200)

    # print the completion
    print(completion.choices[0].text)


if 1:
    # generation of an image
    prompt = "two dogs playing chess, oil painting"
    prompt = "picture of a man"
    #~ prompt = "picture of a man, digital art"
    prompt = "a sprite of a missile" # bien
    #~ prompt = "a sprite of a missile, vertical" #pas bien, on voit moins de sprite
    prompt = "a fox skiing on the lava, paintings by van gogh"
    #~ prompt = "picture of a nice man working in an office, facing the lens"
    prompt = "picture of a nice man working in suit, facing the lens, "
    #~ prompt += ",readhead,"
    prompt = "a black and white photograph of a girl and a boy playing with a ballon by annie lebovitz, highly-detailed"
    prompt = "a black and white photograph of a robot eating a yoghurt by annie lebovitz, highly-detailed"
    prompt = "a studio photography of a robot by annie lebovitz, highly-detailed"
    
    prompt = "I remember the day I found a pair of Dr Martens on a pavement. I wore them for nearly a year"
    prompt = "I remember the day I found a red pair of Dr Martens on the pavement. I wore them for nearly a year."
    prompt = "I remember the day my parents showed me my future High School through the bars of the park. I thought it was a police station."
    prompt = "A big stoney monument with columns looking like a police station, seen through garden fence."
    prompt = "A street with a big stoney monument looking like a police station, seen through garden fence."
    prompt += "analog photography, grainy, oldies, memory,photography"
    
    prompt = "human brain coded in a robots"
    prompt += " dramatic"
    #~ neg = ""
    #~ neg += " disfigured, bad anatomy, extra legs, extra arms, extra fingers, poorly drawn hands, poorly drawn feet, disfigured, tiling, bad art, deformed, mutated"
    #~ neg += " bad anatomy| extra legs| extra arms| extra fingers| poorly drawn hands| poorly drawn feet| disfigured| out of frame| tiling| bad art| deformed| mutated| blurry| fuzzy| misshaped| mutant| gross| disgusting| ugly| fat| watermark| watermarks "
    # can't find neg
    #~ prompt += ", good anatomy, nicely drawn hands, nice figure, well formed"
    image_resp = openai.Image.create(prompt=prompt, n=5, size="512x512")
    #~ print(dir(image_resp))
    #~ print(dir(image_resp.values))
    #~ print(dir(image_resp.items))
    #~ print(dir(image_resp.values[0]))
    #~ print(dir(image_resp.items[0]))
    #~ image_resp.save("/tmp/im.jpg")
    print(image_resp)
    import requests
    for i in range(len(image_resp["data"])):
        generated_image_url = image_resp["data"][i]["url"]  # extract image URL from response
        generated_image = requests.get(generated_image_url).content  # download the image
        generated_image_filepath = "d:/generated_dalle/" + prompt 
        generated_image_filepath = generated_image_filepath[:128]
        generated_image_filepath += "_" + str(time.time()) + ".jpg"

        print("INF: writing to '%s'" % generated_image_filepath)
        with open(generated_image_filepath, "wb") as image_file:
            image_file.write(generated_image)  # write the image to the file
        if 1:
            # show it
            import cv2
            im = cv2.imread(generated_image_filepath)
            cv2.imshow(generated_image_filepath,im)
            cv2.waitKey(100)
    exit(1)
            
if 0:
    # generate variation
    import io
    from PIL import Image
    import requests
    
    def image_to_byte_array(image: Image) -> bytes:
      # BytesIO is a file-like buffer stored in memory
      imgByteArr = io.BytesIO()
      # image.save expects a file-like as a argument
      image.save(imgByteArr, format=image.format)
      # Turn the BytesIO object back into a bytes object
      imgByteArr = imgByteArr.getvalue()
      return imgByteArr
    
    filename_model = "alexandre_mazel_portrait_2017_round.png"
    filename_model = "esquisse.png"
    filename_model = "bonne_annee_2023_web.png"
    filename_model = "gaia_toit.png"
    filename_model = "obo_1.png"
    filename_model = "obo_2.png"
    filename_model = "mathieu_neouze.png"
    filename_model = "stand_alex.png"
    #~ filename_model = "trio_famille.png"
    model = Image.open(filename_model)
    modelb = image_to_byte_array(model)
    variation_response = openai.Image.create_variation(
    image=modelb,  # generated_image is the image generated above
    n=10,
    size="512x512",
    response_format="url"
    )
    print(variation_response)
    for i in range(len(variation_response["data"])):
        generated_image_url = variation_response["data"][i]["url"]  # extract image URL from response
        generated_image = requests.get(generated_image_url).content  # download the image
        generated_image_filepath = "d:/generated_dalle/" + filename_model.split(".")[0] + "_" + str(time.time()) + ".jpg"

        print("INF: writing to '%s'" % generated_image_filepath)
        with open(generated_image_filepath, "wb") as image_file:
            image_file.write(generated_image)  # write the image to the file
    exit(1)

if 0:
    # edit an image

    # create a mask
    width = 1024
    height = 1024
    mask = Image.new("RGBA", (width, height), (0, 0, 0, 1))  # create an opaque image mask

    # set the bottom half to be transparent
    for x in range(width):
        for y in range(height // 2, height):  # only loop over the bottom half of the mask
            # set alpha (A) to zero to turn pixel transparent
            alpha = 0
            mask.putpixel((x, y), (0, 0, 0, alpha))

    # save the mask
    mask_name = "bottom_half_mask.png"
    mask_filepath = os.path.join(image_dir, mask_name)
    mask.save(mask_filepath)

    # call the OpenAI API
    edit_response = openai.Image.create_edit(
        image=open(generated_image_filepath, "rb"),  # from the generation section
        mask=open(mask_filepath, "rb"),  # from right above
        prompt=prompt,  # from the generation section
        n=1,
        size="1024x1024",
        response_format="url",
    )

# print response
#~ print(edit_response)

#~ exit()


start_chat_log = '''Human: Hello, who are you?
AI: I am doing great. How can I help you today?
'''
chat_log = None
completion = openai.Completion()
def ask(question, chat_log=None):
    if chat_log is None:
        chat_log = start_chat_log
    prompt = f'{chat_log}Human: {question}\nAI:'
    response = completion.create(
        prompt=prompt, engine="curie", stop=['\nHuman'], temperature=0.9,
        top_p=1, frequency_penalty=0, presence_penalty=0.6, best_of=1,
        max_tokens=1000) # was 100
    print("DBG: choices: %s" % str(response.choices))
    answer = response.choices[0].text.strip()
    return answer
    
def append_interaction_to_chat_log(question, answer, chat_log=None):
    if chat_log is None:
        chat_log = start_chat_log
    return f'{chat_log}Human: {question}\nAI: {answer}\n'


def interact(q):
    global chat_log
    print("ques: %s" % q )
    answ=ask(q,chat_log)
    chat_log = append_interaction_to_chat_log(q ,answ, chat_log)
    print("answ: %s" % answ)
    return answ
    
def loopInteract():
    while 1:
        s = input("?")
        interact(s)

def autodialog():
    interact("hello !")
    interact("how are you?")
    interact("my name is alexandre, and you?")
    interact("what time is it?")
    interact("do you know me?")
    interact("what is my name?")
    if 0:
        interact("parle moi en francais!")
        interact("Mon fils s'appelle Rodrigue!")
        interact("c’est une énorme caractéristique des espagnols: il n’est pas courageux, il ne veut pas dire en face ce qu’il pense qui ne fera pas plaisir. Il attend que tu t’épuise, en réalité je t’ai plus blessé dans les actes. Comme un mec ou une nana qui n’a plus envie de vivre avec l’autre mais qui n’ose pas le dire. Evite la scène de la confession. Peur de mettre des mauvaises notes aux élèves. Achete la paix. Je sais qu’il ne pourra pas etre heureux. Il se rend compte qu’il se fait chier avec les espagnols, pas assez bête pour se contenter d’une vie tapas, vinho et cerveza.")
        interact("Je me souviens plus, ais je des enfants?")
        interact("que sais tu de Rodrigue?")
        interact("As tu manger des oeufs de boeuf?")
    interact("I have a son nammed Rodrigue!")
    interact("He's selfish, do you think it's a good person?")
    interact("He live in spain, and speaks a lot")
    interact("Today the wheather is great.")
    interact("Please tell me what you know about Rodrigue")
    interact("I have also a daughter nammed Natalia.")
    interact("Do you remember if i have children?")
    interact("Are you sure that's all?")
    interact("I feel alone, could you help me?")

def testUsingSocket():
        
    parser=argparse.ArgumentParser()
    parser.add_argument("port", help="server port", type=int, default="4000")


    args=parser.parse_args()

    port = args.port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(),port))
    while(True):
        msg=s.recv(1024)
        msg=msg.decode()
        if(len(msg)>0):
            if(msg=="exit"):
                break
            answ=ask(msg,chat_log)
            chat_log = append_interaction_to_chat_log(msg ,answ, chat_log)
            print(answ)
            s.send(answ.encode())
            
            
if __name__ == "__main__":
    #~ autodialog()
    #~ loopInteract()
    testUsingSocket()
      
  