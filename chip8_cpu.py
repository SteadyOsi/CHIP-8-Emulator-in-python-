class Chip8_CPU:
    def __init__(self):
        self.memory = bytearray(4096)  # CHIP-8 has 4KB of addressable memory
        self.PC = 0x200  # programs start at 0x200; below holds font sprites/reserved space
        self.I = 0  # index register (unused in this simple loader)
        self.V = [0] * 16  # general-purpose registers V0-VF
        self.Stack = [0] * 16
        self.SP = 0 #stack pointer 
        self.DT = 0 
        self.ST = 0 # display and sound timers (tick @ 60 Hz)
        self.display = [[False for _ in range(64)]for _ in range(32)] # sets a 2D list to all false, its Y,X
        self.keys = [False for _ in range(16)]
        self.draw_Dirty = False 

    def reset(self): # currently reset blows away all memory not just the ROM
        #self.memory = bytearray(4096)  # CHIP-8 has 4KB of addressable memory
        self.PC = 0x200  # programs start at 0x200; below holds font sprites/reserved space
        self.I = 0  # index register (unused in this simple loader)
        self.V = [0] * 16  # general-purpose registers V0-VF
        self.Stack = [0] * 16
        self.SP = 0 #stack pointer 
        self.DT = 0
        self.ST = 0 # display and sound timers (tick @ 60 Hz)
        self.display = [[False for _ in range(64)]for _ in range(32)] # sets a 2D list to all false, its Y,X
        self.keys = [False for _ in range(16)]
        self.draw_Dirty = False 

    def fetch(self): # returns one 16 bit opcode based on the current PC
        FirstPart = self.memory[self.PC]
        SecondPart = self.memory[self.PC + 1]
        return (FirstPart << 8) | SecondPart

    def increment(self): # increments by 2 bytes 
        self.PC += 2
    
    def peek(self): # peek just at the first 2 bytes
        FirstPart = self.memory[self.PC]
        SecondPart = self.memory[self.PC + 1]
        return (FirstPart << 8) | SecondPart

    def load_rom(self, rom_Address):
        with open(rom_Address, "rb") as rom_file:
            rom_data = rom_file.read()

        if len(rom_data) > 4096 - 0x200:
            print("Rom is too large")  # guard against ROMs that overflow memory

        for i,byte in enumerate(rom_data):
            self.memory[0x200 + i] = byte  # sequentially load ROM bytes into memory

        self.PC = 0x200

    def execute_cls(self): #0x0 clear 
        self.display = [[False for _ in range(64)]for _ in range(32)]
        self.draw_Dirty = True
        self.increment()

    def execute_jp(self, nnn): #0x1 jump 
        self.PC = nnn

    def execute_ld_vx_kk(self, x, kk): #0x6 load
        self.V[x] = kk
        self.increment()

    def execute_add_vx_kk(self, x, kk): #0x7 add 
        self.V[x] = (self.V[x] + kk) & 0xFF
        self.increment()

    def execute_ld_i_nnn(self, nnn):
        self.I = nnn
        self.increment()
 
    def decode(self, opcode):
        nibOne = (opcode >> 12) & 0xF
        
        match nibOne:
            case 0x0:
                self.execute_cls()
            case 0x1:
                nnn = opcode & 0x0FFF
                self.execute_jp(nnn)
            case 0x6:
                x = ((opcode >> 8) & 0x000F)
                kk = opcode & 0x00FF
                self.execute_ld_vx_kk(x, kk)
            case 0x7:
                x = ((opcode >> 8) & 0x000F)
                kk = opcode & 0x00FF
                self.execute_add_vx_kk(x, kk)
            case 0xA:
                nnn = opcode & 0x0FFF
                self.execute_ld_i_nnn(nnn)

            case _:
                print(f"UNIMP OPCODE: {hex(opcode)} AT PC:{hex(self.PC)}")
                self.increment()

 