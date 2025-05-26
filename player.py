import pygame
import math
from config import *

class Player:
    def __init__(self):
        self.x = ANCHO // 2
        self.y = ALTO // 2
        self.size = JUGADOR_SIZE
        self.vel = JUGADOR_VEL
        self.vida = JUGADOR_VIDA_MAX
        self.vida_max = JUGADOR_VIDA_MAX
        self.direccion = "UP"
        self.ultimo_disparo = 0
        self.velocidad_disparo = TIEMPO_ENTRE_DISPAROS
        self.powerups = {}
        self.invulnerable = False
        self.tiempo_invulnerable = 0
        self.puntuacion = 0
        self.nivel = 1
        self.experiencia = 0
        self.experiencia_siguiente = EXPERIENCIA_BASE
        self.bullets = []  # Lista para almacenar las balas del jugador
        self.danio_base = BALA_DANIO_BASE
        
        # Mejoras permanentes
        self.multiplicador_danio = 1.0
        self.multiplicador_velocidad = 1.0

    def aplicar_mejora(self, mejora):
        if mejora.nombre == "Más Daño":
            self.multiplicador_danio *= mejora.efecto
        elif mejora.nombre == "Más Vida":
            self.vida_max += mejora.efecto
            self.vida = self.vida_max
        elif mejora.nombre == "Más Velocidad":
            self.multiplicador_velocidad *= mejora.efecto

    def mover(self, dx, dy):
        # Aplicar velocidad modificada por powerups y mejoras permanentes
        vel_actual = self.vel * self.multiplicador_velocidad
        if 'VELOCIDAD' in self.powerups:
            vel_actual *= self.powerups['VELOCIDAD']['efecto']

        # Normalizar para movimiento diagonal
        if dx != 0 or dy != 0:
            magnitud = math.sqrt(dx**2 + dy**2)
            dx = dx / magnitud
            dy = dy / magnitud

        self.x += int(dx * vel_actual)
        self.y += int(dy * vel_actual)

        # Mantener dentro de los límites
        self.x = max(0, min(self.x, ANCHO - self.size))
        self.y = max(0, min(self.y, ALTO - self.size))

    def disparar(self, mouse_x, mouse_y):
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_disparo >= self.velocidad_disparo:
            self.ultimo_disparo = tiempo_actual
            dx = mouse_x - (self.x + self.size // 2)
            dy = mouse_y - (self.y + self.size // 2)
            distancia = math.hypot(dx, dy)
            if distancia == 0:
                return None
            dx /= distancia
            dy /= distancia
            bala = {
                'x': self.x + self.size // 2,
                'y': self.y + self.size // 2,
                'dx': dx * BALA_VEL,
                'dy': dy * BALA_VEL,
                'danio': self.calcular_danio()
            }
            self.bullets.append(bala)
            return bala
        return None

    def calcular_danio(self):
        danio = self.danio_base * self.multiplicador_danio
        if 'DANIO' in self.powerups:
            danio *= self.powerups['DANIO']['efecto']
        return danio

    def recibir_danio(self, danio):
        tiempo_actual = pygame.time.get_ticks()
        if not self.invulnerable:
            self.vida -= danio
            self.invulnerable = True
            self.tiempo_invulnerable = tiempo_actual
            print(f"Vida restante: {self.vida}/{self.vida_max}")  # Debug
            if self.vida <= 0:
                return True
        return False

    def actualizar(self):
        tiempo_actual = pygame.time.get_ticks()
        # Regeneración de vida
        if self.vida < self.vida_max:
            self.vida = min(self.vida_max, self.vida + JUGADOR_VIDA_REGEN)

        # Actualizar invulnerabilidad (1 segundo de invulnerabilidad después de recibir daño)
        if self.invulnerable and tiempo_actual - self.tiempo_invulnerable > 1000:
            self.invulnerable = False

        # Actualizar powerups
        powerups_activos = {}
        for tipo, datos in self.powerups.items():
            if tiempo_actual - datos['tiempo'] < POWERUP_DURACION:
                powerups_activos[tipo] = datos
        self.powerups = powerups_activos

        # Actualizar balas
        for bala in self.bullets[:]:
            bala['x'] += bala['dx']
            bala['y'] += bala['dy']
            
            # Eliminar balas fuera de pantalla
            if (bala['x'] < 0 or bala['x'] > ANCHO or 
                bala['y'] < 0 or bala['y'] > ALTO):
                self.bullets.remove(bala)

    def ganar_experiencia(self, cantidad):
        self.experiencia += cantidad
        if self.experiencia >= self.experiencia_siguiente:
            self.subir_nivel()

    def subir_nivel(self):
        print(f"Subiendo de nivel {self.nivel} a {self.nivel + 1}")  # Debug message
        self.nivel += 1
        # No resetear la experiencia aquí, se hará después de seleccionar la mejora
        self.experiencia_siguiente = int(EXPERIENCIA_BASE * (EXPERIENCIA_MULTIPLICADOR ** (self.nivel - 1)))
        self.vida_max += 10
        self.vida = self.vida_max
        if SONIDO_NIVEL:
            SONIDO_NIVEL.play()

    def dibujar(self, ventana):
        # Dibujar cuerpo principal
        color = VERDE if not self.invulnerable else (VERDE[0]//2, VERDE[1]//2, VERDE[2]//2)
        pygame.draw.rect(ventana, color, (self.x, self.y, self.size, self.size), border_radius=10)
        
        # Dibujar detalles del slime
        # Ojos
        ojo_radio = 6
        ojo_color = BLANCO
        pupila_color = NEGRO
        
        # Posición de los ojos basada en la dirección
        if self.direccion == "UP":
            ojo1_pos = (self.x + self.size//3, self.y + self.size//3)
            ojo2_pos = (self.x + 2*self.size//3, self.y + self.size//3)
        elif self.direccion == "DOWN":
            ojo1_pos = (self.x + self.size//3, self.y + 2*self.size//3)
            ojo2_pos = (self.x + 2*self.size//3, self.y + 2*self.size//3)
        elif self.direccion == "LEFT":
            ojo1_pos = (self.x + self.size//3, self.y + self.size//3)
            ojo2_pos = (self.x + self.size//3, self.y + 2*self.size//3)
        else:  # RIGHT
            ojo1_pos = (self.x + 2*self.size//3, self.y + self.size//3)
            ojo2_pos = (self.x + 2*self.size//3, self.y + 2*self.size//3)
        
        pygame.draw.circle(ventana, ojo_color, ojo1_pos, ojo_radio)
        pygame.draw.circle(ventana, ojo_color, ojo2_pos, ojo_radio)
        pygame.draw.circle(ventana, pupila_color, ojo1_pos, ojo_radio//2)
        pygame.draw.circle(ventana, pupila_color, ojo2_pos, ojo_radio//2)
        
        # Manchas decorativas
        pygame.draw.circle(ventana, VERDE_OSCURO, (self.x + 10, self.y + 10), 4)
        pygame.draw.circle(ventana, VERDE_OSCURO, (self.x + self.size - 10, self.y + self.size - 10), 4)
        pygame.draw.circle(ventana, VERDE_OSCURO, (self.x + self.size - 10, self.y + 10), 4)
        
        # Dibujar barra de vida
        vida_ancho = self.size
        vida_altura = 5
        vida_progreso = self.vida / self.vida_max
        
        pygame.draw.rect(ventana, GRIS, (self.x, self.y - 10, vida_ancho, vida_altura))
        pygame.draw.rect(ventana, VERDE, (self.x, self.y - 10, vida_ancho * vida_progreso, vida_altura))
        pygame.draw.rect(ventana, BLANCO, (self.x, self.y - 10, vida_ancho, vida_altura), 1)

        # Dibujar efectos de powerups
        for i, (tipo, datos) in enumerate(self.powerups.items()):
            pygame.draw.circle(ventana, datos['color'], 
                             (self.x + self.size + 10, self.y + i * 10), 3) 