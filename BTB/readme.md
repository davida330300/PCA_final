compile:
`
gcc -g -flto -O3 -Wall -Wextra scramble.c perf.c gadget.c main.c -o branch
`
echo 1 | sudo tee /proc/sys/vm/nr_hugepages

run test 

`

`

block size test:
`
python3 ./chart.py call_dedicated_ret
python3 ./chart.py forward_call_without_ret
python3 ./chart.py call_shared_ret
python3 ./chart.py jne_never_taken
python3 ./chart.py je_always_taken
python3 ./chart.py jmp_weaved
python3 ./chart.py jmp
python3 ./chart.py inc
`
