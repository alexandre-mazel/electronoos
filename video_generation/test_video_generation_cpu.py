"""
tester sur azure:
~/dev$ python3 -m venv video_generation
source video_generation/bin/activate
pip install diffusers transformers accelerate
"""

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
"""

from diffusers import StableVideoDiffusionPipeline
import torch
from PIL import Image
import os
import subprocess

# ----- 1. Load model -----
pipe = StableVideoDiffusionPipeline.from_pretrained(
    "stabilityai/stable-video-diffusion-img2vid",
    torch_dtype=torch.float32
)
pipe.to("cpu")  # CPU mode (lent mais fonctionne)

# ----- 2. Generate frames -----
prompt = "a scenic mountain landscape"
result = pipe(prompt)
frames = result["frames"][0]  # liste de frames PIL (en général ~25 images)

# ----- 3. Save frames as images -----
os.makedirs("frames", exist_ok=True)

for i, frame in enumerate(frames):
    frame.save(f"frames/frame_{i:04d}.png")

print(f"{len(frames)} frames saved in ./frames/")

# ----- 4. Encode MP4 with FFmpeg -----
output_file = "output.mp4"
fps = 8  # Stable Video Diffusion sort souvent 5-12 fps

subprocess.run([
    "ffmpeg",
    "-y",
    "-framerate", str(fps),
    "-i", "frames/frame_%04d.png",
    "-pix_fmt", "yuv420p",   # compatible avec tous les lecteurs
    output_file
])

print("Vidéo générée :", output_file)