import chip8_cpu as chip
import time

cpu = chip.Chip8_CPU()
cpu.reset()
cpu.load_rom("/home/minion/Documents/GitHub/CHIP8-Roms/chip8-roms/programs/IBM Logo.ch8")
cpu.DT = 120

i = 0
TICK = 1/60
last = time.perf_counter()

while(i <= 30):
    #60hz timer
    now = time.perf_counter()
    while now - last >= TICK:
        last += TICK
        cpu.timer_update()

    opcode = cpu.fetch()
    print(f"PC:{hex(cpu.PC)} | opcode:{hex(opcode)}")
    cpu.decode(opcode)
    i+= 1