import pygame
import os
import sys

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
JUGADOR_VIDA_REGEN = 0.0

# Configuración de enemigos
ENEMIGO_SIZE = 35
ENEMIGO_VEL_BASE = 2.0
ENEMIGO_VIDA_BASE = 3
ENEMIGO_SPAWN_TIME = 800
MAX_ENEMIGOS_BASE = 8
ENEMIGO_DANIO = 20
ENEMIGO_BALA_DANIO = 10

# Configuración de jefes
JEFE_SIZE = 80
JEFE_VIDA_BASE = 2
JEFE_VEL_BASE = 1.0
JEFE_SPAWN_NIVEL = 5
JEFE_DANIO = 30
JEFE_BALA_DANIO = 15

# Configuración de balas
BALA_VEL = 7
BALA_DANIO_BASE = 1
MAX_BALAS_BASE = 5
TIEMPO_ENTRE_DISPAROS = 200

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

# Función para obtener la ruta base de los recursos
def resource_path(relative_path):
    """Obtiene la ruta absoluta del recurso, funciona para desarrollo y para PyInstaller"""
    try:
        # PyInstaller crea un directorio temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Configuración de fuentes
try:
    FUENTE_PIXEL = pygame.font.Font(resource_path("PressStart2P-Regular.ttf"), 16)
except:
    FUENTE_PIXEL = pygame.font.SysFont("Arial", 16)

FUENTE_PEQUEÑA = pygame.font.SysFont("Arial", 20)
FUENTE_MEDIANA = pygame.font.SysFont("Arial", 28)
FUENTE_GRANDE = pygame.font.SysFont("Arial", 56)
FUENTE_TITULO = pygame.font.SysFont("Impact", 72)

# Configuración de sonido
try:
    pygame.mixer.init()
    
    # Configuración de música
    MUSICA_NORMAL = resource_path("soundtrack.mp3")
    MUSICA_BOSS = resource_path("boss.mp3")
    
    # Verificar que los archivos de música existan
    if not os.path.exists(MUSICA_NORMAL):
        print(f"⚠️ Advertencia: No se encontró el archivo {MUSICA_NORMAL}")
        MUSICA_NORMAL = None
    if not os.path.exists(MUSICA_BOSS):
        print(f"⚠️ Advertencia: No se encontró el archivo {MUSICA_BOSS}")
        MUSICA_BOSS = None
    
    # Intentar cargar la música normal si existe
    if MUSICA_NORMAL:
        try:
            pygame.mixer.music.load(MUSICA_NORMAL)
            pygame.mixer.music.set_volume(0.5)  # Volumen al 50%
            print(f"✅ Música normal cargada correctamente: {MUSICA_NORMAL}")
        except Exception as e:
            print(f"⚠️ Error al cargar la música normal: {e}")
            MUSICA_NORMAL = None
    
    # Configuración de efectos de sonido
    SONIDO_DISPARO = None
    SONIDO_EXPLOSION = None
    SONIDO_POWERUP = None
    SONIDO_NIVEL = None
    SONIDO_GAME_OVER = None
    
    # Intentar cargar los efectos de sonido que existen
    try:
        SONIDO_DISPARO = pygame.mixer.Sound(resource_path("energy_shot.mp3"))
        SONIDO_EXPLOSION = pygame.mixer.Sound(resource_path("enemy_destroy.mp3"))
        SONIDO_DISPARO.set_volume(0.02)  # Volumen al 10%
        SONIDO_EXPLOSION.set_volume(0.1)  # Volumen al 10%
        print("✅ Efectos de sonido cargados correctamente")
    except Exception as e:
        print(f"⚠️ Error al cargar los efectos de sonido: {e}")
        
except Exception as e:
    print(f"⚠️ Error al inicializar el audio: {e}")
    SONIDO_DISPARO = None
    SONIDO_EXPLOSION = None
    SONIDO_POWERUP = None
    SONIDO_NIVEL = None
    SONIDO_GAME_OVER = None
    MUSICA_NORMAL = None
    MUSICA_BOSS = None

# Constantes de jefes
BOSS_APARICION_ENEMIGOS = 12
BOSS_VIDA_BASE = 200
BOSS_DANIO_BASE = 5
BOSS_VELOCIDAD_BASE = 2.5
BOSS_TIEMPO_FASE = 15000  # 15 segundos por fase 