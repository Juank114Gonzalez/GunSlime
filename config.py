import pygame

# Inicialización de Pygame
pygame.init()

# Obtener información de la pantalla
info_pantalla = pygame.display.Info()
ANCHO = info_pantalla.current_w
ALTO = info_pantalla.current_h
MODO_PANTALLA_COMPLETA = True

# Configuración de la ventana
if MODO_PANTALLA_COMPLETA:
    VENTANA = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
else:
    VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("GUNSLIME")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
VERDE_OSCURO = (0, 100, 0)
AMARILLO = (255, 255, 0)
GRIS = (128, 128, 128)
AZUL_OSCURO = (0, 0, 100)
NARANJA = (255, 165, 0)
ROSA = (255, 100, 150)
MORADO = (128, 0, 128)
AZUL = (0, 0, 255)

# Configuración del jugador
JUGADOR_SIZE = 40
JUGADOR_VEL = 5
JUGADOR_VIDA_MAX = 100
JUGADOR_VIDA_REGEN = 0.01  # Reducido de 0.1 a 0.01 para que la regeneración sea más lenta

# Configuración de enemigos
ENEMIGO_SIZE = 35
ENEMIGO_VEL_BASE = 1.5
ENEMIGO_VIDA_BASE = 2
ENEMIGO_SPAWN_TIME = 1000  # Milisegundos
MAX_ENEMIGOS_BASE = 5
ENEMIGO_DANIO = 10  # Añadido: daño que hace un enemigo al tocar al jugador
ENEMIGO_BALA_DANIO = 5  # Añadido: daño que hace una bala enemiga

# Configuración de jefes
JEFE_SIZE = 80
JEFE_VIDA_BASE = 2
JEFE_VEL_BASE = 1.0
JEFE_SPAWN_NIVEL = 5  # Cada cuántos niveles aparece un jefe
JEFE_DANIO = 15
JEFE_BALA_DANIO = 8

# Configuración de balas
BALA_VEL = 7
BALA_DANIO_BASE = 1
MAX_BALAS_BASE = 5
TIEMPO_ENTRE_DISPAROS = 200  # 200ms entre cada disparo automático

# Configuración de niveles
EXPERIENCIA_BASE = 100
EXPERIENCIA_MULTIPLICADOR = 1.5
MAX_NIVEL = 20

# Configuración de powerups
POWERUP_DURACION = 10000  # 10 segundos
POWERUP_TIPOS = {
    'VELOCIDAD': {'color': AZUL, 'efecto': 1.5},
    'DANIO': {'color': ROJO, 'efecto': 2.0},
    'VIDA': {'color': VERDE, 'efecto': 50},
    'BALAS': {'color': AMARILLO, 'efecto': 3}
}

# Configuración de fuentes
try:
    FUENTE_PIXEL = pygame.font.Font("PressStart2P-Regular.ttf", 16)
except:
    FUENTE_PIXEL = pygame.font.SysFont("Arial", 16)

FUENTE_PEQUEÑA = pygame.font.SysFont("Arial", 20)
FUENTE_MEDIANA = pygame.font.SysFont("Arial", 28)
FUENTE_GRANDE = pygame.font.SysFont("Arial", 56)
FUENTE_TITULO = pygame.font.SysFont("Impact", 72)

# Configuración de sonido
try:
    pygame.mixer.init()
    SONIDO_DISPARO = pygame.mixer.Sound("sounds/shoot.wav")
    SONIDO_EXPLOSION = pygame.mixer.Sound("sounds/explosion.wav")
    SONIDO_POWERUP = pygame.mixer.Sound("sounds/powerup.wav")
    SONIDO_NIVEL = pygame.mixer.Sound("sounds/level_up.wav")
    SONIDO_GAME_OVER = pygame.mixer.Sound("sounds/game_over.wav")
except:
    print("⚠️ Advertencia: No se pudieron cargar los sonidos. Continuando sin sonido.")
    SONIDO_DISPARO = None
    SONIDO_EXPLOSION = None
    SONIDO_POWERUP = None
    SONIDO_NIVEL = None
    SONIDO_GAME_OVER = None

# Constantes de jefes
BOSS_APARICION_ENEMIGOS = 15  # Cada 30 enemigos aparece un jefe
BOSS_VIDA_BASE = 100
BOSS_DANIO_BASE = 2
BOSS_VELOCIDAD_BASE = 2
BOSS_TIEMPO_FASE = 15000  # 15 segundos por fase 