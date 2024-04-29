#!/usr/bin/env python3
import subprocess
import shlex
import sys
import matplotlib.pyplot as plt

import cpuinfo

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
    cpu_info = get_cpu_info()
    plt.figure(figsize=(10, 6))
    for branch, color in zip(data.keys(), ['blue', 'green', 'red']):
        plt.plot(sizes, data[branch], marker='', label=branch, color=color)
    plt.xlabel('size')
    plt.ylabel('CPU Cycle')
    plt.title(cpu_info + 'BTB Size Test')
    plt.legend()
    plt.grid(True)
    plt.savefig(cpu_info +"_instruction.png")
    plt.show()

def get_cpu_info():
    cpu_info = cpuinfo.get_cpu_info()
    return cpu_info['brand_raw']

def main():
    branch_types = ["jmp", "je taken", "jne not-taken"]
    sizes = list(range(128, 8192+128, 128))
    results = run_branch_command((("jmp", "-a8 -tjmp"), ("je taken", "-a8 -tje_always_taken"), ("jne not-taken", "-a8 -tjne_never_taken")), sizes)
    data = parse_results(results, branch_types)
    print(data)
    plot_data(sizes, data)

if __name__ == "__main__":
    main()
