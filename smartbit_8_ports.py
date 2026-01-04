'''
    smartbit.py

    需先啟動 TRex server  , 進root
    >> sudo ./t-rex-64 -i


    bench.py
    imix_table = [ {'size': 64,    'pps': 100, 'isg': 0},
    	    {'size': 128,   'pps': 80,  'isg': 0.0},
  		    {'size': 256,   'pps': 60,  'isg': 0.0},
	 	    {'size': 512,   'pps': 40,  'isg': 0.0},
		    {'size': 1024,  'pps': 20,  'isg': 0.0},
		    {'size': 1280,  'pps': 10,  'isg': 0.0},
		    {'size': 1518,  'pps': 5,   'isg': 0.0} ]

'''
import subprocess
import time
import pexpect
import re
import pty
import os

pkt_sizes = [1518, 1280, 1024, 512, 256, 128, 64]

def find_max_mult(child, pkt_size):
    low = 0.0
    high = 100.0
    max_safe_mult = 0.0
    first = True
    epsilon = 0.1
    
    while high - low >= epsilon:
     
        if first:
            mid = 100.0
        else :
            mid = round((low + high) / 2, 2)
        
        #mid = round((low + high) / 2, 1)
        child.sendline(f'start -f stl/bench.py -p 0 1 -m {mid}% --force --tunables --size {pkt_size}')
        time.sleep(1)
        child.expect('trex>')
        child.sendline(f'start -f stl/bench_17_49.py -p 2 3 -m {mid}% --force --tunables --size {pkt_size}')
        time.sleep(1)
        child.expect('trex>')
        child.sendline(f'start -f stl/bench_18_50.py -p 4 5 -m {mid}% --force --tunables --size {pkt_size}')
        time.sleep(1)
        child.expect('trex>')
        child.sendline(f'start -f stl/bench_19_51.py -p 6 7 -m {mid}% --force --tunables --size {pkt_size}')
        time.sleep(1)
        child.expect('trex>')
        one_min_count = 60  #60
        flag = 0

        print(f"\npkt_size = {pkt_size}, mid = {mid}")

        while one_min_count > 0:  
            child.sendline('stats')
            child.expect('trex>')
            output = child.before
            clean_output = re.sub(r'\x1b\[[0-9;]*m', '', output) 

            match = re.search(r'drop_rate\s*:\s*([0-9\.]+)\s*([kMG]?bps)', clean_output)
            drop_rate = float(match.group(1))if match else -1
            unit = match.group(2)if match else -1

            if drop_rate > 0:
                flag = -1
                #break

            print(f"time = {one_min_count}, drop_rate = {drop_rate}{unit}")
            time.sleep(1)
            one_min_count-= 1

        child.sendline('stop')
        # time.sleep(1)
        child.expect('trex>')

        if first:  #避免上一輪高流量影響下一輪測試
            child.sendline(f'start -f stl/bench.py -p 0 1 -m 50% --force --tunables --size {pkt_size}')
            time.sleep(0.5)
            child.expect('trex>')
            child.sendline(f'start -f stl/bench_17_49.py -p 2 3 -m 50% --force --tunables --size {pkt_size}')
            time.sleep(0.5)
            child.expect('trex>')
            child.sendline(f'start -f stl/bench_18_50.py -p 4 5 -m 50% --force --tunables --size {pkt_size}')
            time.sleep(0.5)
            child.expect('trex>')
            child.sendline(f'start -f stl/bench_19_51.py -p 6 7 -m 50% --force --tunables --size {pkt_size}')
            time.sleep(0.5)
            child.expect('trex>')
            time.sleep(5)
            child.sendline('stop')
            child.expect('trex>')
            first = False

        if flag == 0:  
            max_safe_mult = mid
            low = round(mid + epsilon, 2)
        else:
            high = round(mid - epsilon, 2)
        
    return round(max_safe_mult, 1)


def main():
    child = pexpect.spawn('sudo ./trex-console', cwd='/home/nsd/Documents/trex/v3.08', encoding='utf-8')
    child.expect('trex>')

    results = {}
    for size in pkt_sizes:
        max_mult = find_max_mult(child, size)  
        results[size] = max_mult

    print("\n\n\n------  Test Result ------")
    print("-" * 26)
    print(f"{'Packet Size':<15}{'Multiplier':>10}")
    print("-" * 26)

    for size, mult in results.items():
        print(f"{size:<15}{mult:>9}%")


    # 如果想保留trex console，才加下面這行
    #child.interact()

if __name__ == "__main__":
    main()
