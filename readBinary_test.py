rom_Address = "CHIP8-Roms/chip8-roms/programs/IBM Logo.ch8"

def whats_In_Mem(mem): # still in works
    for i in mem:
        print(i)

memory = bytearray(4096)
PC = 0x200
I = 0
V = [0] * 16

with open(rom_Address, "rb") as rom_file:
    rom_data = rom_file.read()

if len(rom_data) > 4096 - 0x200:
    print("Rom is too large")

for i,byte in enumerate(rom_data):
    memory[0x200 + i] = byte

i = 0
while(i < 8):
    print(f"memory address {hex(PC + i)} : {hex(memory[PC + i])}")
    i += 1

print(f"value of PC {hex(PC)}")

#teset comment