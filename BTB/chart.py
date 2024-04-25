#!/usr/bin/env python3
import subprocess
import shlex
import sys
import os

from matplotlib import pyplot as plt

JJJJ = (4,8,16,32,64)
TTTT =list(range(128,8192+128,128))

A={}
size = []
block_size_4 = []
block_size_8 = []
block_size_16 = []
block_size_32 = []
block_size_64 = []

for j in JJJJ:
    cmd = "./branch -a%d -t%s" % (j, ' '.join(sys.argv[1:]))
    for t in TTTT:
        if os.environ.get("SKIP") and j*t >= 200000:
            continue
        p = subprocess.run(
            shlex.split(cmd + ' -c%d' % t),
            stdout=subprocess.PIPE)

        x_min = float("inf")
        for l in p.stdout.split(b'\n'):
            if not l:continue
            x = float(l.decode())
            x_min = min(x_min, x)

        A[(j,t)] = x_min


print("," + (",".join(map(str,JJJJ))))
for t in TTTT:
    print("%d" % t, end="")
    size.append(t)
    for j in JJJJ:
        if (j,t) in A:
            if j == 4:
                block_size_4.append(A[(j,t)])
            elif j == 8:
                block_size_8.append(A[(j,t)])
            elif j == 16:
                block_size_16.append(A[(j,t)])
            elif j == 32:
                block_size_32.append(A[(j,t)])
            elif j == 64:
                block_size_64.append(A[(j,t)])
            print(",%.3f" % A[(j,t)], end="")
        else:
            print(",", end="")
    print()

plt.plot(size, block_size_4, marker='', label='4', color='blue')  
plt.plot(size, block_size_8, marker='', label='8', color='green')  
plt.plot(size, block_size_16, marker='', label='16', color='red')  
plt.plot(size, block_size_32, marker='', label='32', color='orange')  
plt.plot(size, block_size_64, marker='', label='64', color='pink')  
plt.xlabel('size')
plt.ylabel('CPU Cycle')
plt.title('AMD R5-5600H BTB Size Test, Instruction' + str(sys.argv[1:]))
plt.legend()  # Add legend to distinguish between different plots
plt.grid(True)
plt.savefig("AMD_block_size_" +str(sys.argv[1:]) + ".png" )
plt.show() 