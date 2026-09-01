
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import requests
import statistics

OLLAMA_URL = "http://127.0.0.1:11434/"


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
       

def ollama_model_exists(model_name):
    try:
        response = requests.get(
            f"{OLLAMA_URL}api/tags",
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

        models = data.get("models", [])

        ret = any(
            model.get("name").upper() == model_name.upper()
            for model in models
        )
        
        if not ret:
            print( "\nDBG: ollama_model_exists: current existing model:" )
            for model in models:
                print( "    - ", model.get("name") )
            print("")
                
        return ret

    except requests.RequestException as e:
        print(f"Ollama inaccessible : {e}")
        return False


def bench_ollama( strModel, strPrompt, nbr_test = 5 ):

    durations = []
    eval_durations = []
    prompt_eval_durations = []
    eval_counts = []
    prompt_eval_counts = []
    token_rates = []


    #~ print( "(preloading...)" )
    strUrl = f"{OLLAMA_URL}api/generate"
    dOptions = { "temperature": 0, "seed": 42 }
    dJson = { "model": strModel, "prompt": strPrompt, "stream": False, "options": dOptions}
    response = requests.post( strUrl, json=dJson, timeout=600 )
    
    print("")
    print(f"# Benchmark Ollama — {strModel}")
    print(f"# {nbr_test} appels, generate: '{prompt}'")
    
    if not ollama_model_exists(strModel):
        print( "WRN: This model isn't present:", strModel )
        print("")
        return
        
    print("")
    
    
    # un petit coup pour charger le modele:

    for i in range(1, nbr_test + 1):
        start = time.perf_counter()

        response = requests.post( strUrl, json=dJson, timeout=600 )

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
            
    print(f"Total       | {stats(durations)} s")
    print(f"Prompt      | {stats(prompt_eval_durations)} s")
    print(f"Tokens eval | {stats(eval_counts)}")
    print(f"Eval        | {stats(eval_durations)} s")
    print(f"Vitesse     | min={min(token_rates):.2f} | "
          f"max={max(token_rates):.2f} | "
          f"avg={statistics.mean(token_rates):.2f} tok/s")
    print( "" )
          
          

prompt = "Hello world, comment ca va et toi je suis malade ?."
nbr_test = 1
nbr_test = 5

strModel = "moondream:latest"
bench_ollama( strModel, prompt, nbr_test )

strModel = "llama3.2:1B"
bench_ollama( strModel, prompt, nbr_test )

strModel = "mistral-small:22B"
bench_ollama( strModel, prompt, nbr_test )


ollama_ps()
print_hardware()


"""

*** MS Tab7

# Benchmark Ollama — moondream:latest
# 5 appels, generate: 'Hello world, comment ca va et toi je suis malade ?.'

#1 | total=0.913s | prompt=0.068s/23 tok | eval=0.798s/18 tok | speed=22.57 tok/s
#2 | total=0.924s | prompt=0.052s/23 tok | eval=0.847s/18 tok | speed=21.24 tok/s
#3 | total=0.915s | prompt=0.056s/23 tok | eval=0.827s/18 tok | speed=21.76 tok/s
#4 | total=0.907s | prompt=0.056s/23 tok | eval=0.831s/18 tok | speed=21.65 tok/s
#5 | total=0.951s | prompt=0.070s/23 tok | eval=0.859s/18 tok | speed=20.95 tok/s

--- Résultats ---
Total       | min=0.907 | max=0.951 | avg=0.922 s
Prompt      | min=0.052 | max=0.070 | avg=0.060 s
Tokens eval | min=18.000 | max=18.000 | avg=18.000
Eval        | min=0.798 | max=0.859 | avg=0.832 s
Vitesse     | min=20.95 | max=22.57 | avg=21.64 tok/s


# Benchmark Ollama — llama3.2:1b
# 5 appels, generate: 'Hello world, comment ca va et toi je suis malade ?.'

#1 | total=5.623s | prompt=0.090s/38 tok | eval=5.501s/75 tok | speed=13.63 tok/s
#2 | total=6.118s | prompt=0.083s/38 tok | eval=6.004s/75 tok | speed=12.49 tok/s
#3 | total=5.652s | prompt=0.090s/38 tok | eval=5.534s/75 tok | speed=13.55 tok/s
#4 | total=5.634s | prompt=0.072s/38 tok | eval=5.535s/75 tok | speed=13.55 tok/s
#5 | total=5.942s | prompt=0.100s/38 tok | eval=5.811s/75 tok | speed=12.91 tok/s

--- Résultats ---
Total       | min=5.623 | max=6.118 | avg=5.794 s
Prompt      | min=0.072 | max=0.100 | avg=0.087 s
Tokens eval | min=75.000 | max=75.000 | avg=75.000
Eval        | min=5.501 | max=6.004 | avg=5.677 s
Vitesse     | min=12.49 | max=13.63 | avg=13.23 tok/s
d

# Benchmark Ollama — mistral-small:22b
# 5 appels, generate: 'Hello world, comment ca va et toi je suis malade ?.'

DBG: ollama_model_exists: current existing model:
    -  llama3.2:1b
    -  moondream:latest

WRN: This model isn't present: mistral-small:22b


--- Ollama PS ---
NAME                ID              SIZE      PROCESSOR    CONTEXT    UNTIL              
llama3.2:1b         baf6a787fdff    1.5 GB    100% CPU     4096       4 minutes from now    
moondream:latest    55fc3abd3867    1.3 GB    100% CPU     2048       4 minutes from now

--- Matériel ---
CPU : Intel(R) Core(TM) i7-1065G7 CPU @ 1.30GHz
GPU : Intel(R) Iris(R) Plus Graphics
        
*** Ordi Corto:

Ollama a lancer ainsi depuis cmd:
set CUDA_VISIBLE_DEVICES=-1 && set OLLAMA_VULKAN=1 && ollama serve

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