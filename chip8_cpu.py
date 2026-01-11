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
            return

        for i,byte in enumerate(rom_data):
            self.memory[0x200 + i] = byte  # sequentially load ROM bytes into memory

        self.PC = 0x200

    def timer_update(self):
        if self.DT > 0:
            self.DT -= 1
            print(f"DT updated to: {self.DT}")
        if self.ST > 0:
            self.ST -= 1
            print(f"ST updated to: {self.ST}")

    # 00E0 - CLS
    def execute_cls(self): #0x0 clear 
        self.display = [[False for _ in range(64)]for _ in range(32)]
        self.draw_Dirty = True
        self.increment()

    # 00EE - RET
    def execute_RET(self):
        self.SP -= 1
        self.PC = self.Stack[self.SP]

    # 0nnn - SYS addr

    # 1nnn - JP addr
    def execute_jp(self, nnn): #0x1 jump 
        self.PC = nnn

    # 2nnn - CALL addr
    def execute_CALL(self, nnn): 
        self.Stack[self.SP] = self.PC + 2
        self.SP += 1
        self.PC = nnn


    # 3xkk - SE Vx, byte

    # 4xkk - SNE Vx, byte

    # 5xy0 - SE Vx, Vy

    # 6xkk - LD Vx, byte
    def execute_ld_vx_kk(self, x, kk): #0x6 load
        self.V[x] = kk
        self.increment()

    # 7xkk - ADD Vx, byte
    def execute_add_vx_kk(self, x, kk): #0x7 add 
        self.V[x] = (self.V[x] + kk) & 0xFF
        self.increment()

    # 8xy0 - LD Vx, Vy

    # 8xy1 - OR Vx, Vy

    # 8xy2 - AND Vx, Vy

    # 8xy3 - XOR Vx, Vy

    # 8xy4 - ADD Vx, Vy

    # 8xy5 - SUB Vx, Vy

    # 8xy6 - SHR Vx {, Vy}

    # 8xy7 - SUBN Vx, Vy

    # 8xyE - SHL Vx {, Vy}

    # 9xy0 - SNE Vx, Vy

    # Annn - LD I, addr
    def execute_ld_i_nnn(self, nnn):
        self.I = nnn
        self.increment()

    # Bnnn - JP V0, addr

    # Cxkk - RND Vx, byte

    # Dxyn - DRW Vx, Vy, nibble
    def execute_drw(self, Vx, Vy, n):

        masks = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01]

        self.V[0xF] = 0

        screenX = self.V[Vx]
        screenY = self.V[Vy]

        row = 0
        while row < n:
            sprite = self.memory[self.I + row]

            col = 0
            while col < len(masks):

                bit = sprite & masks[col]

                if (self.display[(screenY + row) % 32][(screenX + col) % 64] == True) and (bit == masks[col]):
                    self.V[0xF] = 1
                    self.display[(screenY + row) % 32][(screenX + col) % 64] ^= True

                elif bit == masks[col]:
                    self.display[(screenY + row) % 32][(screenX + col) % 64] ^= True

                col += 1

            row += 1

        self.draw_Dirty = True
        self.increment()

    # Ex9E - SKP Vx
    def execute_SKP_V(self, Vx):
        regX = self.V[Vx] & 0x0F 

        key = self.keys[regX]
        if key:
            self.increment()
            self.increment()
        else:
            self.increment()


    # ExA1 - SKNP Vx
    def execute_SKNP_V(self, Vx):
        regX = self.V[Vx] & 0x0F 

        key = self.keys[regX]
        if not key:
            self.increment()
            self.increment()
        else:
            self.increment()
        

    # Fx07 - LD Vx, DT

    # Fx0A - LD Vx, K

    # Fx15 - LD DT, Vx

    # Fx18 - LD ST, Vx

    # Fx1E - ADD I, Vx

    # Fx29 - LD F, Vx

    # Fx33 - LD B, Vx

    # Fx55 - LD [I], Vx

    # Fx65 - LD Vx, [I]
 
    def decode(self, opcode):
        nibOne = (opcode >> 12) & 0xF
        
        match nibOne:
            case 0x0:
                if opcode == 0x00E0:
                    self.execute_cls()
                elif opcode == 0x00EE:
                    if self.SP <= 0: print("STACK UNDER FLOW ERROR")
                    elif self.SP > 16: print("STACK OVER FLOW ERROR")
                    else: 
                        self.execute_RET()
                else:
                    print(f"UNIMP OPCODE: {hex(opcode)} AT PC:{hex(self.PC)}")
                    self.increment()

            case 0x1:
                nnn = opcode & 0x0FFF
                self.execute_jp(nnn)
            case 0x2:
                nnn = opcode & 0x0FFF
                self.execute_CALL(nnn)
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
            case 0xD: 
                Vx = (opcode & 0x0F00) >> 8
                Vy = (opcode & 0x00F0) >> 4
                n = opcode & 0x000F
                self.execute_drw(Vx, Vy, n)
            case 0xE:
                nibThreeFour = (opcode & 0x00FF)
                Vx = (opcode & 0x0F00) >> 8
                
                if nibThreeFour == 0x9E:
                    self.execute_SKP_V(Vx)
                elif nibThreeFour == 0xA1:
                    self.execute_SKNP_V(Vx)
                else:
                    print(f"UNIMP OPCODE: {hex(opcode)} AT PC:{hex(self.PC)}")
                    self.increment()

            case _:
                print(f"UNIMP OPCODE: {hex(opcode)} AT PC:{hex(self.PC)}")
                self.increment()

 