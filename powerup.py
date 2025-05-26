import pygame
import random
from config import *

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20
        self.tipo = random.choice(list(POWERUP_TIPOS.keys()))
        self.color = POWERUP_TIPOS[self.tipo]['color']
        self.efecto = POWERUP_TIPOS[self.tipo]['efecto']
        self.tiempo_aparicion = pygame.time.get_ticks()
        self.duracion = 10000  # 10 segundos en pantalla
        self.parpadeo = False
        self.ultimo_parpadeo = pygame.time.get_ticks()

    def actualizar(self):
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.tiempo_aparicion >= self.duracion - 2000:  # Últimos 2 segundos
            if tiempo_actual - self.ultimo_parpadeo >= 200:  # Parpadeo cada 200ms
                self.parpadeo = not self.parpadeo
                self.ultimo_parpadeo = tiempo_actual

    def aplicar(self, jugador):
        tiempo_actual = pygame.time.get_ticks()
        jugador.powerups[self.tipo] = {
            'efecto': self.efecto,
            'tiempo': tiempo_actual,
            'color': self.color
        }
        if SONIDO_POWERUP:
            SONIDO_POWERUP.play()

    def dibujar(self, ventana):
        if not self.parpadeo:
            # Dibujar el powerup
            pygame.draw.rect(ventana, self.color, 
                           (self.x, self.y, self.size, self.size), 
                           border_radius=5)
            
            # Dibujar símbolo según el tipo
            if self.tipo == 'VELOCIDAD':
                pygame.draw.line(ventana, BLANCO, 
                               (self.x + 5, self.y + self.size//2),
                               (self.x + self.size - 5, self.y + self.size//2), 2)
                pygame.draw.polygon(ventana, BLANCO, [
                    (self.x + self.size - 5, self.y + self.size//2),
                    (self.x + self.size - 10, self.y + self.size//2 - 5),
                    (self.x + self.size - 10, self.y + self.size//2 + 5)
                ])
            elif self.tipo == 'DANIO':
                pygame.draw.line(ventana, BLANCO,
                               (self.x + self.size//2, self.y + 5),
                               (self.x + self.size//2, self.y + self.size - 5), 2)
                pygame.draw.line(ventana, BLANCO,
                               (self.x + 5, self.y + self.size//2),
                               (self.x + self.size - 5, self.y + self.size//2), 2)
            elif self.tipo == 'VIDA':
                pygame.draw.circle(ventana, BLANCO,
                                 (self.x + self.size//2, self.y + self.size//2),
                                 self.size//3)
            elif self.tipo == 'BALAS':
                for i in range(3):
                    pygame.draw.rect(ventana, BLANCO,
                                   (self.x + 5 + i*5, self.y + 5,
                                    self.size - 10, self.size - 10), 1)

    def colisiona_con(self, jugador):
        return (jugador.x < self.x + self.size and
                jugador.x + jugador.size > self.x and
                jugador.y < self.y + self.size and
                jugador.y + jugador.size > self.y) 