# Reminder: use venv from ~/dev/llama_env


if 0:
    # exemple depuis https://medium.com/@tachegnonchristiankpanou/using-llama-3-locally-on-your-computer-a-step-by-step-guide-5c85e3f71bea
    # mais je ne trouve pas llamap-api
    import llama_api # pip install llama-api
    from transformers import AutoModelForCausalLM, AutoTokenizer
    # Load the pre-trained LLaMA 3 model
    model = AutoModelForCausalLM.from_pretrained("llama_v3_model")
    # Load the tokenizer for the LLaMA 3 model
    tokenizer = AutoTokenizer.from_pretrained("llama_v3_model")


import transformers
import torch
from transformers import AutoTokenizer

model = "meta-llama/Meta-Llama-3.2-3B"
model = "Llama3.2-1B"
model = "/home/na/.llama/checkpoints/Llama3.2-1B/"

tokenizer = AutoTokenizer.from_pretrained(model)

pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    torch_dtype=torch.float16,
    device_map="auto",
)

sequences = pipeline(
    'I have tomatoes, basil and cheese at home. What can I cook for dinner?\n',
    do_sample=True,
    top_k=10,
    num_return_sequences=1,
    eos_token_id=tokenizer.eos_token_id,
    truncation = True,
    max_length=400,
)

for seq in sequences:
    print(f"Result: {seq['generated_text']}")