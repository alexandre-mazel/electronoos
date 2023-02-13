import inspect
import warnings
from typing import List, Optional, Union

import torch
from torch import autocast
from tqdm.auto import tqdm

bCensored = 0


if 1:
    print("\n reglage memory pytorch:\n")

    #~ torch.no_grad()
    #~ os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "512"
    #~ print(os.environ["PYTORCH_CUDA_ALLOC_CONF"])
    torch.max_split_size_mb = 512

from diffusers import StableDiffusionImg2ImgPipeline

device = "cuda"
model_path = "CompVis/stable-diffusion-v1-1"
#~ model_path = "CompVis/stable-diffusion-v1-4"

pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
    model_path,
    revision="fp16", 
    torch_dtype=torch.float16,
    use_auth_token=True
)
pipe = pipe.to(device)
if not bCensored: pipe.safety_checker = lambda images, clip_input: (images, False)

import requests
from io import BytesIO
from PIL import Image

if 0:
    url = "https://raw.githubusercontent.com/CompVis/stable-diffusion/main/assets/stable-samples/img2img/sketch-mountains-input.jpg"

    response = requests.get(url)
    init_img = Image.open(BytesIO(response.content)).convert("RGB")
    init_img = init_img.resize((768, 512))
else:
    #~ init_img = Image.open("IMG_9404.CR2_small.jpg", mode='r')
    init_img = Image.open("corto_gaia_bateau.JPG", mode='r')
    init_img = Image.open("corto_gaia_elsa_a_nissan.JPG", mode='r')
    #~ init_img = Image.open("sdb_bech.jpg", mode='r')
    #~ init_img = init_img.resize((768, 512))
    init_img = init_img.resize((512, 512))
    #~ init_img.show()

prompt = "A fantasy landscape, trending on artstation"
prompt = "A repair guy, trending on artstation"
#~ prompt = "A repair guy, trending on artstation diffuse lighting, fantasy, intricate elegant highly detailed lifelike photorealistic digital painting, artstation"
#~ prompt = "A repair guy, photorealistic vintage, art by ,  Alphonse Mucha Jose de ribeira, in the style of ,  Lovecraft,  natural lighting candlelight, blue eyes,  4k trending on artstation very detailed intricate scenery post-processing fine details reflections ultra realistic"

prompt = "two kids on a boat, photorealistic vintage, art by ,  Alphonse Mucha Jose de ribeira, in the style of ,  Lovecraft,  natural lighting candlelight, blue eyes,  4k trending on artstation very detailed intricate scenery post-processing fine details reflections ultra realistic"
prompt = "two kids on a boat drawn by a children"
prompt = "two kids on a boat"
prompt = "painting of two kids on a boat"
prompt = "a family"

#~ prompt  += " diffuse lighting, mythology, intricate elegant highly detailed lifelike photorealistic realistic painting, long shot, studio lighting, by artgerm"
#~ prompt += " photorealistic vintage, art by ,  van gogh, in the style of ,  Lovecraft,  natural lighting candlelight,  4k trending on artstation very detailed intricate scenery post-processing fine details reflections ultra realistic"
#~ prompt += " gorgeous valkyrie| (detailed face with war paint)| ((black eyeliner))| dark background| hyperrealistic| highly detailed| intricate| cinematic lighting| greyscale| Midjourney style"
#~ prompt += " Pixar style little girl, blonde, 4k, unreal engine, octane render photorealistic by cosmicwonder, hdr, photography by cosmicwonder, high definition, symmetrical face, volumetric lighting, dusty haze, photo, 24mm, DSLR, high quality, ultra realistic, kids park "
#~ prompt += " Pixar style 4k, unreal engine, octane render photorealistic by cosmicwonder, hdr, photography by cosmicwonder, high definition, symmetrical face, volumetric lighting, dusty haze, photo, 24mm, DSLR, high quality, ultra realistic, kids park "
prompt += "  at a tropical beach, medium shot, waist up, studio Ghibli, Pixar and Disney animation, sharp, very detailed, high resolution, Rendered in Unreal Engine 5, anime key art by Greg Rutkowski, Bloom, dramatic lighting"

neg = ""
neg = " disfigured, bad anatomy, extra legs, extra arms, extra fingers, poorly drawn hands, poorly drawn feet, disfigured, tiling, bad art, deformed, mutated"

neg += ", hair" # not working

generator = torch.Generator(device=device)

if 1:
    generator.manual_seed(1024)
    seed = generator.seed()
else:
    seed = 6363507785059417
    
    generator.manual_seed(seed)

    height = 512
    width = 512
    latents = torch.randn(
        (1, pipe.unet.in_channels, height // 8, width // 8),
        generator = generator,
        device = device
    )
print( "INF: seed: %s" % seed )
with autocast("cuda"):
    for i in range(10):
        
        strength = 0.75
        strength = 0.5
        strength=0.2+0.05*i
        print("INF: strength: %.2f" % strength )
        
        guidance_scale = 7.5
        #~ guidance_scale = 1+i
        #~ guidance_scale = 15
        #~ guidance_scale = 5
        print("INF: guidance_scale: %.2f" % guidance_scale )
        image = pipe(prompt=prompt, negative_prompt=neg, init_image=init_img, strength=strength, guidance_scale=guidance_scale).images[0]
        import alexgen
        alexgen.save_and_show_pil_image(image,prompt,i)
        
import cv2
cv2.waitKey(0)