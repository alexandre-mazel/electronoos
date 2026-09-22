#!/usr/bin/env python3

"""
Change one face in a tableau containing many face with another one passed as a ref.

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

"""

import argparse
import torch

from PIL import Image
from diffusers import QwenImageEditPlusPipeline


MODEL = "ovedrive/Qwen-Image-Edit-2509-4bit"


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "scene",
        help="Image principale contenant les personnages"
    )

    parser.add_argument(
        "face",
        help="Image contenant le visage de référence"
    )

    parser.add_argument(
        "prompt",
        help="Instruction d'édition"
    )

    parser.add_argument(
        "-o",
        "--output",
        default="result.png",
        help="Image de sortie"
    )

    parser.add_argument(
        "--steps",
        type=int,
        default=20
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=12345
    )

    args = parser.parse_args()

    print("Loading model...")

    pipe = QwenImageEditPlusPipeline.from_pretrained(
        MODEL,
        torch_dtype=torch.bfloat16,
    )

    # Important pour une RTX 3080 10 GB :
    # les différentes parties du modèle sont déplacées
    # automatiquement entre GPU et RAM.
    pipe.enable_model_cpu_offload()

    pipe.set_progress_bar_config(disable=False)

    scene = Image.open(args.scene).convert("RGB")
    face = Image.open(args.face).convert("RGB")

    generator = torch.Generator(device="cpu").manual_seed(args.seed)

    print("Generating...")

    result = pipe(
        image=[scene, face],
        prompt=args.prompt,
        num_inference_steps=args.steps,
        generator=generator,
    ).images[0]

    result.save(args.output)

    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()