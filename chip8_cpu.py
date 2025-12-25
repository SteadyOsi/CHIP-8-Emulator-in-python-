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

    def decode(opcode):
        nibOne = (opcode >> 12) & 0xF
        
        match nibOne:
            case 0x0:
                print(f"{opcaode} family: CLS/RST")
            case 0x1:
                print(f"{opcaode} family: JP nnn")
            case 0x6:
                print(f"{opcaode} family: LD Vx, kk")
            case 0x7
                print(f"{opcaode} family: ADD Vx, kk")