import time
import os
import random

def do_60hz_thing():
    print(f"TICK {TICK}")
    print(f"LAST {last}")
    print(f"now {now}")
    print("")

def hz_timer():
    TICK = 1/10
    last = time.time()

    while True:
        now = time.time()
        if now - last >= TICK:
            last += TICK
            do_60hz_thing()

def count_down():
    count = 60 * 1

    start = time.time()

    while time.time() - start <= count:
        print(time.time() - start)

def randomHex():
    ran = random.randbytes(2)
    print(ran.hex() & 0x0F)
# call functinos 
randomHex()