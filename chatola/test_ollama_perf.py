
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import requests
import statistics

URL = "http://127.0.0.1:11434/api/generate"
MODEL = "mistral-small:22B"
MODEL = "llama3.2:1B"
PROMPT = "Hello world, comment ca va et toi je suis malade ?."
N = 5

durations = []
eval_durations = []
prompt_eval_durations = []
eval_counts = []
prompt_eval_counts = []
token_rates = []

print(f"Benchmark Ollama — {MODEL}")
print(f"{N} appels, stream=false\n")

for i in range(1, N + 1):
    start = time.perf_counter()

    response = requests.post(
        URL,
        json={
            "model": MODEL,
            "prompt": PROMPT,
            "stream": False,
            "options": {
                "temperature": 0,
                "seed": 42,
            },            
        },
        timeout=600,
    )

    end = time.perf_counter()

    response.raise_for_status()
    data = response.json()

    total_time = end - start

    eval_count = data.get("eval_count", 0)
    eval_duration_ns = data.get("eval_duration", 0)
    prompt_eval_count = data.get("prompt_eval_count", 0)
    prompt_eval_duration_ns = data.get("prompt_eval_duration", 0)

    eval_duration = eval_duration_ns / 1e9
    prompt_eval_duration = prompt_eval_duration_ns / 1e9

    tok_s = (
        eval_count / eval_duration
        if eval_duration > 0
        else 0
    )

    durations.append(total_time)
    eval_durations.append(eval_duration)
    prompt_eval_durations.append(prompt_eval_duration)
    eval_counts.append(eval_count)
    prompt_eval_counts.append(prompt_eval_count)
    token_rates.append(tok_s)

    print(
        f"#{i} | "
        f"total={total_time:.3f}s | "
        f"prompt={prompt_eval_duration:.3f}s/{prompt_eval_count} tok | "
        f"eval={eval_duration:.3f}s/{eval_count} tok | "
        f"speed={tok_s:.2f} tok/s"
    )

print("\n--- Résultats ---")

def stats(values):
    return (
        f"min={min(values):.3f} | "
        f"max={max(values):.3f} | "
        f"avg={statistics.mean(values):.3f}"
    )
    

      
def ollama_ps():
    import subprocess

    print("\n--- Ollama PS ---")

    try:
        result = subprocess.run(
            ["ollama", "ps"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )

        print(result.stdout.strip())

    except Exception as e:
        print(f"Impossible d'exécuter 'ollama ps' : {e}")	
        
def print_hardware():
    import subprocess

    print("\n--- Matériel ---")

    try:
        cpu = subprocess.run(
            ["cmd", "/c", "wmic cpu get name /value"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        ).stdout.strip()

        gpu = subprocess.run(
            ["cmd", "/c", "wmic path win32_VideoController get name /value"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        ).stdout.strip()

        # Extraction des valeurs
        cpu_name = next(
            (line.split("=", 1)[1].strip()
             for line in cpu.splitlines()
             if line.startswith("Name=")),
            "Inconnu"
        )

        gpu_names = [
            line.split("=", 1)[1].strip()
            for line in gpu.splitlines()
            if line.startswith("Name=")
        ]

        print(f"CPU : {cpu_name}")

        for gpu_name in gpu_names:
            print(f"GPU : {gpu_name}")

    except Exception as e:
        print(f"Erreur lors de la détection du matériel : {e}")
        
        
        
print(f"Total       | {stats(durations)} s")
print(f"Prompt      | {stats(prompt_eval_durations)} s")
print(f"Tokens eval | {stats(eval_counts)}")
print(f"Eval        | {stats(eval_durations)} s")
print(f"Vitesse     | min={min(token_rates):.2f} | "
      f"max={max(token_rates):.2f} | "
      f"avg={statistics.mean(token_rates):.2f} tok/s")
      
ollama_ps()
print_hardware()


"""
        
*** Ordi Corto:

Benchmark Ollama — mistral-small:22B
5 appels, stream=false

#1 | total=12.513s | prompt=0.359s/21 tok | eval=12.138s/35 tok | speed=2.88 tok/s
#2 | total=12.521s | prompt=0.360s/21 tok | eval=12.136s/35 tok | speed=2.88 tok/s
#3 | total=12.528s | prompt=0.360s/21 tok | eval=12.139s/35 tok | speed=2.88 tok/s
#4 | total=12.532s | prompt=0.360s/21 tok | eval=12.148s/35 tok | speed=2.88 tok/s
#5 | total=12.514s | prompt=0.359s/21 tok | eval=12.130s/35 tok | speed=2.89 tok/s

--- Résultats ---
Total       | min=12.513 | max=12.532 | avg=12.522 s
Prompt      | min=0.359 | max=0.360 | avg=0.360 s
Tokens eval | min=35.000 | max=35.000 | avg=35.000
Eval        | min=12.130 | max=12.148 | avg=12.138 s
Vitesse     | min=2.88 | max=2.89 | avg=2.88 tok/s

--- Ollama PS ---
NAME                 ID              SIZE     PROCESSOR          CONTEXT    UNTIL              
mistral-small:22B    d095cd553b04    13 GB    51%/49% CPU/GPU    4096       4 minutes from now

--- Matériel ---
CPU : Intel(R) Core(TM) Ultra 7 265KF
GPU : NVIDIA GeForce GTX 1070







"""