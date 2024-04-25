#!/usr/bin/env python3
import subprocess
import shlex
import sys
import os
import matplotlib.pyplot as plt

def run_branch_command(command, sizes):
    results = {}
    for branch_type, options in command:
        for size in sizes:
            full_command = f"./branch {options} {' '.join(sys.argv[1:])} -c {size}"
            process = subprocess.run(shlex.split(full_command), stdout=subprocess.PIPE)
            min_cycle = min(float(line.decode()) for line in process.stdout.split(b'\n') if line.strip())
            results[(branch_type, size)] = min_cycle
    return results

def parse_results(results, branch_types):
    data = {branch: [] for branch in branch_types}
    for branch, size in results.keys():
        data[branch].append(results[(branch, size)])
    return data

def print_data(branch_types, data):
    print("," + ",".join(branch for branch in branch_types))
    for size, values in data.items():
        print(size, end="")
        for value in values:
            print(f",{value:.3f}", end="")
        print()

def plot_data(sizes, data):
    plt.figure(figsize=(10, 6))
    for branch, color in zip(data.keys(), ['blue', 'green', 'red']):
        plt.plot(sizes, data[branch], marker='o', label=branch, color=color)
    plt.xlabel('size')
    plt.ylabel('CPU Cycle')
    plt.title('AMD R5-5600H BTB Size Test')
    plt.legend()
    plt.grid(True)
    plt.savefig("AMD_jmp.png")
    plt.show()

def run_branch_command_optimized(sizes):
    results = {}
    for j in sizes:
        cmd = f"./branch -a{j} {' '.join(sys.argv[1:])}"
        for t in sizes:
            if os.environ.get("SKIP") and j * t >= 200000:
                continue
            full_command = f"{cmd} -c {t}"
            process = subprocess.run(shlex.split(full_command), stdout=subprocess.PIPE)
            min_cycle = min(float(line.decode()) for line in process.stdout.split(b'\n') if line.strip())
            results[(j, t)] = min_cycle
    return results

def parse_results_optimized(results, sizes):
    data = {size: [] for size in sizes}
    for _, size in results.keys():
        data[size].append(results[(_, size)])
    return data

def print_data_optimized(sizes, data):
    print("," + ",".join(str(size) for size in sizes))
    for t in sizes:
        print(t, end="")
        for value in data[t]:
            print(f",{value:.3f}", end="")
        print()

def plot_data_optimized(sizes, data):
    plt.figure(figsize=(10, 6))
    for size, values in data.items():
        plt.plot(sizes, values, marker='o', label=f'size={size}')
    plt.xlabel('size')
    plt.ylabel('CPU Cycle')
    plt.title('AMD R5-5600H BTB Size Test')
    plt.legend()
    plt.grid(True)
    plt.savefig("AMD_jmp_optimized.png")
    plt.show()

def main():
    branch_types = ["jmp", "je taken", "jne not-taken"]
    sizes = list(range(128, 8192+128, 128))
    #results = run_branch_command((("jmp", "-a8 -tjmp"), ("je taken", "-a8 -tje_always_taken"), ("jne not-taken", "-a8 -tjne_never_taken")), sizes)
    results = run_branch_command((("jmp", "-a4 -tjmp"), ("je taken", "-a4 -tje_always_taken"), ("jne not-taken", "-a4 -tjne_never_taken")), sizes)
    
    data = parse_results(results, branch_types)
    print_data(branch_types, data)
    plot_data(sizes, data)

    JJJJ = (4, 8, 16, 32, 64)
    TTTT = list(range(128, 8192 + 128, 128))

    results_optimized = run_branch_command_optimized(JJJJ, TTTT)
    data_optimized = parse_results_optimized(results_optimized, TTTT)
    print_data_optimized(TTTT, data_optimized)
    plot_data_optimized(TTTT, data_optimized)

if __name__ == "__main__":
    main()
