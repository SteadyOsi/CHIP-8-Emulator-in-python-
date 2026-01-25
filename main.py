import chip8_cpu as chip
import display
import input
import time
import audio

cpu = chip.Chip8_CPU()
cpu.reset()
cpu.load_rom("/home/jk/Documents/GitHub/chip8-roms/programs/Keypad Test [Hap, 2006].ch8")
# cpu.load_rom("/home/minion/Documents/GitHub/CHIP8-Roms/chip8-roms/programs/Keypad Test [Hap, 2006].ch8")
cpu.DT = 120

TICK = 1/60         # Timer tick rate
CPU_HZ = 700        # Instruction rate (normally between 500-1000)
CPU_STEP = 1/CPU_HZ

last = time.perf_counter()
timer_acc = 0.0
cpu_acc = 0.0

graphics = display.Graphics()
inputs = input.controls()
screen = graphics.init_display(20)

while cpu.running:
    now = time.perf_counter()
    time_dif = now - last
    last = now

    timer_acc += time_dif
    cpu_acc += time_dif

    #60hz timer, sound and display 
    while timer_acc >= TICK:
        timer_acc -= TICK

        cpu.timer_update()
        inputs.input_handler(cpu)
        if cpu.draw_Dirty:
            graphics.render(cpu, screen)

        if cpu.ST > 0:
            audio.beep()


    #CPU execution at CPU HZ timer 
    while cpu_acc >= CPU_STEP:
        cpu_acc -= CPU_STEP
        opcode = cpu.fetch()
        # print(f"PC:{hex(cpu.PC)} | opcode:{hex(opcode)}")
        cpu.decode(opcode)
    