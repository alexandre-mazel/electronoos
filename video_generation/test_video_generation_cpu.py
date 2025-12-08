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

"""
# error: ca doit prendre une image 

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
frames = result["frames"][0]  # liste de frames PIL (en general ~25 images)

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

print("Video generated :", output_file)
"""

"""
Text => Image => Video
Génère une image avec SD 1.5 (CPU compatible)

La passe à SVD pour générer la vidéo

Sauve la vidéo en MP4 avec ffmpeg

# install:
pip install diffusers transformers accelerate safetensors pillow
sudo apt install ffmpeg
"""

from diffusers import StableDiffusionPipeline, StableVideoDiffusionPipeline
import torch
from PIL import Image
import os
import subprocess

# --------------------------
# 1. Generate image from text
# --------------------------
txt2img = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float32
).to("cpu")

prompt = "a scenic mountain landscape, cinematic, detailed"
image = txt2img(prompt).images[0]
image.save("input_image.png")
print("Image générée : input_image.png")

# --------------------------
# 2. Generate video from image
# --------------------------
svd = StableVideoDiffusionPipeline.from_pretrained(
    "stabilityai/stable-video-diffusion-img2vid",
    torch_dtype=torch.float32
).to("cpu")

result = svd(image=image)
frames = result["frames"][0]  # liste de frames PIL

os.makedirs("frames", exist_ok=True)
for i, frame in enumerate(frames):
    frame.save(f"frames/frame_{i:04d}.png")

print(f"{len(frames)} frames générées dans ./frames/")

# --------------------------
# 3. Convert frames to MP4
# --------------------------
fps = 8
subprocess.run([
    "ffmpeg", "-y",
    "-framerate", str(fps),
    "-i", "frames/frame_%04d.png",
    "-pix_fmt", "yuv420p",
    "output.mp4",
])

print("Vidéo générée : output.mp4")
