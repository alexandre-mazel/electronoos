import torch # don't forget to use python3
from torch import autocast
from diffusers import StableDiffusionPipeline

import os
import cv2
import time

model_id = "CompVis/stable-diffusion-v1-1"
device = "cuda"


bLarge = 1
bLarge = 0

def generateImg():

    if bLarge:
        pipe = StableDiffusionPipeline.from_pretrained(model_id)
    else:
        pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
        
    pipe = pipe.to(device)
    pipe.safety_checker = lambda images, clip_input: (images, False)

    #~ prompt = "a photo of an astronaut riding a horse on mars"
    #~ prompt = "portrait of a girl"
    #~ prompt = "a beautiful and naked red-head girl with high checkbones smiling at the camera at work"
    #~ prompt = "portrait of a young cyberpunk woman"
    # https://www.stable-diffusion-france.fr/prompt-helper.php
    #~ prompt = "a woman  painting,  photorealistic vintage, art by ,  Alphonse Mucha Rembrandt, in the style of ,  Lovecraft,  natural lighting, blue eyes,  ultra realistic trending on artstation fine details complex picture Octane reflections"
    #~ prompt = "a woman  painting,  photorealistic vintage, art by ,  Alphonse Mucha Goya, in the style of ,  Lovecraft,  natural lighting candlelight, blue eyes,  4k trending on artstation very detailed intricate scenery post-processing fine details reflections ultra realistic"
    #~ prompt = "a woman  painting,  photorealistic vintage, art by ,  Alphonse Mucha Jose de ribeira, in the style of ,  Lovecraft,  natural lighting candlelight, blue eyes,  4k trending on artstation very detailed intricate scenery post-processing fine details reflections ultra realistic"
    #~ prompt = "illustration of a handsome! ! man with long black curly hair + tan skin + anchor goatee, guitar | wearing a cowboy hat | art by hirohiko araki & jean giraud & artgerm & jack kirby | artstation, character design, concept art, full body, digital painting | intricate, high detail, smooth, sharp focus "
    #~ prompt = "a realistic elven forest [moss]" # remove moss (not working)
    #~ prompt = "a realistic elven forest (moss)-2" # remove moss (not working) => use negative_prompt
    #~ prompt = "a realistic elven forest"

    #~ prompt = "industrial age, (pocket watch), 35mm, sharp, high gloss, brass, gears wallpaper, cinematic atmosphere, panoramic"
    #~ prompt = "picture of dimly lit living room, minimalist furniture, vaulted ceiling, huge room, floor to ceiling window with an ocean view, nighttime"


    #~ prompt = "a full page design of spaceship engine, black and bronze paper, intricate, highly detailed, epic, infographic, marginalia"

    #~ prompt ="alexandre mazel, diffuse lighting, fantasy, intricate elegant highly detailed lifelike photorealistic digital painting, artstation "

    prompt = "zeus, diffuse lighting, mythology, intricate elegant highly detailed lifelike photorealistic realistic painting, long shot, studio lighting, by artgerm"

    neg = ""

    neg = "disfigured, bad anatomy, extra legs, extra arms, extra fingers, poorly drawn hands, poorly drawn feet, disfigured, tiling, bad art, deformed, mutated"
    #~ neg += "out of frame, "

    #~ pipe.seed = 2229135949491605 # not working need to generate latents ourselves

    with autocast("cuda"):
        for i in range(4):
            print("Generating...")
            if bLarge:
                image = pipe(prompt)["sample"][0]  
            else:
                ret = pipe(prompt, negative_prompt=neg, guidance_scale=7.5) # champion1: 9.9 it/s
                #~ print("dir: " + str(dir(ret)))
                image = ret["images"][0]  
                #~ print("image: " + str(image))
            #~ image.show()
            
            fn = prompt.replace(" ", "_")[:80] + '__' + str(time.time()) + ".png"
            fn = os.path.expanduser("~/generated/" + fn)
            image.save(fn)
            
            print("INF: showing '%s'" % fn)
            im = cv2.imread(fn)
            win_name = "generated_%d" % i
            cv2.imshow(win_name,im)
            cv2.moveWindow(win_name, (i%4)*256, (i//4)*256 )
            cv2.waitKey(1000)
            
    cv2.waitKey(0)
    
generateImg()