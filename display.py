import pygame

class Graphics:
    def __init__(self):
        self.scale = 0
        self.WIDTH = 64
        self.HEIGHT = 32
        self.screen = 0
        self.cpuFrameBuffer = [[False for _ in range(64)]for _ in range(32)]

    

    def init_display(self, scale):
        self.WIDTH *= scale
        self.HEIGHT *= scale

        pygame.init()

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("CHIP-8-PY")

    def render(self, cpu, screen, scale):
        