import pygame
import math
import random
from config import *

class BossEpisodico:
    def __init__(self, x, y, nivel):
        self.x = x
        self.y = y
        self.size = 120  # Más grande que un jefe normal
        self.vida_max = 200 + (nivel * 30)
        self.vida = self.vida_max
        self.vel = 2
        self.fase = 1
        self.ultimo_cambio_fase = pygame.time.get_ticks()
        self.tiempo_fase = 15000  # 15 segundos por fase
        self.patron_disparo = 0
        self.ultimo_patron = pygame.time.get_ticks()
        self.ultimo_disparo = 0
        self.velocidad_disparo = 1000
        self.angulo = 0
        self.radio_orbita = 200
        self.centro_x = ANCHO // 2
        self.centro_y = ALTO // 2
        self.efectos = []

    def actualizar_fase(self):
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_cambio_fase >= self.tiempo_fase:
            self.fase = (self.fase % 3) + 1
            self.ultimo_cambio_fase = tiempo_actual
            self.vel = 2 * (1.2 if self.fase == 2 else 0.8 if self.fase == 3 else 1)

    def mover(self, jugador_x, jugador_y):
        if self.fase == 1:  # Movimiento en círculo
            self.angulo += 0.02
            self.x = self.centro_x + math.cos(self.angulo) * self.radio_orbita
            self.y = self.centro_y + math.sin(self.angulo) * self.radio_orbita
        elif self.fase == 2:  # Persecución agresiva
            dx = jugador_x - self.x
            dy = jugador_y - self.y
            dist = math.hypot(dx, dy)
            if dist != 0:
                self.x += (dx/dist) * self.vel * 1.5
                self.y += (dy/dist) * self.vel * 1.5
        else:  # Fase 3: Movimiento errático
            self.x += random.uniform(-self.vel, self.vel)
            self.y += random.uniform(-self.vel, self.vel)
            self.x = max(0, min(self.x, ANCHO - self.size))
            self.y = max(0, min(self.y, ALTO - self.size))

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
                        'danio': 2,
                        'tiempo_creacion': tiempo_actual
                    })
            elif self.patron_disparo == 1:  # Disparo en cruz
                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                    balas.append({
                        'x': self.x + self.size // 2,
                        'y': self.y + self.size // 2,
                        'dx': dx * BALA_VEL,
                        'dy': dy * BALA_VEL,
                        'danio': 1,
                        'tiempo_creacion': tiempo_actual
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
                        'danio': 1,
                        'rebota': True,
                        'rebotes': 0,
                        'tiempo_creacion': tiempo_actual
                    })
            return balas
        return None

    def recibir_danio(self, danio):
        self.vida -= danio
        # Efecto visual de daño
        self.efectos.append({
            'tipo': 'flash',
            'duracion': 5,
            'color': ROJO
        })
        return self.vida <= 0

    def dibujar(self, ventana):
        # Efectos visuales
        for efecto in self.efectos[:]:
            if efecto['tipo'] == 'flash':
                pygame.draw.rect(ventana, efecto['color'], 
                               (self.x, self.y, self.size, self.size), 
                               border_radius=15)
                efecto['duracion'] -= 1
                if efecto['duracion'] <= 0:
                    self.efectos.remove(efecto)

        # Cuerpo principal
        color = MORADO if self.fase == 1 else ROJO if self.fase == 2 else AZUL
        pygame.draw.rect(ventana, color, 
                        (self.x, self.y, self.size, self.size), 
                        border_radius=15)
        
        # Detalles
        # Ojos
        ojo_radio = 15
        pygame.draw.circle(ventana, BLANCO, 
                         (self.x + self.size//3, self.y + self.size//3), 
                         ojo_radio)
        pygame.draw.circle(ventana, BLANCO, 
                         (self.x + 2*self.size//3, self.y + self.size//3), 
                         ojo_radio)
        pygame.draw.circle(ventana, NEGRO, 
                         (self.x + self.size//3, self.y + self.size//3), 
                         ojo_radio//2)
        pygame.draw.circle(ventana, NEGRO, 
                         (self.x + 2*self.size//3, self.y + self.size//3), 
                         ojo_radio//2)
        
        # Corona
        pygame.draw.rect(ventana, AMARILLO, 
                        (self.x - 10, self.y - 15, self.size + 20, 10))
        for i in range(7):
            pygame.draw.rect(ventana, AMARILLO, 
                           (self.x + i * (self.size//6), self.y - 30, 5, 20))
        
        # Barra de vida
        vida_ancho = self.size
        vida_altura = 15
        vida_progreso = self.vida / self.vida_max
        
        pygame.draw.rect(ventana, GRIS, 
                        (self.x, self.y - 40, vida_ancho, vida_altura))
        pygame.draw.rect(ventana, VERDE, 
                        (self.x, self.y - 40, vida_ancho * vida_progreso, vida_altura))
        pygame.draw.rect(ventana, BLANCO, 
                        (self.x, self.y - 40, vida_ancho, vida_altura), 2) 