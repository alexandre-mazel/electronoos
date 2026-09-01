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
        print(f"Impossible d'executer 'ollama ps' : {e}")	
        
def print_hardware():
    import subprocess

    print("\n--- Materiel ---")

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
        print(f"Erreur lors de la detection du materiel : {e}")
       

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
    print(f"# Benchmark Ollama - {strModel}")
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

    print("\n--- Results ---")
            
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

*** Ordi Corto:

Ollama a lancer ainsi depuis cmd:
set CUDA_VISIBLE_DEVICES=-1 && set OLLAMA_VULKAN=1 && ollama serve


"""