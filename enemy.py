import pygame
import math
import random
from config import *

class Enemy:
    def __init__(self, x, y, nivel):
        self.x = x
        self.y = y
        self.size = ENEMIGO_SIZE
        self.vida_max = ENEMIGO_VIDA_BASE + nivel  # Aumentado el escalado por nivel
        self.vida = self.vida_max
        self.vel = ENEMIGO_VEL_BASE + (nivel * 0.15)  # Aumentado el escalado por nivel
        self.tipo = random.choice(['NORMAL', 'RAPIDO', 'TANQUE'])
        self.ajustar_por_tipo()
        self.ultimo_disparo = 0
        self.velocidad_disparo = 1500  # Reducido de 2000 a 1500 para más ataques

    def ajustar_por_tipo(self):
        if self.tipo == 'RAPIDO':
            self.vel *= 1.8  # Aumentado de 1.5 a 1.8
            self.vida_max = int(self.vida_max * 0.6)  # Reducido de 0.7 a 0.6
            self.velocidad_disparo = 1000  # Más rápido en disparos
        elif self.tipo == 'TANQUE':
            self.vel *= 0.6  # Reducido de 0.7 a 0.6
            self.vida_max = int(self.vida_max * 2.0)  # Aumentado de 1.5 a 2.0
            self.velocidad_disparo = 2500  # Más lento en disparos
        self.vida = self.vida_max

    def mover(self, jugador_x, jugador_y):
        dx = jugador_x - self.x
        dy = jugador_y - self.y
        distancia = math.hypot(dx, dy)
        if distancia != 0:
            dx /= distancia
            dy /= distancia
            self.x += dx * self.vel
            self.y += dy * self.vel

    def recibir_danio(self, danio):
        self.vida -= danio
        return self.vida <= 0

    def disparar(self, jugador_x, jugador_y):
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_disparo >= self.velocidad_disparo:
            self.ultimo_disparo = tiempo_actual
            dx = jugador_x - self.x
            dy = jugador_y - self.y
            distancia = math.hypot(dx, dy)
            if distancia == 0:
                return None
            dx /= distancia
            dy /= distancia
            return {
                'x': self.x + self.size // 2,
                'y': self.y + self.size // 2,
                'dx': dx * BALA_VEL * 0.7,
                'dy': dy * BALA_VEL * 0.7,
                'danio': 1
            }
        return None

    def dibujar(self, ventana):
        # Dibujar cuerpo
        color = ROJO if self.tipo == 'NORMAL' else AMARILLO if self.tipo == 'RAPIDO' else MORADO
        pygame.draw.rect(ventana, color, (self.x, self.y, self.size, self.size), border_radius=5)
        
        # Ojos
        pygame.draw.circle(ventana, BLANCO, (self.x + 10, self.y + 12), 5)
        pygame.draw.circle(ventana, BLANCO, (self.x + self.size - 10, self.y + 12), 5)
        pygame.draw.circle(ventana, NEGRO, (self.x + 10, self.y + 12), 2)
        pygame.draw.circle(ventana, NEGRO, (self.x + self.size - 10, self.y + 12), 2)
        
        # Barra de vida
        vida_ancho = self.size
        vida_altura = 5
        vida_progreso = self.vida / self.vida_max
        
        pygame.draw.rect(ventana, GRIS, (self.x, self.y - 10, vida_ancho, vida_altura))
        pygame.draw.rect(ventana, VERDE, (self.x, self.y - 10, vida_ancho * vida_progreso, vida_altura))
        pygame.draw.rect(ventana, BLANCO, (self.x, self.y - 10, vida_ancho, vida_altura), 1)

class Boss(Enemy):
    def __init__(self, x, y, nivel):
        super().__init__(x, y, nivel)
        self.size = JEFE_SIZE
        self.vida_max = JEFE_VIDA_BASE + (nivel * 10)
        self.vida = self.vida_max
        self.vel = JEFE_VEL_BASE
        self.fase = 1
        self.ultimo_cambio_fase = pygame.time.get_ticks()
        self.tiempo_fase = 10000  # 10 segundos por fase
        self.patron_disparo = 0
        self.ultimo_patron = pygame.time.get_ticks()

    def actualizar_fase(self):
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_cambio_fase >= self.tiempo_fase:
            self.fase = (self.fase % 3) + 1
            self.ultimo_cambio_fase = tiempo_actual
            self.vel = JEFE_VEL_BASE * (1.2 if self.fase == 2 else 0.8 if self.fase == 3 else 1)

    def disparar(self, jugador_x, jugador_y):
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_disparo >= self.velocidad_disparo:
            self.ultimo_disparo = tiempo_actual
            
            # Cambiar patrón de disparo cada 5 segundos
            if tiempo_actual - self.ultimo_patron >= 5000:
                self.patron_disparo = (self.patron_disparo + 1) % 3
                self.ultimo_patron = tiempo_actual

            balas = []
            if self.patron_disparo == 0:  # Disparo directo
                dx = jugador_x - self.x
                dy = jugador_y - self.y
                distancia = math.hypot(dx, dy)
                if distancia != 0:
                    dx /= distancia
                    dy /= distancia
                    balas.append({
                        'x': self.x + self.size // 2,
                        'y': self.y + self.size // 2,
                        'dx': dx * BALA_VEL,
                        'dy': dy * BALA_VEL,
                        'danio': 2
                    })
            elif self.patron_disparo == 1:  # Disparo en cruz
                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                    balas.append({
                        'x': self.x + self.size // 2,
                        'y': self.y + self.size // 2,
                        'dx': dx * BALA_VEL,
                        'dy': dy * BALA_VEL,
                        'danio': 1
                    })
            else:  # Disparo circular
                for angulo in range(0, 360, 45):
                    rad = math.radians(angulo)
                    dx = math.cos(rad)
                    dy = math.sin(rad)
                    balas.append({
                        'x': self.x + self.size // 2,
                        'y': self.y + self.size // 2,
                        'dx': dx * BALA_VEL * 0.7,
                        'dy': dy * BALA_VEL * 0.7,
                        'danio': 1
                    })
            return balas
        return None

    def dibujar(self, ventana):
        # Dibujar cuerpo principal
        color = MORADO if self.fase == 1 else ROJO if self.fase == 2 else AZUL
        pygame.draw.rect(ventana, color, (self.x, self.y, self.size, self.size), border_radius=10)
        
        # Detalles del jefe
        # Ojos
        ojo_radio = 10
        pygame.draw.circle(ventana, BLANCO, (self.x + self.size//3, self.y + self.size//3), ojo_radio)
        pygame.draw.circle(ventana, BLANCO, (self.x + 2*self.size//3, self.y + self.size//3), ojo_radio)
        pygame.draw.circle(ventana, NEGRO, (self.x + self.size//3, self.y + self.size//3), ojo_radio//2)
        pygame.draw.circle(ventana, NEGRO, (self.x + 2*self.size//3, self.y + self.size//3), ojo_radio//2)
        
        # Corona
        pygame.draw.rect(ventana, AMARILLO, (self.x - 5, self.y - 10, self.size + 10, 5))
        for i in range(5):
            pygame.draw.rect(ventana, AMARILLO, 
                           (self.x + i * (self.size//4), self.y - 20, 5, 15))
        
        # Barra de vida
        vida_ancho = self.size
        vida_altura = 10
        vida_progreso = self.vida / self.vida_max
        
        pygame.draw.rect(ventana, GRIS, (self.x, self.y - 30, vida_ancho, vida_altura))
        pygame.draw.rect(ventana, VERDE, (self.x, self.y - 30, vida_ancho * vida_progreso, vida_altura))
        pygame.draw.rect(ventana, BLANCO, (self.x, self.y - 30, vida_ancho, vida_altura), 2) 