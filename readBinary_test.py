rom_Address = "CHIP8-Roms/chip8-roms/programs/IBM Logo.ch8"  # test ROM to load

def whats_In_Mem(mem):  # still in works
    for i in mem:
        print(i)

memory = bytearray(4096)  # CHIP-8 has 4KB of addressable memory
PC = 0x200  # programs start at 0x200; below holds font sprites/reserved space
I = 0  # index register (unused in this simple loader)
V = [0] * 16  # general-purpose registers V0-VF

with open(rom_Address, "rb") as rom_file:
    rom_data = rom_file.read()

if len(rom_data) > 4096 - 0x200:
    print("Rom is too large")  # guard against ROMs that overflow memory

for i,byte in enumerate(rom_data):
    memory[0x200 + i] = byte  # sequentially load ROM bytes into memory

i = 0
while(i < 8):
    print(f"memory address {hex(PC + i)} : {hex(memory[PC + i])}")  # peek at first few bytes
    i += 1

print(f"value of PC {hex(PC)}")
