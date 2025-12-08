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
width = height = 512
im_resized = img_prompt.resize((width, height))

    
#~ print( "starting to generate: ", prompt )
frames = pipe(im_resized)["frames"]

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

print("Video generated:", output_file)