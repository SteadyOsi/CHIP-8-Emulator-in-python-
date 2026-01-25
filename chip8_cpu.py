import random

FONT_START = 0x50
FONTSET = [
    0xF0,0x90,0x90,0x90,0xF0,  # 0
    0x20,0x60,0x20,0x20,0x70,  # 1
    0xF0,0x10,0xF0,0x80,0xF0,  # 2
    0xF0,0x10,0xF0,0x10,0xF0,  # 3
    0x90,0x90,0xF0,0x10,0x10,  # 4
    0xF0,0x80,0xF0,0x10,0xF0,  # 5
    0xF0,0x80,0xF0,0x90,0xF0,  # 6
    0xF0,0x10,0x20,0x40,0x40,  # 7
    0xF0,0x90,0xF0,0x90,0xF0,  # 8
    0xF0,0x90,0xF0,0x10,0xF0,  # 9
    0xF0,0x90,0xF0,0x90,0x90,  # A
    0xE0,0x90,0xE0,0x90,0xE0,  # B
    0xF0,0x80,0x80,0x80,0xF0,  # C
    0xE0,0x90,0x90,0x90,0xE0,  # D
    0xF0,0x80,0xF0,0x80,0xF0,  # E
    0xF0,0x80,0xF0,0x80,0x80,  # F
]

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
        self.running = True

        for i, b in enumerate(FONTSET):
            self.memory[FONT_START + i] = b

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
        self.running = True

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
            # print(f"DT updated to: {self.DT}")
        if self.ST > 0:
            self.ST -= 1
            # print(f"ST updated to: {self.ST}")

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
    # normally do nothing 

    # 1nnn - JP addr
    def execute_jp(self, nnn): #0x1 jump 
        self.PC = nnn

    # 2nnn - CALL addr
    def execute_CALL(self, nnn): 
        self.Stack[self.SP] = self.PC + 2
        self.SP += 1
        self.PC = nnn

    # 3xkk - SE Vx, byte
    def execute_SE_vx_kk(self, x, kk):
        if self.V[x] == kk:
            self.PC += 4
        else: 
            self.increment()

    # 4xkk - SNE Vx, byte
    def execute_SNE_vx_kk(self, x, kk):
        if self.V[x] != kk:
            self.PC += 4
        else: 
            self.increment()

    # 5xy0 - SE Vx, Vy
    def execute_SE_vx_vy(self, x, y):
        if self.V[x] == self.V[y]:
            self.PC += 4
        else: 
            self.increment()

    # 6xkk - LD Vx, byte
    def execute_ld_vx_kk(self, x, kk): #0x6 load
        self.V[x] = kk
        self.increment()

    # 7xkk - ADD Vx, byte
    def execute_add_vx_kk(self, x, kk): #0x7 add 
        self.V[x] = (self.V[x] + kk) & 0xFF
        self.increment()

    # 8xy0 - LD Vx, Vy
    def execute_LD_vx_vy(self, x, y):
        self.V[x] = self.V[y]
        self.increment()

    # 8xy1 - OR Vx, Vy
    def execute_OR_vx_vy(self, x, y):
        self.V[x] = self.V[x] | self.V[y]
        self.increment()

    # 8xy2 - AND Vx, Vy
    def execute_AND_vx_vy(self, x, y):
        self.V[x] = self.V[x] & self.V[y]
        self.increment()

    # 8xy3 - XOR Vx, Vy
    def execute_XOR_vx_vy(self, x, y):
        self.V[x] ^= self.V[y]
        self.increment()

    # 8xy4 - ADD Vx, Vy
    def execute_ADD_vx_vy(self, x, y):
        self.V[0xF] = 1 if self.V[x] + self.V[y] > 255 else 0
        self.V[x] = (self.V[x] + self.V[y]) & 0xFF
        self.increment() 

    # 8xy5 - SUB Vx, Vy
    def execute_SUB_vx_vy(self, x, y):
        if self.V[x] >= self.V[y]:
            self.V[0xF] = 1
        else:
            self.V[0xF] = 0

        self.V[x] = (self.V[x] - self.V[y]) & 0xFF
        self.increment() 

    # 8xy6 - SHR Vx {, Vy}
    def execute_SHR_vx(self, x):
        self.V[0xF] = (self.V[x] & 0x01)
        self.V[x] >>= 1 # or self.V[x] = self.V[x] >> 1 .... Okay I cant tell if this goes >> or <<... well see
        self.increment()

    # 8xy7 - SUBN Vx, Vy
    def execute_SUBN_x_y(self, x, y):
        vx = self.V[x]
        vy = self.V[y]

        self.V[0xF] = 1 if vy >= vx else 0
        self.V[x] = (self.V[y] - self.V[x]) & 0xFF

        self.increment()

    # 8xyE - SHL Vx {, Vy}
    def execute_SHL_vx(self, x):
        self.V[0xF] = (self.V[x] & 0x80) >> 7
        self.V[x] = (self.V[x] << 1) & 0xFF
        self.increment()

    # 9xy0 - SNE Vx, Vy
    def execute_SNE_vx_vy(self, x, y):
        if self.V[x] != self.V[y]:
            self.PC += 4
        else: 
            self.increment()

    # Annn - LD I, addr
    def execute_ld_i_nnn(self, nnn):
        self.I = nnn
        self.increment()

    # Bnnn - JP V0, addr
    def execute_JP_V0(self, nnn):
        self.PC = nnn + self.V[0]

    # Cxkk - RND Vx, byte
    def execute_RND_vx_kk(self, x, kk):
        self.V[x] = random.randint(0, 255) & kk
        self.increment()

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
    def execute_LD_vx_dt(self, x):
        self.V[x] = self.DT
        self.increment()

    # Fx0A - LD Vx, K
    def execute_LD_vx_k(self, x):
        for i in range(16):
            if self.keys[i]: 
                self.V[x] = i
                self.increment()
                break

    # Fx15 - LD DT, Vx
    def execute_LD_DT_vx(self, x):
        self.DT = self.V[x]
        self.increment()

    # Fx18 - LD ST, Vx
    def execute_LD_ST_vx(self, x):
        self.ST = self.V[x]
        self.increment()

    # Fx1E - ADD I, Vx
    def execute_ADD_I_vx(self, x):
        self.I += self.V[x]
        self.increment()

    # Fx29 - LD F, Vx
    def execute_LD_F_vx(self, x):
        self.I = FONT_START + (self.V[x] & 0x0F) * 5
        self.increment()

    # Fx33 - LD B, Vx
    def execute_LD_B_vx(self, x):
        value = self.V[x]

        self.memory[self.I] = value // 100
        self.memory[self.I + 1] = (value // 10) % 10
        self.memory[self.I + 2] = value % 10

        self.increment()

    # Fx55 - LD [I], Vx
    def execute_LD_I_vx(self, x):
        index = 0
        
        while index <= x:
            self.memory[self.I + index] = self.V[index]
            index += 1

        self.increment()

    # Fx65 - LD Vx, [I]
    def execute_LD_vx_I(self, x):
        index = 0
        
        while index <= x:
            self.V[index] = self.memory[self.I + index]
            index += 1

        self.increment()

 
    def decode(self, opcode):
        nibOne = (opcode >> 12) & 0xF
        
        match nibOne:
            case 0x0:
                if opcode == 0x00E0:
                    self.execute_cls()
                elif opcode == 0x00EE:
                    if self.SP <= 0: 
                        print("STACK UNDER FLOW ERROR")
                        self.increment()
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

            case 0x3:
                x = (opcode & 0x0F00) >> 8
                kk = opcode & 0x00FF
                self.execute_SE_vx_kk(x, kk)

            case 0x4:
                x = (opcode & 0x0F00) >> 8
                kk = opcode & 0x00FF
                self.execute_SNE_vx_kk(x, kk)

            case 0x5:
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4 
                if (opcode & 0x000F) == 0:
                    self.execute_SE_vx_vy(x, y)
                else:
                    print(f"UNIMP OPCODE: {hex(opcode)} AT PC:{hex(self.PC)}")
                    self.increment()

            case 0x6:
                x = ((opcode >> 8) & 0x000F)
                kk = opcode & 0x00FF
                self.execute_ld_vx_kk(x, kk)

            case 0x7:
                x = ((opcode >> 8) & 0x000F)
                kk = opcode & 0x00FF
                self.execute_add_vx_kk(x, kk)
            
            case 0x8:
                nibFour = (opcode & 0x000F)
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4

                #8xy0
                if nibFour == 0:
                    self.execute_LD_vx_vy(x, y)

                #8xy1
                elif nibFour == 1:
                    self.execute_OR_vx_vy(x, y)

                #8xy2
                elif nibFour == 2:
                    self.execute_AND_vx_vy(x, y)

                #8xy3
                elif nibFour == 3:
                    self.execute_XOR_vx_vy(x, y)

                #8xy4
                elif nibFour == 4:
                    self.execute_ADD_vx_vy(x, y)

                #8xy5
                elif nibFour == 5:
                    self.execute_SUB_vx_vy(x, y)

                #8xy6
                elif nibFour == 6:
                    self.execute_SHR_vx(x)

                #8xy7
                elif nibFour == 7:
                    self.execute_SUBN_x_y(x, y)

                #8xyE
                elif nibFour == 0xE:
                    self.execute_SHL_vx(x)
                
                else:
                    print(f"UNIMP OPCODE: {hex(opcode)} AT PC:{hex(self.PC)}")
                    self.increment()

            case 0x9:
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4 
                if (opcode & 0x000F) == 0:
                    self.execute_SNE_vx_vy(x, y)
                else:
                    print(f"UNIMP OPCODE: {hex(opcode)} AT PC:{hex(self.PC)}")
                    self.increment()
                

            case 0xA:
                nnn = opcode & 0x0FFF
                self.execute_ld_i_nnn(nnn)

            case 0xB:
                nnn = opcode & 0x0FFF
                self.execute_JP_V0(nnn)

            case 0xC:
                x = ((opcode >> 8) & 0x000F)
                kk = opcode & 0x00FF
                self.execute_RND_vx_kk(x, kk)

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

            case 0xF:
                nibThreeFour = (opcode & 0x00FF)
                x = (opcode & 0x0F00) >> 8

                #Fx07
                if nibThreeFour == 0x07: 
                    self.execute_LD_vx_dt(x)
                
                #Fx0A
                elif nibThreeFour == 0x0A:
                    self.execute_LD_vx_k(x)

                #Fx15
                elif nibThreeFour == 0x15:
                    self.execute_LD_DT_vx(x)

                #Fx18
                elif nibThreeFour == 0x18:
                    self.execute_LD_ST_vx(x)

                #Fx1E
                elif nibThreeFour == 0x1E:
                    self.execute_ADD_I_vx(x)

                #Fx29
                elif nibThreeFour == 0x29:
                    self.execute_LD_F_vx(x)

                #Fx33
                elif nibThreeFour == 0x33:
                    self.execute_LD_B_vx(x)

                #Fx55
                elif nibThreeFour == 0x55:
                    self.execute_LD_I_vx(x)

                #Fx65
                elif nibThreeFour == 0x65:
                    self.execute_LD_vx_I(x)

                else: 
                    print(f"UNIMP OPCODE: {hex(opcode)} AT PC:{hex(self.PC)}")
                    self.increment()
            

            case _:
                print(f"UNIMP OPCODE: {hex(opcode)} AT PC:{hex(self.PC)}")
                self.increment()

 