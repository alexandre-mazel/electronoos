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
ollama_ps()

strModel = "llama3.2:1B"
bench_ollama( strModel, prompt, nbr_test )
ollama_ps()

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

corto@DESKTOP-MOTSL8C C:\Users\corto\dev\git\electronoos\chatola>python test_ollama_perf.py

# Benchmark Ollama — moondream:latest
# 5 appels, generate: 'Hello world, comment ca va et toi je suis malade ?.'

#1 | total=0.149s | prompt=0.007s/23 tok | eval=0.114s/18 tok | speed=157.86 tok/s
#2 | total=0.156s | prompt=0.009s/23 tok | eval=0.111s/18 tok | speed=161.80 tok/s
#3 | total=0.152s | prompt=0.007s/23 tok | eval=0.109s/18 tok | speed=165.29 tok/s
#4 | total=0.150s | prompt=0.007s/23 tok | eval=0.109s/18 tok | speed=164.64 tok/s
#5 | total=0.134s | prompt=0.007s/23 tok | eval=0.107s/18 tok | speed=168.88 tok/s

--- Résultats ---
Total       | min=0.134 | max=0.156 | avg=0.148 s
Prompt      | min=0.007 | max=0.009 | avg=0.007 s
Tokens eval | min=18.000 | max=18.000 | avg=18.000
Eval        | min=0.107 | max=0.114 | avg=0.110 s
Vitesse     | min=157.86 | max=168.88 | avg=163.69 tok/s


# Benchmark Ollama — llama3.2:1B
# 5 appels, generate: 'Hello world, comment ca va et toi je suis malade ?.'

#1 | total=0.964s | prompt=0.009s/38 tok | eval=0.924s/98 tok | speed=106.09 tok/s
#2 | total=0.979s | prompt=0.009s/38 tok | eval=0.940s/98 tok | speed=104.27 tok/s
#3 | total=0.969s | prompt=0.010s/38 tok | eval=0.923s/98 tok | speed=106.14 tok/s
#4 | total=0.978s | prompt=0.010s/38 tok | eval=0.934s/98 tok | speed=104.98 tok/s
#5 | total=0.984s | prompt=0.010s/38 tok | eval=0.942s/98 tok | speed=104.09 tok/s

--- Résultats ---
Total       | min=0.964 | max=0.984 | avg=0.975 s
Prompt      | min=0.009 | max=0.010 | avg=0.010 s
Tokens eval | min=98.000 | max=98.000 | avg=98.000
Eval        | min=0.923 | max=0.942 | avg=0.932 s
Vitesse     | min=104.09 | max=106.14 | avg=105.11 tok/s


# Benchmark Ollama — mistral-small:22B
# 5 appels, generate: 'Hello world, comment ca va et toi je suis malade ?.'

#1 | total=8.124s | prompt=0.234s/21 tok | eval=7.859s/35 tok | speed=4.45 tok/s
#2 | total=8.034s | prompt=0.232s/21 tok | eval=7.769s/35 tok | speed=4.50 tok/s
#3 | total=8.005s | prompt=0.231s/21 tok | eval=7.746s/35 tok | speed=4.52 tok/s
#4 | total=7.984s | prompt=0.232s/21 tok | eval=7.746s/35 tok | speed=4.52 tok/s
#5 | total=7.997s | prompt=0.233s/21 tok | eval=7.758s/35 tok | speed=4.51 tok/s

--- Résultats ---
Total       | min=7.984 | max=8.124 | avg=8.029 s
Prompt      | min=0.231 | max=0.234 | avg=0.232 s
Tokens eval | min=35.000 | max=35.000 | avg=35.000
Eval        | min=7.746 | max=7.859 | avg=7.776 s
Vitesse     | min=4.45 | max=4.52 | avg=4.50 tok/s


--- Ollama PS ---
NAME                 ID              SIZE     PROCESSOR          CONTEXT    UNTIL
mistral-small:22B    d095cd553b04    13 GB    51%/49% CPU/GPU    4096       4 minutes from now

--- Matériel ---
CPU : Intel(R) Core(TM) Ultra 7 265KF
GPU : NVIDIA GeForce GTX 1070

corto@DESKTOP-MOTSL8C C:\Users\corto\dev\git\electronoos\chatola>







"""