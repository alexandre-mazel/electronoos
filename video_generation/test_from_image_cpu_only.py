from diffusers import StableVideoDiffusionPipeline
import torch

pipe = StableVideoDiffusionPipeline.from_pretrained(
    "stabilityai/stable-video-diffusion-img2vid",
    torch_dtype=torch.float32
)
pipe = pipe.to("cpu")

img_filename = "Rose high res.png"
from PIL import Image
img_prompt = Image.open(img_filename)
    
#~ print( "starting to generate: ", prompt )
frames = pipe(img_prompt)["frames"]