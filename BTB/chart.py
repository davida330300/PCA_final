#!/usr/bin/env python3
import subprocess
import shlex
import sys
import os
from matplotlib import pyplot as plt

import cpuinfo


def run_benchmark():
    block_sizes = (4, 8, 16, 32, 64)
    test_sizes = list(range(128, 8192 + 128, 128))
    results = {}

    for block_size in block_sizes:
        cmd = f"./branch -a{block_size} -t{' '.join(sys.argv[1:])}"
        for test_size in test_sizes:
            if os.environ.get("SKIP") and block_size * test_size >= 200000:
                continue
            process = subprocess.run(
                shlex.split(f"{cmd} -c{test_size}"),
                stdout=subprocess.PIPE)
            min_cycle = min(float(line.decode()) for line in process.stdout.split(b'\n') if line.strip())
            results[(block_size, test_size)] = min_cycle

    return results

def parse_results(results, block_sizes, test_sizes):
    parsed_data = {block_size: [] for block_size in block_sizes}
    for test_size in test_sizes:
        for block_size in block_sizes:
            if (block_size, test_size) in results:
                parsed_data[block_size].append(results[(block_size, test_size)])
            else:
                parsed_data[block_size].append(None)
    return parsed_data

def print_results(block_sizes, test_sizes, parsed_data):
    print("," + ",".join(map(str, block_sizes)))
    for test_size in test_sizes:
        print(test_size, end="")
        for block_size in block_sizes:
            if parsed_data[block_size]:
                print(f",{parsed_data[block_size].pop(0):.3f}", end="")
            else:
                print(",", end="")
        print()

def plot_data(test_sizes, parsed_data):
    cpu_info = get_cpu_info()
    plt.figure(figsize=(10, 6))
    colors = ['blue', 'green', 'red', 'orange', 'pink']
    for block_size, color in zip(parsed_data.keys(), colors):
        plt.plot(test_sizes, parsed_data[block_size], marker='', label=str(block_size), color=color)
    plt.xlabel('size')
    plt.ylabel('CPU Cycle')
    plt.title(f'{cpu_info} BTB Size Test, Instruction {sys.argv[1:]}')
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{cpu_info}_block_size_{sys.argv[1:]}.png")
    plt.show()

def get_cpu_info():
    cpu_info = cpuinfo.get_cpu_info()
    return cpu_info['brand_raw']


def main():
    results = run_benchmark()
    block_sizes = (4, 8, 16, 32, 64)
    test_sizes = list(range(128, 8192 + 128, 128))
    parsed_data = parse_results(results, block_sizes, test_sizes)
    print(parsed_data)
    plot_data(test_sizes, parsed_data)

if __name__ == "__main__":
    main()
