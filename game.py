import pygame
import sys
import random
import json
import os
from config import *
from player import Player
from enemy import Enemy
from powerup import PowerUp
from boss import BossEpisodico
from upgrades import MenuMejoras
from pygame import gfxdraw
from PIL import Image
import io
import math

class GIFHandler:
    def __init__(self, gif_path):
        self.frames = []
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_delay = 16  # 60 FPS (1000ms/60 ≈ 16.67ms)
        self.animation_speed = 1.0  # Velocidad de la animación (1.0 = normal)
        
        try:
            # Cargar el GIF usando PIL
            gif = Image.open(gif_path)
            print(f"GIF cargado: {gif_path}")
            print(f"Tamaño del GIF: {gif.size}")
            print(f"Modo del GIF: {gif.mode}")
            
            # Obtener la duración de cada frame del GIF
            self.frame_durations = []
            for frame in range(gif.n_frames):
                gif.seek(frame)
                try:
                    duration = gif.info.get('duration', 100)  # Duración en milisegundos
                    self.frame_durations.append(duration)
                except:
                    self.frame_durations.append(100)  # Valor por defecto si no hay duración
            
            # Convertir cada frame a una superficie de pygame
            for frame in range(gif.n_frames):
                gif.seek(frame)
                # Convertir el frame a RGBA
                frame_image = gif.convert('RGBA')
                # Redimensionar si es necesario
                if frame_image.size != (ANCHO, ALTO):
                    frame_image = frame_image.resize((ANCHO, ALTO), Image.Resampling.LANCZOS)
                
                # Convertir a formato de pygame
                frame_data = frame_image.tobytes()
                frame_surface = pygame.image.fromstring(frame_data, frame_image.size, 'RGBA')
                self.frames.append(frame_surface)
                
            print(f"Frames extraídos: {len(self.frames)}")
            
        except Exception as e:
            print(f"Error al cargar el GIF {gif_path}: {e}")
            self.frames = []

    def update(self):
        if not self.frames:
            return

        current_time = pygame.time.get_ticks()
        # Usar la duración específica del frame actual
        frame_duration = self.frame_durations[self.current_frame]
        # Aplicar la velocidad de animación
        adjusted_duration = frame_duration / self.animation_speed
        
        if current_time - self.last_update > adjusted_duration:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time

    def set_animation_speed(self, speed):
        """Ajusta la velocidad de la animación (1.0 = normal, 2.0 = doble velocidad, 0.5 = mitad de velocidad)"""
        self.animation_speed = max(0.1, min(5.0, speed))  # Limitar entre 0.1x y 5x

    def get_current_frame(self):
        if self.frames:
            return self.frames[self.current_frame]
        return None

class EfectoVisual:
    def __init__(self, x, y, tipo, duracion=1000):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.tiempo_inicio = pygame.time.get_ticks()
        self.duracion = duracion
        self.radio = 0
        self.alpha = 255
        self.color = ROJO if tipo == "explosion" else AMARILLO if tipo == "aura" else AZUL

    def actualizar(self):
        tiempo_actual = pygame.time.get_ticks()
        progreso = (tiempo_actual - self.tiempo_inicio) / self.duracion
        
        if self.tipo == "explosion":
            self.radio = 50 * (1 - progreso)
            self.alpha = int(255 * (1 - progreso))
        elif self.tipo == "aura":
            self.radio = 30 + 20 * math.sin(progreso * 10)
            self.alpha = int(128 + 127 * math.sin(progreso * 5))
        elif self.tipo == "onda":
            self.radio = 100 * progreso
            self.alpha = int(255 * (1 - progreso))
        
        return progreso < 1

    def dibujar(self, ventana):
        if self.alpha > 0:
            superficie = pygame.Surface((self.radio * 2, self.radio * 2), pygame.SRCALPHA)
            if self.tipo == "explosion":
                pygame.draw.circle(superficie, (*self.color, self.alpha), 
                                 (self.radio, self.radio), self.radio)
            elif self.tipo == "aura":
                pygame.draw.circle(superficie, (*self.color, self.alpha), 
                                 (self.radio, self.radio), self.radio, 3)
            elif self.tipo == "onda":
                pygame.draw.circle(superficie, (*self.color, self.alpha), 
                                 (self.radio, self.radio), self.radio, 2)
            ventana.blit(superficie, (self.x - self.radio, self.y - self.radio))

class Game:
    def __init__(self):
        # Mostrar pantalla de carga
        self.mostrar_pantalla_carga()
        
        self.jugador = Player()
        self.enemigos = []
        self.balas_jugador = []
        self.balas_enemigos = []
        self.powerups = []
        self.efectos = []
        self.nivel = 1
        self.ultimo_spawn = pygame.time.get_ticks()
        self.jefe_actual = None
        self.mejor_puntuacion = self.cargar_mejor_puntuacion()
        self.estado = "MENU"  # MENU, JUGANDO, GAME_OVER
        self.reloj = pygame.time.Clock()
        self.enemigos_derrotados = 0
        self.balas_jefe = []
        self.menu_mejoras = MenuMejoras()
        self.juego_pausado = False
        
        # Sistema de fondos simplificado
        self.fondos = {}
        self.fondo_actual = None
        
        # Precargar todos los fondos
        self.precargar_fondos()
        
        # Seleccionar fondo inicial
        self.fondo_actual = self.fondos.get('normal')
        print("Game inicializado con sistema de fondos simplificado")  # Debug

        self.efectos_visuales = []
        self.ultimo_efecto_jefe = 0
        self.intervalo_efectos_jefe = 500  # 500ms entre efectos

    def mostrar_pantalla_carga(self):
        """Muestra una pantalla de carga mientras se inicializan los assets"""
        # Crear una superficie para la pantalla de carga
        pantalla_carga = pygame.Surface((ANCHO, ALTO))
        pantalla_carga.fill(AZUL_OSCURO)
        
        # Dibujar fondo estrellado
        for _ in range(100):
            x = random.randint(0, ANCHO)
            y = random.randint(0, ALTO)
            pygame.draw.circle(pantalla_carga, BLANCO, (x, y), 1)
        
        # Título
        titulo = FUENTE_TITULO.render("GUNSLIME", True, NARANJA)
        sombra = FUENTE_TITULO.render("GUNSLIME", True, GRIS)
        pantalla_carga.blit(sombra, (ANCHO//2 - titulo.get_width()//2 + 5, ALTO//3 + 5))
        pantalla_carga.blit(titulo, (ANCHO//2 - titulo.get_width()//2, ALTO//3))
        
        # Barra de progreso
        barra_ancho = 400
        barra_alto = 20
        barra_x = ANCHO//2 - barra_ancho//2
        barra_y = ALTO//2
        
        # Dibujar barra base
        pygame.draw.rect(pantalla_carga, GRIS, 
                        (barra_x, barra_y, barra_ancho, barra_alto), 
                        border_radius=10)
        
        # Mostrar la pantalla inicial
        VENTANA.blit(pantalla_carga, (0, 0))
        pygame.display.flip()
        
        # Simular carga de assets
        for i in range(101):
            # Limpiar el área del texto de carga
            pygame.draw.rect(pantalla_carga, AZUL_OSCURO, 
                           (0, barra_y + 40, ANCHO, 50))
            
            # Actualizar barra de progreso
            progreso = i / 100
            pygame.draw.rect(pantalla_carga, NARANJA, 
                           (barra_x, barra_y, int(barra_ancho * progreso), barra_alto), 
                           border_radius=10)
            
            # Texto de carga
            texto_carga = FUENTE_MEDIANA.render(f"Cargando... {i}%", True, BLANCO)
            pantalla_carga.blit(texto_carga, 
                              (ANCHO//2 - texto_carga.get_width()//2, barra_y + 40))
            
            # Actualizar pantalla
            VENTANA.blit(pantalla_carga, (0, 0))
            pygame.display.flip()
            
            # Pequeña pausa para simular carga
            pygame.time.wait(15)  # Reducido de 20 a 15 para que sea más fluido
            
            # Mantener la ventana responsiva
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        
        # Transición suave al menú
        for alpha in range(255, 0, -5):
            pantalla_carga.set_alpha(alpha)
            VENTANA.blit(pantalla_carga, (0, 0))
            pygame.display.flip()
            pygame.time.wait(10)

    def precargar_fondos(self):
        """Precarga todos los fondos del juego"""
        try:
            # Fondo normal
            fondo_normal = GIFHandler('dist/bg4.gif')
            fondo_normal.set_animation_speed(1.5)
            self.fondos['normal'] = fondo_normal
            
            # Fondo del jefe
            fondo_jefe = GIFHandler('dist/bg3.gif')
            fondo_jefe.set_animation_speed(1.5)
            self.fondos['jefe'] = fondo_jefe
            
            print("Fondos precargados exitosamente")
        except Exception as e:
            print(f"Error al precargar fondos: {e}")

    def cambiar_fondo(self, tipo_fondo):
        """Cambia directamente al nuevo fondo"""
        if tipo_fondo in self.fondos:
            self.fondo_actual = self.fondos[tipo_fondo]
            print(f"Fondo cambiado a: {tipo_fondo}")

    def cargar_mejor_puntuacion(self):
        try:
            with open('mejor_puntuacion.json', 'r') as f:
                return json.load(f)['puntuacion']
        except:
            return 0

    def guardar_mejor_puntuacion(self):
        with open('mejor_puntuacion.json', 'w') as f:
            json.dump({'puntuacion': self.mejor_puntuacion}, f)

    def spawnear_enemigo(self):
        if self.jefe_actual is None and self.enemigos_derrotados >= BOSS_APARICION_ENEMIGOS and self.enemigos_derrotados % BOSS_APARICION_ENEMIGOS == 0:
            # Spawnear jefe
            x = ANCHO // 2 - JEFE_SIZE // 2
            y = ALTO // 2 - JEFE_SIZE // 2
            self.jefe_actual = BossEpisodico(x, y, self.nivel)
            # Efecto de explosión al aparecer el jefe
            self.efectos_visuales.append(EfectoVisual(x + JEFE_SIZE//2, y + JEFE_SIZE//2, "explosion", 1000))
            # Cambiar al fondo del jefe
            self.cambiar_fondo('jefe')
            # Cambiar música a la del jefe con transición suave
            if MUSICA_BOSS:
                try:
                    pygame.mixer.music.load(MUSICA_BOSS)
                    pygame.mixer.music.play(-1)  # -1 para loop infinito
                except Exception as e:
                    print(f"⚠️ Error al cambiar a la música del jefe: {e}")
            print(f"¡Jefe aparecido! Enemigos derrotados: {self.enemigos_derrotados}")  # Debug
        elif self.jefe_actual is None and len(self.enemigos) < MAX_ENEMIGOS_BASE + self.nivel // 2:
            # Solo spawnea enemigos comunes si no hay jefe
            lado = random.choice(["TOP", "BOTTOM", "LEFT", "RIGHT"])
            if lado == "TOP":
                x = random.randint(0, ANCHO - ENEMIGO_SIZE)
                y = 0
            elif lado == "BOTTOM":
                x = random.randint(0, ANCHO - ENEMIGO_SIZE)
                y = ALTO - ENEMIGO_SIZE
            elif lado == "LEFT":
                x = 0
                y = random.randint(0, ALTO - ENEMIGO_SIZE)
            else:  # RIGHT
                x = ANCHO - ENEMIGO_SIZE
                y = random.randint(0, ALTO - ENEMIGO_SIZE)
            
            self.enemigos.append(Enemy(x, y, self.nivel))

            # Colisión balas-jefe
            for bala in self.jugador.bullets[:]:
                if self.jefe_actual and (self.jefe_actual.x < bala['x'] < self.jefe_actual.x + self.jefe_actual.size and
                    self.jefe_actual.y < bala['y'] < self.jefe_actual.y + self.jefe_actual.size):
                    if self.jefe_actual.recibir_danio(bala['danio']):
                        self.jugador.puntuacion += 1000
                        self.enemigos_derrotados += 1
                        self.jugador.ganar_experiencia(50 * self.nivel)
                        if SONIDO_EXPLOSION:
                            SONIDO_EXPLOSION.play()
                        self.balas_jefe.clear()
                        self.jefe_actual = None
                        # Cambiar al fondo normal
                        self.cambiar_fondo('normal')
                        self.spawnear_powerup()
                    if bala in self.jugador.bullets:
                        self.jugador.bullets.remove(bala)

    def spawnear_jefe(self):
        if not self.jefe_actual:
            x = ANCHO // 2 - JEFE_SIZE // 2
            y = ALTO // 2 - JEFE_SIZE // 2
            self.jefe_actual = BossEpisodico(x, y, self.nivel)

    def spawnear_powerup(self):
        if random.random() < 0.1:  # 10% de probabilidad
            x = random.randint(0, ANCHO - 20)
            y = random.randint(0, ALTO - 20)
            self.powerups.append(PowerUp(x, y))

    def actualizar(self):
        # Actualizar fondo animado
        if self.fondo_actual:
            self.fondo_actual.update()

        # Actualizar efectos visuales
        self.efectos_visuales = [efecto for efecto in self.efectos_visuales if efecto.actualizar()]

        # Generar efectos del jefe
        if self.jefe_actual:
            tiempo_actual = pygame.time.get_ticks()
            if tiempo_actual - self.ultimo_efecto_jefe > self.intervalo_efectos_jefe:
                self.ultimo_efecto_jefe = tiempo_actual
                # Efecto de aura alrededor del jefe
                self.efectos_visuales.append(EfectoVisual(
                    self.jefe_actual.x + self.jefe_actual.size//2,
                    self.jefe_actual.y + self.jefe_actual.size//2,
                    "aura",
                    1000
                ))
                # Efecto de onda expansiva
                self.efectos_visuales.append(EfectoVisual(
                    self.jefe_actual.x + self.jefe_actual.size//2,
                    self.jefe_actual.y + self.jefe_actual.size//2,
                    "onda",
                    2000
                ))

        if self.juego_pausado:
            print("Juego pausado, esperando selección de mejora")  # Debug
            return

        # Actualizar jugador
        self.jugador.actualizar()

        # Verificar si el jugador subió de nivel
        if self.jugador.experiencia >= self.jugador.experiencia_siguiente:
            print(f"Experiencia actual: {self.jugador.experiencia}, Siguiente nivel: {self.jugador.experiencia_siguiente}")  # Debug
            self.jugador.subir_nivel()
            print("Activando menú de mejoras...")  # Debug
            self.menu_mejoras.activar()
            self.juego_pausado = True
            print(f"Estado después de activar - Menú activo: {self.menu_mejoras.activo}, Juego pausado: {self.juego_pausado}")  # Debug
            return

        # Spawnear enemigos
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_spawn > ENEMIGO_SPAWN_TIME:
            self.spawnear_enemigo()
            self.ultimo_spawn = tiempo_actual

        # Actualizar enemigos
        for enemigo in self.enemigos[:]:
            enemigo.mover(self.jugador.x, self.jugador.y)
            
            # Colisión directa con el jugador
            if (self.jugador.x < enemigo.x + enemigo.size and
                self.jugador.x + self.jugador.size > enemigo.x and
                self.jugador.y < enemigo.y + enemigo.size and
                self.jugador.y + self.jugador.size > enemigo.y):
                if self.jugador.recibir_danio(ENEMIGO_DANIO):
                    self.game_over()
                    return
            
            bala = enemigo.disparar(self.jugador.x, self.jugador.y)
            if bala:
                bala['danio'] = ENEMIGO_BALA_DANIO
                self.balas_enemigos.append(bala)

        # Actualizar balas enemigas
        for bala in self.balas_enemigos[:]:
            bala['x'] += bala['dx']
            bala['y'] += bala['dy']
            
            # Eliminar balas fuera de pantalla
            if (bala['x'] < -50 or bala['x'] > ANCHO + 50 or 
                bala['y'] < -50 or bala['y'] > ALTO + 50):
                self.balas_enemigos.remove(bala)
                continue
            
            # Colisión con el jugador
            if (self.jugador.x < bala['x'] < self.jugador.x + self.jugador.size and
                self.jugador.y < bala['y'] < self.jugador.y + self.jugador.size):
                if self.jugador.recibir_danio(bala['danio']):
                    self.game_over()
                    return
                self.balas_enemigos.remove(bala)

        # Actualizar jefe
        if self.jefe_actual:
            self.jefe_actual.actualizar_fase()
            self.jefe_actual.mover(self.jugador.x, self.jugador.y)
            
            # Colisión directa con el jefe
            if (self.jugador.x < self.jefe_actual.x + self.jefe_actual.size and
                self.jugador.x + self.jugador.size > self.jefe_actual.x and
                self.jugador.y < self.jefe_actual.y + self.jefe_actual.size and
                self.jugador.y + self.jugador.size > self.jefe_actual.y):
                if self.jugador.recibir_danio(BOSS_DANIO_BASE):
                    self.game_over()
                    return
            
            # Manejar disparos del jefe
            nuevas_balas = self.jefe_actual.disparar(self.jugador.x, self.jugador.y)
            if nuevas_balas:
                self.balas_jefe.extend(nuevas_balas)
            
            # Actualizar balas del jefe
            for bala in self.balas_jefe[:]:
                bala['x'] += bala['dx']
                bala['y'] += bala['dy']
                
                # Rebotar balas si tienen la propiedad
                if bala.get('rebota', False):
                    if bala['x'] <= 0 or bala['x'] >= ANCHO:
                        bala['dx'] *= -1
                        bala['rebotes'] = bala.get('rebotes', 0) + 1
                    if bala['y'] <= 0 or bala['y'] >= ALTO:
                        bala['dy'] *= -1
                        bala['rebotes'] = bala.get('rebotes', 0) + 1
                    
                    # Eliminar bala después de 3 rebotes
                    if bala.get('rebotes', 0) >= 3:
                        self.balas_jefe.remove(bala)
                        continue
                
                # Eliminar balas después de 5 segundos
                tiempo_actual = pygame.time.get_ticks()
                if tiempo_actual - bala.get('tiempo_creacion', tiempo_actual) > 5000:
                    self.balas_jefe.remove(bala)
                    continue
                
                # Colisión con el jugador
                if (self.jugador.x < bala['x'] < self.jugador.x + self.jugador.size and
                    self.jugador.y < bala['y'] < self.jugador.y + self.jugador.size):
                    if self.jugador.recibir_danio(bala['danio']):
                        self.game_over()
                        return
                    self.balas_jefe.remove(bala)
                    continue
                
                # Eliminar balas fuera de pantalla
                if (bala['x'] < -50 or bala['x'] > ANCHO + 50 or 
                    bala['y'] < -50 or bala['y'] > ALTO + 50):
                    self.balas_jefe.remove(bala)

        # Actualizar balas del jugador y verificar colisiones con enemigos y jefe
        for bala in self.jugador.bullets[:]:
            # Colisión con enemigos
            for enemigo in self.enemigos[:]:
                if (enemigo.x < bala['x'] < enemigo.x + enemigo.size and
                    enemigo.y < bala['y'] < enemigo.y + enemigo.size):
                    if enemigo.recibir_danio(bala['danio']):
                        self.enemigos.remove(enemigo)
                        self.enemigos_derrotados += 1
                        self.jugador.ganar_experiencia(10 * self.nivel)
                        self.jugador.puntuacion += 100 * self.nivel
                        self.spawnear_powerup()
                        if SONIDO_EXPLOSION:
                            SONIDO_EXPLOSION.play()
                    if bala in self.jugador.bullets:
                        self.jugador.bullets.remove(bala)
                    break
            
            # Colisión con el jefe
            if self.jefe_actual and (self.jefe_actual.x < bala['x'] < self.jefe_actual.x + self.jefe_actual.size and
                self.jefe_actual.y < bala['y'] < self.jefe_actual.y + self.jefe_actual.size):
                if self.jefe_actual.recibir_danio(bala['danio']):
                    # Efecto de explosión al recibir daño
                    self.efectos_visuales.append(EfectoVisual(
                        bala['x'], bala['y'], "explosion", 500))
                    self.jugador.puntuacion += 1000
                    self.enemigos_derrotados += 1
                    self.jugador.ganar_experiencia(50 * self.nivel)
                    if SONIDO_EXPLOSION:
                        SONIDO_EXPLOSION.play()
                    self.balas_jefe.clear()
                    self.jefe_actual = None
                    # Cambiar al fondo normal
                    self.cambiar_fondo('normal')
                    # Cambiar música a la normal con transición suave
                    if MUSICA_NORMAL:
                        try:
                            pygame.mixer.music.load(MUSICA_NORMAL)
                            pygame.mixer.music.play(-1)  # -1 para loop infinito
                        except Exception as e:
                            print(f"⚠️ Error al cambiar a la música normal: {e}")
                    self.spawnear_powerup()
                if bala in self.jugador.bullets:
                    self.jugador.bullets.remove(bala)

        # Actualizar powerups
        for powerup in self.powerups[:]:
            powerup.actualizar()
            if powerup.colisiona_con(self.jugador):
                powerup.aplicar(self.jugador)
                self.powerups.remove(powerup)
            elif pygame.time.get_ticks() - powerup.tiempo_aparicion >= powerup.duracion:
                self.powerups.remove(powerup)

        # Actualizar efectos
        for efecto in self.efectos[:]:
            efecto['duracion'] -= 1
            if efecto['duracion'] <= 0:
                self.efectos.remove(efecto)

    def dibujar(self):
        # Limpiar la pantalla completamente
        VENTANA.fill(AZUL_OSCURO)
        
        # Dibujar fondo actual
        if self.fondo_actual:
            frame = self.fondo_actual.get_current_frame()
            if frame:
                VENTANA.blit(frame, (0, 0))
        else:
            # Dibujar fondo estrellado como respaldo
            for _ in range(30):
                x = random.randint(0, ANCHO)
                y = random.randint(0, ALTO)
                pygame.draw.circle(VENTANA, BLANCO, (x, y), 1)
        
        # Dibujar efectos visuales
        for efecto in self.efectos_visuales:
            efecto.dibujar(VENTANA)
        
        # Dibujar powerups
        for powerup in self.powerups:
            powerup.dibujar(VENTANA)
        
        # Dibujar enemigos
        for enemigo in self.enemigos:
            enemigo.dibujar(VENTANA)
        
        # Dibujar jefe
        if self.jefe_actual:
            self.jefe_actual.dibujar(VENTANA)
        
        # Dibujar balas
        for bala in self.jugador.bullets:
            pygame.draw.rect(VENTANA, AMARILLO, 
                           (int(bala['x']), int(bala['y']), 6, 6), border_radius=3)
        for bala in self.balas_enemigos:
            pygame.draw.rect(VENTANA, ROJO, 
                           (int(bala['x']), int(bala['y']), 6, 6), border_radius=3)
        for bala in self.balas_jefe:
            pygame.draw.circle(VENTANA, ROJO, 
                             (int(bala['x']), int(bala['y'])), 5)
        
        # Dibujar jugador
        self.jugador.dibujar(VENTANA)
        
        # Dibujar HUD
        self.dibujar_hud()
        
        # Dibujar mira
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.line(VENTANA, BLANCO, (mouse_x - 10, mouse_y), 
                        (mouse_x + 10, mouse_y), 2)
        pygame.draw.line(VENTANA, BLANCO, (mouse_x, mouse_y - 10), 
                        (mouse_x, mouse_y + 10), 2)
        
        # Dibujar menú de mejoras si está activo
        if self.juego_pausado and self.menu_mejoras.activo:
            self.menu_mejoras.mostrar(VENTANA)
        
        # Actualizar la pantalla
        pygame.display.flip()

    def dibujar_hud(self):
        # Barra de experiencia
        ancho_barra = 250
        altura_barra = 20
        progreso = min(self.jugador.experiencia / self.jugador.experiencia_siguiente, 1)
        
        pygame.draw.rect(VENTANA, GRIS, (10, 10, ancho_barra, altura_barra), border_radius=5)
        pygame.draw.rect(VENTANA, NARANJA, (10, 10, ancho_barra * progreso, altura_barra), border_radius=5)
        pygame.draw.rect(VENTANA, BLANCO, (10, 10, ancho_barra, altura_barra), 2, border_radius=5)
        
        # Texto de nivel y experiencia
        nivel_texto = FUENTE_PIXEL.render(f"LVL: {self.jugador.nivel}", True, BLANCO)
        exp_texto = FUENTE_PIXEL.render(
            f"XP: {self.jugador.experiencia}/{int(self.jugador.experiencia_siguiente)}", 
            True, BLANCO)
        puntuacion_texto = FUENTE_PIXEL.render(
            f"PUNTOS: {self.jugador.puntuacion}", True, BLANCO)
        vida_texto = FUENTE_PIXEL.render(
            f"VIDA: {int(self.jugador.vida)}/{self.jugador.vida_max}", True, BLANCO)
        
        # Contador de enemigos para el siguiente jefe
        enemigos_restantes = BOSS_APARICION_ENEMIGOS - (self.enemigos_derrotados % BOSS_APARICION_ENEMIGOS)
        jefe_texto = FUENTE_PIXEL.render(
            f"SIGUIENTE JEFE: {enemigos_restantes}", True, AMARILLO)
        
        VENTANA.blit(nivel_texto, (15, 35))
        VENTANA.blit(exp_texto, (15, 60))
        VENTANA.blit(puntuacion_texto, (15, 85))
        VENTANA.blit(vida_texto, (15, 110))
        VENTANA.blit(jefe_texto, (15, 135))

        # Barra de vida del jugador
        vida_ancho = 200
        vida_altura = 15
        vida_progreso = self.jugador.vida / self.jugador.vida_max
        
        pygame.draw.rect(VENTANA, GRIS, (15, 160, vida_ancho, vida_altura), border_radius=5)
        pygame.draw.rect(VENTANA, VERDE, (15, 160, vida_ancho * vida_progreso, vida_altura), border_radius=5)
        pygame.draw.rect(VENTANA, BLANCO, (15, 160, vida_ancho, vida_altura), 2, border_radius=5)

        # Añadir instrucción de pantalla completa
        modo_texto = FUENTE_PEQUEÑA.render("Presiona F para cambiar modo pantalla", True, GRIS)
        VENTANA.blit(modo_texto, (ANCHO - modo_texto.get_width() - 15, ALTO - 30))

    def pantalla_inicio(self):
        while self.estado == "MENU":
            VENTANA.fill(AZUL_OSCURO)
            
            # Fondo estrellado animado
            tiempo_actual = pygame.time.get_ticks()
            for i in range(100):
                x = (tiempo_actual * 0.1 + i * 50) % ANCHO
                y = (tiempo_actual * 0.05 + i * 30) % ALTO
                brillo = int(128 + 127 * math.sin(tiempo_actual * 0.001 + i * 0.1))
                color = (brillo, brillo, brillo)
                pygame.draw.circle(VENTANA, color, (int(x), int(y)), 1)
            
            # Título con efecto de brillo
            brillo_titulo = int(128 + 127 * math.sin(tiempo_actual * 0.002))
            color_titulo = (255, brillo_titulo, 0)
            titulo = FUENTE_TITULO.render("GUNSLIME", True, color_titulo)
            sombra = FUENTE_TITULO.render("GUNSLIME", True, GRIS)
            
            # Efecto de escala para el título
            escala = 1.0 + 0.05 * math.sin(tiempo_actual * 0.003)
            titulo_escalado = pygame.transform.scale(titulo, 
                (int(titulo.get_width() * escala), int(titulo.get_height() * escala)))
            
            VENTANA.blit(sombra, (ANCHO//2 - titulo.get_width()//2 + 5, 150 + 5))
            VENTANA.blit(titulo_escalado, 
                        (ANCHO//2 - titulo_escalado.get_width()//2, 150))
            
            # Mejor puntuación con efecto de brillo
            brillo_punt = int(128 + 127 * math.sin(tiempo_actual * 0.001))
            color_punt = (brillo_punt, brillo_punt, brillo_punt)
            mejor_punt = FUENTE_MEDIANA.render(
                f"Mejor puntuación: {self.mejor_puntuacion}", True, color_punt)
            VENTANA.blit(mejor_punt, 
                        (ANCHO//2 - mejor_punt.get_width()//2, 250))
            
            # Instrucciones con efecto de parpadeo
            alpha = int(128 + 127 * math.sin(tiempo_actual * 0.005))
            texto_jugar = FUENTE_MEDIANA.render(
                "Presiona ENTER para jugar", True, (255, 255, 255, alpha))
            texto_controles = FUENTE_PEQUEÑA.render(
                "Controles: WASD para mover, Click para disparar", True, GRIS)
            
            VENTANA.blit(texto_jugar, 
                        (ANCHO//2 - texto_jugar.get_width()//2, 350))
            VENTANA.blit(texto_controles, 
                        (ANCHO//2 - texto_controles.get_width()//2, 400))
            
            # Versión del juego
            version = FUENTE_PEQUEÑA.render("v1.0", True, GRIS)
            VENTANA.blit(version, (ANCHO - version.get_width() - 10, ALTO - 30))
            
            pygame.display.update()
            
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_RETURN:
                        self.estado = "JUGANDO"
                        self.reiniciar_juego()

    def pantalla_game_over(self):
        while self.estado == "GAME_OVER":
            VENTANA.fill(AZUL_OSCURO)
            
            # Fondo estrellado
            for _ in range(100):
                x = random.randint(0, ANCHO)
                y = random.randint(0, ALTO)
                pygame.draw.circle(VENTANA, BLANCO, (x, y), 1)
            
            # Game Over
            texto = FUENTE_GRANDE.render("GAME OVER", True, ROJO)
            sombra = FUENTE_GRANDE.render("GAME OVER", True, GRIS)
            VENTANA.blit(sombra, (ANCHO//2 - texto.get_width()//2 + 5, 200 + 5))
            VENTANA.blit(texto, (ANCHO//2 - texto.get_width()//2, 200))
            
            # Estadísticas
            stats = FUENTE_MEDIANA.render(
                f"Alcanzaste el nivel {self.jugador.nivel}", True, BLANCO)
            puntuacion = FUENTE_MEDIANA.render(
                f"Puntuación: {self.jugador.puntuacion}", True, BLANCO)
            
            VENTANA.blit(stats, (ANCHO//2 - stats.get_width()//2, 280))
            VENTANA.blit(puntuacion, (ANCHO//2 - puntuacion.get_width()//2, 320))
            
            # Opciones
            reiniciar = FUENTE_MEDIANA.render(
                "Presiona R para reiniciar", True, VERDE)
            menu = FUENTE_MEDIANA.render(
                "Presiona M para volver al menú", True, BLANCO)
            salir = FUENTE_MEDIANA.render(
                "Presiona ESC para salir", True, GRIS)
            
            VENTANA.blit(reiniciar, (ANCHO//2 - reiniciar.get_width()//2, 380))
            VENTANA.blit(menu, (ANCHO//2 - menu.get_width()//2, 430))
            VENTANA.blit(salir, (ANCHO//2 - salir.get_width()//2, 480))
            
            pygame.display.update()
            
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_r:
                        self.estado = "JUGANDO"
                        self.reiniciar_juego()
                    if evento.key == pygame.K_m:
                        self.estado = "MENU"
                    if evento.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

    def reiniciar_juego(self):
        self.jugador = Player()
        self.enemigos = []
        self.balas_enemigos = []
        self.powerups = []
        self.efectos = []
        self.nivel = 1
        self.ultimo_spawn = pygame.time.get_ticks()
        self.jefe_actual = None
        self.enemigos_derrotados = 0
        self.balas_jefe = []
        self.score = 0
        self.juego_pausado = False
        
        # Asegurar que el fondo y la música estén en su estado normal
        self.cambiar_fondo('normal')
        
        # Iniciar música normal
        if MUSICA_NORMAL:
            try:
                pygame.mixer.music.stop()  # Detener cualquier música que esté sonando
                pygame.mixer.music.load(MUSICA_NORMAL)
                pygame.mixer.music.play(-1)  # -1 para loop infinito
                print("✅ Música normal iniciada")
            except Exception as e:
                print(f"⚠️ Error al reproducir la música: {e}")
        else:
            print("⚠️ No hay música disponible para reproducir")

    def game_over(self):
        if self.jugador.puntuacion > self.mejor_puntuacion:
            self.mejor_puntuacion = self.jugador.puntuacion
            self.guardar_mejor_puntuacion()
        
        # Restablecer fondo y música a normal
        self.cambiar_fondo('normal')
        if MUSICA_NORMAL:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(MUSICA_NORMAL)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"⚠️ Error al restablecer la música normal: {e}")
        
        if SONIDO_GAME_OVER:
            SONIDO_GAME_OVER.play()
        self.estado = "GAME_OVER"

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.game_over()
                if evento.key == pygame.K_f:  # Tecla F para cambiar modo pantalla
                    global MODO_PANTALLA_COMPLETA, VENTANA, ANCHO, ALTO
                    MODO_PANTALLA_COMPLETA = not MODO_PANTALLA_COMPLETA
                    if MODO_PANTALLA_COMPLETA:
                        VENTANA = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
                    else:
                        VENTANA = pygame.display.set_mode((ANCHO, ALTO))
            
            # Manejar eventos del menú de mejoras
            if self.juego_pausado and self.menu_mejoras.activo:
                print("Menú de mejoras activo, esperando selección...")  # Debug
                mejora_seleccionada = self.menu_mejoras.manejar_eventos(evento)
                if mejora_seleccionada:
                    print(f"Mejora seleccionada: {mejora_seleccionada.nombre}")  # Debug message
                    self.jugador.aplicar_mejora(mejora_seleccionada)
                    self.jugador.experiencia = 0  # Resetear experiencia después de aplicar la mejora
                    self.menu_mejoras.desactivar()
                    self.juego_pausado = False
                continue
        
        if not self.juego_pausado:
            # Manejar disparo automático
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:  # Click izquierdo
                bala = self.jugador.disparar(*pygame.mouse.get_pos())
                if bala and SONIDO_DISPARO:
                    SONIDO_DISPARO.play()
            
            teclas = pygame.key.get_pressed()
            dx, dy = 0, 0
            if teclas[pygame.K_a]:
                dx -= 1
            if teclas[pygame.K_d]:
                dx += 1
            if teclas[pygame.K_w]:
                dy -= 1
            if teclas[pygame.K_s]:
                dy += 1
            
            self.jugador.mover(dx, dy)

    def ejecutar(self):
        pygame.mouse.set_visible(False)
        
        while True:
            if self.estado == "MENU":
                self.pantalla_inicio()
            elif self.estado == "JUGANDO":
                self.manejar_eventos()
                self.actualizar()
                self.dibujar()
            elif self.estado == "GAME_OVER":
                self.pantalla_game_over()
            
            self.reloj.tick(60)

if __name__ == "__main__":
    juego = Game()
    juego.ejecutar() 