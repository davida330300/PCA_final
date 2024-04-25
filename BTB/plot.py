#!/usr/bin/env python3
import subprocess
import shlex
import sys
import os
import matplotlib.pyplot as plt


JJJJ = (("jmp", "-a8 -tjmp"), ("je taken", "-a8 -tje_always_taken"),("jne not-taken", "-a8 -tjne_never_taken"))
#JJJJ = (("jmp", "-a8 -tjmp"))
TTTT =list(range(128,8192+128,128))

A={}

for j in JJJJ:
    cmd = "./branch %s %s" % (j[1], ' '.join(sys.argv[1:]))
    for t in TTTT:
        p = subprocess.run(
            shlex.split(cmd + ' -c %d' % t),
            stdout=subprocess.PIPE)

        x_min = float("inf")
        for l in p.stdout.split(b'\n'):
            if not l:continue
            x = float(l.decode())
            x_min = min(x_min, x)

        A[(j,t)] = x_min

size = []
cycle_jmp = []
cycle_taken = []
cycle_not_taken = []
print("," + (",".join(j[0] for j in JJJJ)))
for t in TTTT:
    print("%d" % t, end="")
    size.append(t)
    for j in JJJJ:
        if (j,t) in A:
            if j[0] == "jmp":
                cycle_jmp.append(A[(j,t)])
            elif j[0] == "je taken":
                cycle_taken.append(A[(j,t)])
            elif j[0] == "jne not-taken":
                cycle_not_taken.append(A[(j,t)])
            print(",%.3f" % A[(j,t)], end="")
        else:
            print(",", end="")
    print()
    
plt.plot(size, cycle_jmp, marker='o', label='jmp', color='blue')  
plt.plot(size, cycle_taken, marker='o', label='je taken', color='green')  
plt.plot(size, cycle_not_taken, marker='o', label='jne not-taken', color='red')  
plt.xlabel('size')
plt.ylabel('CPU Cycle')
plt.title('AMD R5-5600H BTB Size Test')
plt.legend()  # Add legend to distinguish between different plots
plt.grid(True)
plt.savefig("AMD_jmp.png")
plt.show() 