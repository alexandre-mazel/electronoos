import requests

URL = "http://127.0.0.1:11434/api/generate"

payload = {
    "model": "mistral-small:22b",
    "prompt": "Hello world et toi je suis malade?.",
    "stream": False,
}

response = requests.post(URL, json=payload)
response.raise_for_status()
data = response.json()

print("\n===== RÉPONSE =====")
print(data["response"])

print("\n===== BENCH =====")

prompt_tokens = data.get("prompt_eval_count", 0)
prompt_duration = data.get("prompt_eval_duration", 0) / 1e9

eval_tokens = data.get("eval_count", 0)
eval_duration = data.get("eval_duration", 0) / 1e9

total_duration = data.get("total_duration", 0) / 1e9
load_duration = data.get("load_duration", 0) / 1e9

if prompt_duration > 0:
    print(f"Prompt      : {prompt_tokens} tokens")
    print(f"Prompt eval : {prompt_duration:.2f} s")
    print(f"Prompt speed: {prompt_tokens / prompt_duration:.2f} tok/s")

if eval_duration > 0:
    print(f"Génération  : {eval_tokens} tokens")
    print(f"Eval        : {eval_duration:.2f} s")
    print(f"Gen speed   : {eval_tokens / eval_duration:.2f} tok/s")

print(f"Chargement  : {load_duration:.2f} s")
print(f"Total       : {total_duration:.2f} s")
