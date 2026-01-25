import pygame

# Key pad mapping is as so: 

# 1 2 3 C      1 2 3 4      0 1 2 3 
# 4 5 6 D  =>  q w e r  =>  4 5 6 7
# 7 8 9 E  =>  a s d f  =>  8 9 10 11
# A 0 B F      z x c v      12 13 14 15

class controls:
    def __init__(self):
        pygame.init()
        self.keys = [False for _ in range(16)]
        self.map = {
            pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
            pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
            pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
            pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF,
        }

    def input_handler(self, cpu):
        self.keys = [False for _ in range(16)]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cpu.running = False
            
            elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                if event.key in self.map:
                    self.keys[self.map[event.key]] = (event.type == pygame.KEYDOWN)

        cpu.keys = self.keys
                    