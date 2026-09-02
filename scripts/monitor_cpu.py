# -*- coding: cp1252 -*- 

import psutil
import time

def top_cpu_processes(count=10):
    print("1")
    for p in psutil.process_iter():
        try:
            p.cpu_percent(None)
        except:
            pass
    print("2")
    time.sleep(1.)

    processes = []

    for p in psutil.process_iter(["pid", "name"]):
        try:
            cpu = p.cpu_percent(None)

            processes.append(
                (cpu, p.info["pid"], p.info["name"])
            )

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    print("3")
    processes.sort(
        key=lambda x: x[0],
        reverse=True
    )
    print("4")

    print("\n--- CPU ---")

    for cpu, pid, name in processes[:count]:
        print(
            f"{cpu:6.1f}%  "
            f"PID={pid:<6} "
            f"{name}"
        )
        
def compute_top_cpu_processes( interval = 0.1 ):

    processes = []

    # Snapshot 1
    t1 = time.perf_counter()

    for p in psutil.process_iter(["pid", "name"]):
        try:
            cpu_times = p.cpu_times()
            processes.append({
                "process": p,
                "pid": p.pid,
                "name": p.info["name"],
                "cpu": cpu_times.user + cpu_times.system
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Petite fenêtre de mesure
    time.sleep(interval)

    # Snapshot 2
    t2 = time.perf_counter()

    results = []

    for item in processes:
        p = item["process"]

        try:
            cpu_times = p.cpu_times()

            cpu_delta = (
                cpu_times.user
                + cpu_times.system
                - item["cpu"]
            )

            elapsed = t2 - t1

            # Nombre de CPU logiques
            cpu_percent = (
                cpu_delta / elapsed
                * 100
                / psutil.cpu_count()
            )

            results.append(
                (
                    cpu_percent,
                    item["pid"],
                    item["name"]
                )
            )

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    results.sort(reverse=True)

    return results
    
    
    
def print_results( results, count = 10 ):
    mypid = psutil.Process().pid
    for cpu, pid, name in results[:count]:
        if pid == mypid:
            name = f"[{name}]"
        print(
            f"{cpu:6.1f}%  "
            f"{pid:<6}  "
            f"{name}"
        )
    
_last_cpu_times = psutil.cpu_times()
_last_time = time.perf_counter()


def get_cpu_total_usage():
    global _last_cpu_times, _last_time

    now = time.perf_counter()
    cpu_times = psutil.cpu_times()

    elapsed = now - _last_time

    idle = cpu_times.idle - _last_cpu_times.idle
    total = sum(cpu_times) - sum(_last_cpu_times)

    _last_cpu_times = cpu_times
    _last_time = now

    if total <= 0:
        return 0.0

    return (1.0 - idle / total) * 100.0



if __name__ == "__main__":
    print( "this pid:", psutil.Process().pid )

    while 1:
        print(f"CPU : {get_cpu_total_usage():.1f}%")

        res = compute_top_cpu_processes() # takes around 5 sec and 33% of my cpu !
        print_results( res )
        print("")
        time.sleep(3.)