import chip8_cpu as chip

cpu = chip.Chip8_CPU()
cpu.reset()
cpu.load_rom("CHIP8-Roms/chip8-roms/programs/IBM Logo.ch8")

opcode = cpu.fetch()
cpu.decode(opcode)