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
    init_img = Image.open("IMG_9404.CR2_small.jpg", mode='r')
    #~ init_img = init_img.resize((768, 512))
    init_img = init_img.resize((512, 512))
    #~ init_img.show()

prompt = "A fantasy landscape, trending on artstation"
prompt = "A repair guy, trending on artstation"
prompt = "A repair guy, trending on artstation diffuse lighting, fantasy, intricate elegant highly detailed lifelike photorealistic digital painting, artstation"


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
        strength=0.75
        strength=0.4+0.05*i
        image = pipe(prompt=prompt, init_image=init_img, strength=strength, guidance_scale=7.5).images[0]
        import alexgen
        alexgen.save_and_show_pil_image(image,prompt,i)
        
import cv2
cv2.waitKey(0)