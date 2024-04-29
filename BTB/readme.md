compile:
`
gcc -g -flto -O3 -Wall -Wextra scramble.c perf.c gadget.c main.c -o branch
`
echo 1 | sudo tee /proc/sys/vm/nr_hugepages

run test 

`
python3 ./BTB.py
`

block size test:
`
python3 ./Block.py call_dedicated_ret
python3 ./Block.py forward_call_without_ret
python3 ./Block.py call_shared_ret
python3 ./Block.py jne_never_taken
python3 ./Block.py je_always_taken
python3 ./Block.py jmp_weaved
python3 ./Block.py jmp
python3 ./Block.py inc
`
