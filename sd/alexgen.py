import torch # don't forget to use python3
from torch import autocast
from diffusers import StableDiffusionPipeline

import os
import cv2
import time

# faire une fois:
# import huggingface_hub
# huggingface_hub.login()
# et taper token

# lancer ce script depuis ../../stable... ? ou pas!


model_id = "CompVis/stable-diffusion-v1-1"
model_id = "CompVis/stable-diffusion-v1-4"
device = "cuda"


bLarge = 1
bLarge = 0

def generateWithSeed(prompt, seed = 123):
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        revision="fp16",
        torch_dtype=torch.float16,
        use_auth_token=True,
    ).to(device)
    
    from PIL import Image

    # memory problem:

    if 1:
        print("\n reglage memory pytorch:\n")

        #~ torch.no_grad()
        #~ os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "512"
        #~ print(os.environ["PYTORCH_CUDA_ALLOC_CONF"])
        #~ torch.max_split_size_mb = 512
    

    def image_grid(imgs, rows, cols):
        assert len(imgs) == rows*cols

        w, h = imgs[0].size
        grid = Image.new('RGB', size=(cols*w, rows*h))
        grid_w, grid_h = grid.size
        
        for i, img in enumerate(imgs):
            grid.paste(img, box=(i%cols*w, i//cols*h))
        return grid
        
    num_images = 4

    width = 512
    height = 512
    
    #~ if 1:
        #~ width = 256
        #~ height = 256
    
    generator = torch.Generator(device=device)

    latents = None
    seeds = []
    for _ in range(num_images):
        # Get a new random seed, store it and use it as the generator state
        seed = generator.seed()
        seeds.append(seed)
        generator = generator.manual_seed(seed)
        
        image_latents = torch.randn(
            (1, pipe.unet.in_channels, height // 8, width // 8),
            generator = generator,
            device = device
        )
        latents = image_latents if latents is None else torch.cat((latents, image_latents))
        
    # latents should have shape (4, 4, 64, 64) in this case
    latents.shape

    with torch.autocast("cuda"):
        images = pipe(
            [prompt] * num_images,
            guidance_scale=7.5,
            latents = latents,
        )["sample"]
    
    image_grid(images, 2, 2).show()
    
    seed=6363507785059417
    
    generator.manual_seed(seed)

    latents = torch.randn(
        (1, pipe.unet.in_channels, height // 8, width // 8),
        generator = generator,
        device = device
    )
    
    with torch.autocast("cuda"):
        image = pipe(
            [prompt] * 1,
            guidance_scale=7.5,
            latents = latents,
        )["sample"]
    
        image[0].show()
    
    

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

    prompt = "industrial age, (pocket watch), 35mm, sharp, high gloss, brass, gears wallpaper, cinematic atmosphere, panoramic"
    #~ prompt = "picture of dimly lit living room, minimalist furniture, vaulted ceiling, huge room, floor to ceiling window with an ocean view, nighttime"
    #~ prompt = "picture of a naked girl in a dimly lit living room, minimalist furniture, vaulted ceiling, huge room, floor to ceiling window with an ocean view, nighttime"


    #~ prompt = "a full page design of spaceship engine, black and bronze paper, intricate, highly detailed, epic, infographic, marginalia"

    #~ prompt ="alexandre mazel, diffuse lighting, fantasy, intricate elegant highly detailed lifelike photorealistic digital painting, artstation "

    #~ prompt = "zeus, diffuse lighting, mythology, intricate elegant highly detailed lifelike photorealistic realistic painting, long shot, studio lighting, by artgerm"

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
#~ generateWithSeed("Labrador in the style of Vermeer")