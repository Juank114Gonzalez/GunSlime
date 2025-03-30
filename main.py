import pygame
import sys
import random
import math

# Inicializar Pygame
pygame.init()

# Definir las dimensiones de la ventana
ANCHO = 800
ALTO = 600
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("GUNSLIME")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 50, 50)
VERDE = (50, 255, 100)
VERDE_OSCURO = (0, 100, 0)
AMARILLO = (255, 255, 0)
GRIS = (100, 100, 100)
AZUL_OSCURO = (0, 0, 100)
NARANJA = (255, 165, 0)
ROSA = (255, 100, 150)

# Configuración del jugador
jugador_size = 40
jugador_x = ANCHO // 2
jugador_y = ALTO // 2
jugador_vel = 5
jugador_dir = "UP"

# Sistema de niveles
nivel = 1
experiencia = 0
experiencia_siguiente_nivel = 100
niveles = [100 * (1.5 ** i) for i in range(20)]  # Experiencia requerida para cada nivel

# Configuración de los enemigos
enemigos = []  # Cada enemigo será [x, y, vida_max, vida_actual]
enemigo_size = 35
enemigo_vel = 1.5
enemigo_vida_base = 2
enemigo_spawn_time = 1000  # Milisegundos
ultimo_spawn = pygame.time.get_ticks()
max_enemigos = 5

# Configuración de las balas
balas = []
bala_vel = 7
bala_danio = 1
max_balas = 5

# Efectos visuales
efectos = []  # Para feedback visual

# Reloj para controlar los FPS
reloj = pygame.time.Clock()

# Fuentes - Usamos una fuente pixel art para el HUD
try:
    fuente_pixel = pygame.font.Font("PressStart2P-Regular.ttf", 16)  # Más grande
except:
    fuente_pixel = pygame.font.SysFont("Arial", 16)  # Fallback si no encuentra la fuente

fuente_pequena = pygame.font.SysFont("Arial", 20)  # Aumentado
fuente_mediana = pygame.font.SysFont("Arial", 28)  # Aumentado
fuente_grande = pygame.font.SysFont("Arial", 56)  # Aumentado
fuente_titulo = pygame.font.SysFont("Impact", 72)  # Aumentado

def dibujar_jugador(x, y, direccion):
    # Cuerpo del jugador (similar a enemigos pero con arma)
    pygame.draw.rect(VENTANA, VERDE, (x, y, jugador_size, jugador_size), border_radius=5)
    
    # Manchas verdes oscuras
    pygame.draw.circle(VENTANA, VERDE_OSCURO, (x + 10, y + 10), 4)
    pygame.draw.circle(VENTANA, VERDE_OSCURO, (x + jugador_size - 10, y + jugador_size - 10), 4)
    pygame.draw.circle(VENTANA, VERDE_OSCURO, (x + jugador_size - 10, y + 10), 4)
    
    # Ojos del jugador
    pygame.draw.circle(VENTANA, BLANCO, (x + 15, y + 15), 5)
    pygame.draw.circle(VENTANA, BLANCO, (x + jugador_size - 15, y + 15), 5)
    pygame.draw.circle(VENTANA, NEGRO, (x + 15, y + 15), 2)
    pygame.draw.circle(VENTANA, NEGRO, (x + jugador_size - 15, y + 15), 2)
    
    # Arma según dirección
    arma_largo = 20
    if direccion == "UP":
        pygame.draw.rect(VENTANA, NARANJA, (x + jugador_size//2 - 3, y - arma_largo, 6, arma_largo), border_radius=3)
    elif direccion == "DOWN":
        pygame.draw.rect(VENTANA, NARANJA, (x + jugador_size//2 - 3, y + jugador_size, 6, arma_largo), border_radius=3)
    elif direccion == "LEFT":
        pygame.draw.rect(VENTANA, NARANJA, (x - arma_largo, y + jugador_size//2 - 3, arma_largo, 6), border_radius=3)
    elif direccion == "RIGHT":
        pygame.draw.rect(VENTANA, NARANJA, (x + jugador_size, y + jugador_size//2 - 3, arma_largo, 6), border_radius=3)

def disparar():
    if len(balas) < max_balas:
        arma_largo = 20
        if jugador_dir == "UP":
            balas.append([jugador_x + jugador_size//2 - 2, jugador_y - arma_largo, 0, -bala_vel])
        elif jugador_dir == "DOWN":
            balas.append([jugador_x + jugador_size//2 - 2, jugador_y + jugador_size + arma_largo - 10, 0, bala_vel])
        elif jugador_dir == "LEFT":
            balas.append([jugador_x - arma_largo + 10, jugador_y + jugador_size//2 - 2, -bala_vel, 0])
        elif jugador_dir == "RIGHT":
            balas.append([jugador_x + jugador_size + arma_largo - 10, jugador_y + jugador_size//2 - 2, bala_vel, 0])

def mover_balas():
    global experiencia, nivel, experiencia_siguiente_nivel, bala_danio
    
    # Aumentar daño según nivel
    bala_danio = 1 + nivel // 3
    
    for bala in balas[:]:
        bala[0] += bala[2]
        bala[1] += bala[3]
        
        # Eliminar balas fuera de pantalla
        if bala[0] < 0 or bala[0] > ANCHO or bala[1] < 0 or bala[1] > ALTO:
            balas.remove(bala)
            continue
            
        for enemigo in enemigos[:]:
            # Detectar colisión bala-enemigo
            if (enemigo[0] < bala[0] < enemigo[0] + enemigo_size and
                enemigo[1] < bala[1] < enemigo[1] + enemigo_size):
                
                # Reducir vida del enemigo
                enemigo[3] -= bala_danio
                
                # Añadir efecto visual
                efectos.append([bala[0], bala[1], 10, ROJO])  # x, y, duración, color
                
                # Eliminar bala
                if bala in balas:
                    balas.remove(bala)
                
                # Si el enemigo muere
                if enemigo[3] <= 0:
                    enemigos.remove(enemigo)
                    experiencia += 10 * nivel
                    
                    # Añadir efecto de muerte
                    for _ in range(5):
                        efectos.append([
                            enemigo[0] + enemigo_size//2, 
                            enemigo[1] + enemigo_size//2,
                            random.randint(10, 20),
                            random.choice([ROJO, NARANJA, AMARILLO])
                        ])
                    
                    # Subir de nivel si se alcanza la experiencia requerida
                    if experiencia >= experiencia_siguiente_nivel:
                        nivel += 1
                        experiencia = 0
                        experiencia_siguiente_nivel = niveles[nivel-1] if nivel <= len(niveles) else niveles[-1]
                        
                        # Efecto de subida de nivel
                        for _ in range(10):
                            efectos.append([
                                jugador_x + jugador_size//2,
                                jugador_y + jugador_size//2,
                                random.randint(15, 30),
                                VERDE
                            ])
                break

def spawnear_enemigos():
    global ultimo_spawn, max_enemigos, enemigo_vida_base
    
    # Ajustar dificultad según nivel
    max_enemigos = 5 + nivel // 2
    vida_enemigo = enemigo_vida_base + nivel // 4
    
    if len(enemigos) < max_enemigos and pygame.time.get_ticks() - ultimo_spawn > enemigo_spawn_time:
        lado = random.choice(["TOP", "BOTTOM", "LEFT", "RIGHT"])
        if lado == "TOP":
            x = random.randint(0, ANCHO - enemigo_size)
            y = 0
        elif lado == "BOTTOM":
            x = random.randint(0, ANCHO - enemigo_size)
            y = ALTO - enemigo_size
        elif lado == "LEFT":
            x = 0
            y = random.randint(0, ALTO - enemigo_size)
        elif lado == "RIGHT":
            x = ANCHO - enemigo_size
            y = random.randint(0, ALTO - enemigo_size)
        
        enemigos.append([x, y, vida_enemigo, vida_enemigo])  # x, y, vida_max, vida_actual
        ultimo_spawn = pygame.time.get_ticks()

def pantalla_inicio():
    while True:
        VENTANA.fill(AZUL_OSCURO)
        
        # Fondo estrellado
        for _ in range(100):
            x = random.randint(0, ANCHO)
            y = random.randint(0, ALTO)
            pygame.draw.circle(VENTANA, BLANCO, (x, y), 1)
        
        # Título del juego
        titulo = fuente_titulo.render("GUNSLIME", True, NARANJA)
        sombra = fuente_titulo.render("GUNSLIME", True, GRIS)
        VENTANA.blit(sombra, (ANCHO//2 - titulo.get_width()//2 + 5, 150 + 5))
        VENTANA.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 150))
        
        # Dibujar jugador y enemigo de ejemplo
        dibujar_jugador(ANCHO//2 - 50, 250, "RIGHT")
        
        ejemplo_x, ejemplo_y = ANCHO//2 + 20, 250
        pygame.draw.rect(VENTANA, ROJO, (ejemplo_x, ejemplo_y, enemigo_size, enemigo_size), border_radius=5)
        pygame.draw.circle(VENTANA, BLANCO, (ejemplo_x + 10, ejemplo_y + 12), 5)
        pygame.draw.circle(VENTANA, BLANCO, (ejemplo_x + enemigo_size - 10, ejemplo_y + 12), 5)
        pygame.draw.circle(VENTANA, NEGRO, (ejemplo_x + 10, ejemplo_y + 12), 2)
        pygame.draw.circle(VENTANA, NEGRO, (ejemplo_x + enemigo_size - 10, ejemplo_y + 12), 2)
        
        # Instrucciones
        texto_jugar = fuente_mediana.render("Presiona ENTER para jugar", True, BLANCO)
        texto_controles = fuente_pequena.render("Controles: Flechas para mover, ESPACIO para disparar", True, GRIS)
        VENTANA.blit(texto_jugar, (ANCHO//2 - texto_jugar.get_width()//2, 350))
        VENTANA.blit(texto_controles, (ANCHO//2 - texto_controles.get_width()//2, 400))
        
        pygame.display.update()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    return

def pantalla_game_over():
    while True:
        VENTANA.fill(AZUL_OSCURO)
        
        # Fondo estrellado
        for _ in range(100):
            x = random.randint(0, ANCHO)
            y = random.randint(0, ALTO)
            pygame.draw.circle(VENTANA, BLANCO, (x, y), 1)
        
        # Texto Game Over
        texto = fuente_grande.render("GAME OVER", True, ROJO)
        sombra = fuente_grande.render("GAME OVER", True, GRIS)
        VENTANA.blit(sombra, (ANCHO//2 - texto.get_width()//2 + 5, 200 + 5))
        VENTANA.blit(texto, (ANCHO//2 - texto.get_width()//2, 200))
        
        # Estadísticas
        stats = fuente_mediana.render(f"Alcanzaste el nivel {nivel}", True, BLANCO)
        VENTANA.blit(stats, (ANCHO//2 - stats.get_width()//2, 280))
        
        # Opciones
        reiniciar = fuente_mediana.render("Presiona R para reiniciar", True, VERDE)
        menu = fuente_mediana.render("Presiona M para volver al menú", True, BLANCO)
        salir = fuente_mediana.render("Presiona ESC para salir", True, GRIS)
        
        VENTANA.blit(reiniciar, (ANCHO//2 - reiniciar.get_width()//2, 350))
        VENTANA.blit(menu, (ANCHO//2 - menu.get_width()//2, 400))
        VENTANA.blit(salir, (ANCHO//2 - salir.get_width()//2, 450))
        
        pygame.display.update()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    return "reiniciar"
                if evento.key == pygame.K_m:
                    return "menu"
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def dibujar_hud():
    # Barra de experiencia
    ancho_barra = 250  # Más ancha
    altura_barra = 20  # Más alta
    progreso = min(experiencia / experiencia_siguiente_nivel, 1)
    
    pygame.draw.rect(VENTANA, GRIS, (10, 10, ancho_barra, altura_barra), border_radius=5)
    pygame.draw.rect(VENTANA, NARANJA, (10, 10, ancho_barra * progreso, altura_barra), border_radius=5)
    pygame.draw.rect(VENTANA, BLANCO, (10, 10, ancho_barra, altura_barra), 2, border_radius=5)
    
    # Texto de nivel y experiencia con fuente más grande
    nivel_texto = fuente_pixel.render(f"LVL: {nivel}", True, BLANCO)
    exp_texto = fuente_pixel.render(f"XP: {experiencia}/{int(experiencia_siguiente_nivel)}", True, BLANCO)
    VENTANA.blit(nivel_texto, (15, 35))
    VENTANA.blit(exp_texto, (15, 60))  # Más separado
    
    # Balas disponibles
    balas_texto = fuente_pixel.render(f"BALAS: {max_balas - len(balas)}/{max_balas}", True, BLANCO)
    VENTANA.blit(balas_texto, (ANCHO - balas_texto.get_width() - 15, 15))
    
    # Daño de las balas
    danio_texto = fuente_pixel.render(f"DANIO: {bala_danio}", True, ROJO)
    VENTANA.blit(danio_texto, (ANCHO - danio_texto.get_width() - 15, 45))

def dibujar_enemigos():
    for enemigo in enemigos:
        x, y, vida_max, vida_actual = enemigo
        
        # Cuerpo del enemigo
        pygame.draw.rect(VENTANA, ROJO, (x, y, enemigo_size, enemigo_size), border_radius=5)
        
        # Ojos del enemigo
        pygame.draw.circle(VENTANA, BLANCO, (x + 10, y + 12), 5)
        pygame.draw.circle(VENTANA, BLANCO, (x + enemigo_size - 10, y + 12), 5)
        pygame.draw.circle(VENTANA, NEGRO, (x + 10, y + 12), 2)
        pygame.draw.circle(VENTANA, NEGRO, (x + enemigo_size - 10, y + 12), 2)
        
        # Barra de vida
        vida_ancho = enemigo_size
        vida_altura = 5
        vida_progreso = vida_actual / vida_max
        
        pygame.draw.rect(VENTANA, GRIS, (x, y - 10, vida_ancho, vida_altura))
        pygame.draw.rect(VENTANA, VERDE, (x, y - 10, vida_ancho * vida_progreso, vida_altura))
        pygame.draw.rect(VENTANA, BLANCO, (x, y - 10, vida_ancho, vida_altura), 1)

def dibujar_balas():
    for bala in balas:
        pygame.draw.rect(VENTANA, AMARILLO, (bala[0], bala[1], 6, 6), border_radius=3)

def dibujar_efectos():
    for efecto in efectos[:]:
        x, y, duracion, color = efecto
        pygame.draw.circle(VENTANA, color, (int(x), int(y)), int(duracion / 3))
        
        efecto[3] = (  # Hacer el efecto más transparente
            min(255, color[0] + 10),
            min(255, color[1] + 10),
            min(255, color[2] + 10)
        )
        efecto[2] -= 1  # Reducir duración
        
        if efecto[2] <= 0:
            efectos.remove(efecto)

def reiniciar_juego():
    global jugador_x, jugador_y, enemigos, balas, nivel, experiencia, experiencia_siguiente_nivel, efectos
    
    jugador_x, jugador_y = ANCHO // 2, ALTO // 2
    enemigos = []
    balas = []
    efectos = []
    nivel = 1
    experiencia = 0
    experiencia_siguiente_nivel = niveles[0]

def juego():
    reiniciar_juego()
    
    while True:
        manejar_eventos()
        spawnear_enemigos()
        mover_balas()
        mover_enemigos()
        
        # Dibujar todo
        VENTANA.fill(AZUL_OSCURO)
        
        # Estrellas de fondo
        for _ in range(30):
            x = random.randint(0, ANCHO)
            y = random.randint(0, ALTO)
            pygame.draw.circle(VENTANA, BLANCO, (x, y), 1)
        
        dibujar_balas()
        dibujar_enemigos()
        dibujar_jugador(jugador_x, jugador_y, jugador_dir)
        dibujar_efectos()
        dibujar_hud()
        
        pygame.display.update()
        reloj.tick(60)

def manejar_eventos():
    global jugador_x, jugador_y, jugador_dir, balas
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                disparar()
            if evento.key == pygame.K_ESCAPE:
                resultado = pantalla_game_over()
                if resultado == "menu":
                    pantalla_inicio()
                    juego()
    
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT]:
        jugador_x -= jugador_vel
        jugador_dir = "LEFT"
    if teclas[pygame.K_RIGHT]:
        jugador_x += jugador_vel
        jugador_dir = "RIGHT"
    if teclas[pygame.K_UP]:
        jugador_y -= jugador_vel
        jugador_dir = "UP"
    if teclas[pygame.K_DOWN]:
        jugador_y += jugador_vel
        jugador_dir = "DOWN"
    
    # Mantener al jugador dentro de los límites
    jugador_x = max(0, min(jugador_x, ANCHO - jugador_size))
    jugador_y = max(0, min(jugador_y, ALTO - jugador_size))

def mover_enemigos():
    global enemigo_vel
    
    enemigo_vel = 1.5 + nivel * 0.1
    
    for enemigo in enemigos[:]:
        x, y, vida_max, vida_actual = enemigo
        
        # Movimiento hacia el jugador
        if jugador_x > x:
            enemigo[0] += enemigo_vel
        elif jugador_x < x:
            enemigo[0] -= enemigo_vel
        if jugador_y > y:
            enemigo[1] += enemigo_vel
        elif jugador_y < y:
            enemigo[1] -= enemigo_vel
        
        # Detección de colisión con el jugador
        if (jugador_x < x + enemigo_size and
            jugador_x + jugador_size > x and
            jugador_y < y + enemigo_size and
            jugador_y + jugador_size > y):
            resultado = pantalla_game_over()
            if resultado == "reiniciar":
                reiniciar_juego()
            elif resultado == "menu":
                pantalla_inicio()
                reiniciar_juego()

# Iniciar el juego
pantalla_inicio()
juego()