# -*- coding: utf-8 -*-

import time
import requests
import statistics

OLLAMA_ADDR = "http://127.0.0.1"

def test_ollama_port( addr, port ):
    import urllib3
    url = "%s:%s/api/tags" % (addr, port)
    print( "DBG: test_ollama_port: testing url: '%s'" % url )
    try:
        r = requests.get( url )
        #~ print(r.status_code)
        data = r.json()
        #~ print( data )
        if "models" in data:
            return True
    except (ConnectionRefusedError, urllib3.exceptions.NewConnectionError,requests.exceptions.ConnectionError):
        pass
    return False

def find_ollama_port(addr):
    for port in [11434, 11435]:
        if test_ollama_port( addr,port ):
            print( "INF: find_ollama_port: find ollama on %s:%s" % (addr,port) )
            return port
    return -1

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
        
def print_hardware_win():
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
        
def print_hardware_linux():
    import subprocess

    print("\n--- Materiel ---")

    try:
        cpu = subprocess.check_output(
            ["lscpu"],
            text=True
        )

        cpu_name = next(
            (
                line.split(":", 1)[1].strip()
                for line in cpu.splitlines()
                if line.startswith("Model name:")
            ),
            "Inconnu"
        )

        print(f"CPU : {cpu_name}")

        gpu = subprocess.check_output(
            ["lspci"],
            text=True
        )

        for line in gpu.splitlines():
            if any(x in line for x in (
                "VGA compatible controller",
                "3D controller",
                "Display controller"
            )):
                print(f"GPU : {line.split(':', 2)[-1].strip()}")

    except Exception as e:
        print(f"Erreur lors de la detection du materiel : {e}")
        
def print_hardware():
    import platform
    bWindows = "windows" in platform.system().lower()
    if bWindows:
        return print_hardware_win()
    return print_hardware_linux()

       

def ollama_model_exists(model_name,addr,port):
    
    strOllamaUrl = addr + ":" + str(port) + "/"
    
    try:
        response = requests.get(
            f"{strOllamaUrl}api/tags",
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


def bench_ollama( strModel, strPrompt, nbr_test, addr, port ):
    
    strOllamaUrl = addr + ":" + str(port) + "/"

    durations = []
    eval_durations = []
    prompt_eval_durations = []
    eval_counts = []
    prompt_eval_counts = []
    token_rates = []


    #~ print( "(preloading...)" )
    strUrl = f"{strOllamaUrl}api/generate"
    dOptions = { "temperature": 0, "seed": 42,"num_ctx": 4096 }
    dJson = { "model": strModel, "prompt": strPrompt, "stream": False, "options": dOptions}
    response = requests.post( strUrl, json=dJson, timeout=600 )
    
    print("")
    print(f"# Benchmark Ollama - {strModel}")
    print(f"# {nbr_test} appels, generate: '{prompt}'")
    
    if not ollama_model_exists(strModel,addr, port):
        print( "WRN: This model isn't present:", strModel )
        print("")
        return -1
        
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
    
    avg_total = statistics.mean(durations)
    return avg_total
          

avg_summary = []
ollama_port = find_ollama_port(OLLAMA_ADDR)

prompt = "Hello world, comment ca va et toi je suis malade ?."
nbr_test = 1
nbr_test = 5

strModel = "moondream:latest"
ret = bench_ollama( strModel, prompt, nbr_test, OLLAMA_ADDR, ollama_port )
avg_summary.append( ret )
if ret != -1:
    ollama_ps()

strModel = "llama3.2:1B"
ret = bench_ollama( strModel, prompt, nbr_test, OLLAMA_ADDR, ollama_port )
avg_summary.append( ret )
if ret != -1:
    ollama_ps()

strModel = "mistral-small:22B"
ret = bench_ollama( strModel, prompt, nbr_test, OLLAMA_ADDR, ollama_port )
avg_summary.append( ret )
if ret != -1:
    ollama_ps()
    
print( "Summary: ", end = "" )
for a in avg_summary:
    print( "%.4f" % a, end = "" )
print( "" )

print_hardware()

"""

*** MS Tab7

# Benchmark Ollama - moondream:latest
# 5 appels, generate: 'Hello world, comment ca va et toi je suis malade ?.'

#1 | total=0.892s | prompt=0.055s/23 tok | eval=0.815s/18 tok | speed=22.08 tok/s
#2 | total=0.971s | prompt=0.065s/23 tok | eval=0.880s/18 tok | speed=20.45 tok/s
#3 | total=0.949s | prompt=0.062s/23 tok | eval=0.868s/18 tok | speed=20.74 tok/s
#4 | total=0.943s | prompt=0.057s/23 tok | eval=0.856s/18 tok | speed=21.03 tok/s
#5 | total=0.960s | prompt=0.052s/23 tok | eval=0.881s/18 tok | speed=20.43 tok/s

--- Results ---
Total       | min=0.892 | max=0.971 | avg=0.943 s
Prompt      | min=0.052 | max=0.065 | avg=0.058 s
Tokens eval | min=18.000 | max=18.000 | avg=18.000
Eval        | min=0.815 | max=0.881 | avg=0.860 s
Vitesse     | min=20.43 | max=22.08 | avg=20.94 tok/s


--- Ollama PS ---
NAME                ID              SIZE      PROCESSOR    CONTEXT    UNTIL              
moondream:latest    55fc3abd3867    1.3 GB    100% CPU     2048       4 minutes from now    
llama3.2:1b         baf6a787fdff    1.5 GB    100% CPU     4096       4 minutes from now

# Benchmark Ollama - llama3.2:1B
# 5 appels, generate: 'Hello world, comment ca va et toi je suis malade ?.'

#1 | total=5.644s | prompt=0.072s/38 tok | eval=5.543s/75 tok | speed=13.53 tok/s
#2 | total=5.707s | prompt=0.091s/38 tok | eval=5.579s/75 tok | speed=13.44 tok/s
#3 | total=5.745s | prompt=0.084s/38 tok | eval=5.631s/75 tok | speed=13.32 tok/s
#4 | total=5.678s | prompt=0.073s/38 tok | eval=5.576s/75 tok | speed=13.45 tok/s
#5 | total=5.668s | prompt=0.083s/38 tok | eval=5.554s/75 tok | speed=13.50 tok/s

--- Results ---
Total       | min=5.644 | max=5.745 | avg=5.688 s
Prompt      | min=0.072 | max=0.091 | avg=0.081 s
Tokens eval | min=75.000 | max=75.000 | avg=75.000
Eval        | min=5.543 | max=5.631 | avg=5.577 s
Vitesse     | min=13.32 | max=13.53 | avg=13.45 tok/s


--- Ollama PS ---
NAME                ID              SIZE      PROCESSOR    CONTEXT    UNTIL              
llama3.2:1b         baf6a787fdff    1.5 GB    100% CPU     4096       4 minutes from now    
moondream:latest    55fc3abd3867    1.3 GB    100% CPU     2048       4 minutes from now

# Benchmark Ollama - mistral-small:22B
# 5 appels, generate: 'Hello world, comment ca va et toi je suis malade ?.'

DBG: ollama_model_exists: current existing model:
    -  moondream:latest
    -  llama3.2:1b

WRN: This model isn't present: mistral-small:22B


--- Ollama PS ---
NAME                ID              SIZE      PROCESSOR    CONTEXT    UNTIL              
llama3.2:1b         baf6a787fdff    1.5 GB    100% CPU     4096       4 minutes from now    
moondream:latest    55fc3abd3867    1.3 GB    100% CPU     2048       4 minutes from now

--- Materiel ---
CPU : Intel(R) Core(TM) i7-1065G7 CPU @ 1.30GHz
GPU : Intel(R) Iris(R) Plus Graphics



*** Ordi Corto:

Ollama a lancer ainsi depuis cmd:
set CUDA_VISIBLE_DEVICES=-1 && set OLLAMA_VULKAN=1 && ollama serve


# Benchmark Ollama - moondream:latest
# 5 appels, generate: 'Hello world, comment ca va et toi je suis malade ?.'

#1 | total=0.154s | prompt=0.008s/23 tok | eval=0.113s/18 tok | speed=159.21 tok/s
#2 | total=0.137s | prompt=0.007s/23 tok | eval=0.112s/18 tok | speed=160.50 tok/s
#3 | total=0.126s | prompt=0.007s/23 tok | eval=0.109s/18 tok | speed=165.54 tok/s
#4 | total=0.120s | prompt=0.006s/23 tok | eval=0.106s/18 tok | speed=169.75 tok/s
#5 | total=0.142s | prompt=0.007s/23 tok | eval=0.111s/18 tok | speed=162.00 tok/s

--- Results ---
Total       | min=0.120 | max=0.154 | avg=0.136 s
Prompt      | min=0.006 | max=0.008 | avg=0.007 s
Tokens eval | min=18.000 | max=18.000 | avg=18.000
Eval        | min=0.106 | max=0.113 | avg=0.110 s
Vitesse     | min=159.21 | max=169.75 | avg=163.40 tok/s


--- Ollama PS ---
NAME                ID              SIZE      PROCESSOR    CONTEXT    UNTIL
moondream:latest    55fc3abd3867    1.2 GB    100% GPU     2048       4 minutes from now

# Benchmark Ollama - llama3.2:1B
# 5 appels, generate: 'Hello world, comment ca va et toi je suis malade ?.'

#1 | total=0.965s | prompt=0.009s/38 tok | eval=0.923s/98 tok | speed=106.13 tok/s
#2 | total=0.971s | prompt=0.010s/38 tok | eval=0.911s/98 tok | speed=107.62 tok/s
#3 | total=0.958s | prompt=0.010s/38 tok | eval=0.921s/98 tok | speed=106.42 tok/s
#4 | total=0.972s | prompt=0.011s/38 tok | eval=0.930s/98 tok | speed=105.40 tok/s
#5 | total=0.955s | prompt=0.010s/38 tok | eval=0.927s/98 tok | speed=105.73 tok/s

--- Results ---
Total       | min=0.955 | max=0.972 | avg=0.964 s
Prompt      | min=0.009 | max=0.011 | avg=0.010 s
Tokens eval | min=98.000 | max=98.000 | avg=98.000
Eval        | min=0.911 | max=0.930 | avg=0.922 s
Vitesse     | min=105.40 | max=107.62 | avg=106.26 tok/s


--- Ollama PS ---
NAME                ID              SIZE      PROCESSOR    CONTEXT    UNTIL
llama3.2:1b         baf6a787fdff    1.5 GB    100% GPU     4096       4 minutes from now
moondream:latest    55fc3abd3867    1.2 GB    100% GPU     2048       4 minutes from now

# Benchmark Ollama - mistral-small:22B
# 5 appels, generate: 'Hello world, comment ca va et toi je suis malade ?.'

#1 | total=7.588s | prompt=0.220s/21 tok | eval=7.353s/35 tok | speed=4.76 tok/s
#2 | total=7.582s | prompt=0.222s/21 tok | eval=7.354s/35 tok | speed=4.76 tok/s
#3 | total=7.598s | prompt=0.222s/21 tok | eval=7.358s/35 tok | speed=4.76 tok/s
#4 | total=7.583s | prompt=0.222s/21 tok | eval=7.355s/35 tok | speed=4.76 tok/s
#5 | total=7.810s | prompt=0.220s/21 tok | eval=7.574s/35 tok | speed=4.62 tok/s

--- Results ---
Total       | min=7.582 | max=7.810 | avg=7.632 s
Prompt      | min=0.220 | max=0.222 | avg=0.221 s
Tokens eval | min=35.000 | max=35.000 | avg=35.000
Eval        | min=7.353 | max=7.574 | avg=7.399 s
Vitesse     | min=4.62 | max=4.76 | avg=4.73 tok/s


--- Ollama PS ---
NAME                 ID              SIZE     PROCESSOR          CONTEXT    UNTIL
mistral-small:22B    d095cd553b04    13 GB    51%/49% CPU/GPU    4096       4 minutes from now

--- Materiel ---
CPU : Intel(R) Core(TM) Ultra 7 265KF
GPU : NVIDIA GeForce GTX 1070

*** Champion1:

# Benchmark Ollama - moondream:latest
# 5 appels, generate: 'Hello world, comment ca va et toi je suis malade ?.'

#1 | total=0.090s | prompt=0.002s/23 tok | eval=0.040s/22 tok | speed=549.14 tok/s
#2 | total=0.089s | prompt=0.002s/23 tok | eval=0.040s/22 tok | speed=548.88 tok/s
#3 | total=0.092s | prompt=0.002s/23 tok | eval=0.040s/22 tok | speed=548.08 tok/s
#4 | total=0.094s | prompt=0.002s/23 tok | eval=0.040s/22 tok | speed=548.97 tok/s
#5 | total=0.089s | prompt=0.002s/23 tok | eval=0.040s/22 tok | speed=550.48 tok/s

--- Results ---
Total       | min=0.089 | max=0.094 | avg=0.091 s
Prompt      | min=0.002 | max=0.002 | avg=0.002 s
Tokens eval | min=22.000 | max=22.000 | avg=22.000
Eval        | min=0.040 | max=0.040 | avg=0.040 s
Vitesse     | min=548.08 | max=550.48 | avg=549.11 tok/s


--- Ollama PS ---
NAME                ID              SIZE      PROCESSOR    CONTEXT    UNTIL
moondream:latest    55fc3abd3867    1.3 GB    100% GPU     2048       4 minutes from now

# Benchmark Ollama - llama3.2:1B
# 5 appels, generate: 'Hello world, comment ca va et toi je suis malade ?.'

#1 | total=0.682s | prompt=0.003s/38 tok | eval=0.359s/147 tok | speed=409.12 tok/s
#2 | total=0.680s | prompt=0.003s/38 tok | eval=0.359s/147 tok | speed=409.10 tok/s
#3 | total=0.678s | prompt=0.003s/38 tok | eval=0.360s/147 tok | speed=408.38 tok/s
#4 | total=0.678s | prompt=0.003s/38 tok | eval=0.360s/147 tok | speed=408.39 tok/s
#5 | total=0.679s | prompt=0.003s/38 tok | eval=0.360s/147 tok | speed=408.38 tok/s

--- Results ---
Total       | min=0.678 | max=0.682 | avg=0.679 s
Prompt      | min=0.003 | max=0.003 | avg=0.003 s
Tokens eval | min=147.000 | max=147.000 | avg=147.000
Eval        | min=0.359 | max=0.360 | avg=0.360 s
Vitesse     | min=408.38 | max=409.12 | avg=408.67 tok/s


--- Ollama PS ---
NAME                ID              SIZE      PROCESSOR    CONTEXT    UNTIL
llama3.2:1B         baf6a787fdff    1.7 GB    100% GPU     4096       4 minutes from now
moondream:latest    55fc3abd3867    1.3 GB    100% GPU     2048       4 minutes from now

# Benchmark Ollama - mistral-small:22B
# 5 appels, generate: 'Hello world, comment ca va et toi je suis malade ?.'

#1 | total=6.034s | prompt=0.164s/21 tok | eval=5.816s/35 tok | speed=6.02 tok/s
#2 | total=6.176s | prompt=0.191s/21 tok | eval=5.897s/35 tok | speed=5.94 tok/s
#3 | total=6.010s | prompt=0.163s/21 tok | eval=5.805s/35 tok | speed=6.03 tok/s
#4 | total=15.321s | prompt=0.163s/21 tok | eval=15.118s/35 tok | speed=2.32 tok/s
#5 | total=6.111s | prompt=0.163s/21 tok | eval=5.910s/35 tok | speed=5.92 tok/s

--- Results ---
Total       | min=6.010 | max=15.321 | avg=7.930 s
Prompt      | min=0.163 | max=0.191 | avg=0.169 s
Tokens eval | min=35.000 | max=35.000 | avg=35.000
Eval        | min=5.805 | max=15.118 | avg=7.709 s
Vitesse     | min=2.32 | max=6.03 | avg=5.24 tok/s


--- Ollama PS ---
NAME                 ID              SIZE     PROCESSOR          CONTEXT    UNTIL
mistral-small:22B    d095cd553b04    13 GB    32%/68% CPU/GPU    4096       4 minutes from now

--- Materiel ---
CPU : Intel(R) Core(TM) i7-9700K CPU @ 3.60GHz
GPU : Intel Corporation CoffeeLake-S GT2 [UHD Graphics 630] (rev 02)
GPU : NVIDIA Corporation GA102 [GeForce RTX 3080 Lite Hash Rate] (rev a1)



"""