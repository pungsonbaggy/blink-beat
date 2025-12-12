import random
import pygame

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel = [random.randint(-4, 4), random.randint(-8, -2)]
        self.size = random.randint(3, 6)
        self.life = 30

    def update(self):
        self.x += self.vel[0]
        self.y += self.vel[1]
        self.life -= 1

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def spawn(self, x, y):
        for _ in range(15):
            self.particles.append(Particle(x, y))

    def draw(self, screen):
        for p in self.particles[:]:
            if p.life <= 0:
                self.particles.remove(p)
                continue
            pygame.draw.circle(screen, (255, 200, 50), (int(p.x), int(p.y)), p.size)
            p.update()
