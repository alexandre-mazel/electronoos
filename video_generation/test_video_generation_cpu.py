"""
tester sur azure:
~/dev$ python3 -m venv video_generation
source video_generation/bin/activate
pip install diffusers transformers accelerate
"""

from diffusers import StableVideoDiffusionPipeline
import torch

pipe = StableVideoDiffusionPipeline.from_pretrained(
    "stabilityai/stable-video-diffusion-img2vid",
    torch_dtype=torch.float32
)
pipe = pipe.to("cpu")

prompt = "a scenic mountain landscape"
print( "starting to generate: ", prompt )
frames = pipe(prompt)["frames"]