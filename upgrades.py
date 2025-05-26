import pygame
from config import *

class Upgrade:
    def __init__(self, nombre, descripcion, efecto, color):
        self.nombre = nombre
        self.descripcion = descripcion
        self.efecto = efecto
        self.color = color

class Arma:
    def __init__(self):
        self.nivel = 1
        self.tipo = "BASICA"
        self.danio_base = 1
        self.velocidad_disparo = 1
        self.balas_por_disparo = 1
        self.patron_disparo = "NORMAL"  # NORMAL, TRIPLE, CIRCULAR

    def evolucionar(self, tipo):
        if tipo == "RAPIDA":
            self.velocidad_disparo *= 1.5
            self.tipo = "RAPIDA"
        elif tipo == "POTENTE":
            self.danio_base *= 2
            self.tipo = "POTENTE"
        elif tipo == "MULTIPLE":
            self.balas_por_disparo = 3
            self.patron_disparo = "TRIPLE"
            self.tipo = "MULTIPLE"
        self.nivel += 1

# Definición de mejoras disponibles
MEJORAS_VIDA = [
    Upgrade("Vida +20%", "Aumenta la vida máxima en un 20%", lambda p: setattr(p, 'vida_max', int(p.vida_max * 1.2)), VERDE),
    Upgrade("Regeneración", "Aumenta la regeneración de vida", lambda p: setattr(p, 'vida_regen', p.vida_regen * 1.5), VERDE),
    Upgrade("Escudo", "Reduce el daño recibido en un 25%", lambda p: setattr(p, 'reduccion_danio', 0.25), AZUL)
]

MEJORAS_DANIO = [
    Upgrade("Daño +30%", "Aumenta el daño base en un 30%", lambda p: setattr(p, 'danio_base', p.danio_base * 1.3), ROJO),
    Upgrade("Velocidad de Ataque", "Aumenta la velocidad de disparo", lambda p: setattr(p, 'velocidad_disparo', p.velocidad_disparo * 1.2), NARANJA),
    Upgrade("Penetración", "Las balas atraviesan enemigos", lambda p: setattr(p, 'balas_penetrantes', True), MORADO)
]

MEJORAS_VELOCIDAD = [
    Upgrade("Velocidad +25%", "Aumenta la velocidad de movimiento", lambda p: setattr(p, 'vel', p.vel * 1.25), AZUL),
    Upgrade("Esquiva", "Chance de esquivar ataques", lambda p: setattr(p, 'chance_esquiva', 0.2), AMARILLO),
    Upgrade("Dash", "Permite hacer un dash rápido", lambda p: setattr(p, 'tiene_dash', True), ROSA)
]

EVOLUCIONES_ARMA = [
    Upgrade("Rápida", "Aumenta la velocidad de disparo", "RAPIDA", AZUL),
    Upgrade("Potente", "Aumenta el daño de las balas", "POTENTE", ROJO),
    Upgrade("Múltiple", "Dispara 3 balas a la vez", "MULTIPLE", AMARILLO)
]

class MenuMejoras:
    def __init__(self):
        self.mejoras = [
            Upgrade("Más Daño", "Aumenta el daño de tus disparos en un 20%", 1.2, ROJO),
            Upgrade("Más Vida", "Aumenta tu vida máxima en 25 puntos", 25, VERDE),
            Upgrade("Más Velocidad", "Aumenta tu velocidad de movimiento en un 15%", 1.15, AZUL)
        ]
        self.seleccionado = None
        self.activo = False
        self.ancho_card = 200
        self.alto_card = 250
        self.espacio = 50
        print("MenuMejoras inicializado")  # Debug

    def mostrar(self, ventana):
        if not self.activo:
            print("MenuMejoras no está activo")  # Debug
            return

        print("Mostrando menú de mejoras")  # Debug

        # Fondo semi-transparente
        s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))  # Más oscuro para mejor visibilidad
        ventana.blit(s, (0, 0))

        # Título
        titulo = FUENTE_MEDIANA.render("¡Elige una mejora!", True, BLANCO)
        ventana.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 50))

        # Dibujar cards
        for i, mejora in enumerate(self.mejoras):
            x = ANCHO//2 - (self.ancho_card * 1.5 + self.espacio) + i * (self.ancho_card + self.espacio)
            y = ALTO//2 - self.alto_card//2

            # Fondo de la card
            color = mejora.color if i != self.seleccionado else BLANCO
            pygame.draw.rect(ventana, color, (x, y, self.ancho_card, self.alto_card), border_radius=10)
            pygame.draw.rect(ventana, BLANCO, (x, y, self.ancho_card, self.alto_card), 2, border_radius=10)

            # Contenido de la card
            nombre = FUENTE_PIXEL.render(mejora.nombre, True, NEGRO)
            descripcion = FUENTE_PEQUEÑA.render(mejora.descripcion, True, NEGRO)
            
            # Centrar texto
            ventana.blit(nombre, (x + self.ancho_card//2 - nombre.get_width()//2, y + 30))
            
            # Dividir descripción en múltiples líneas
            palabras = mejora.descripcion.split()
            lineas = []
            linea_actual = ""
            for palabra in palabras:
                test_linea = linea_actual + " " + palabra if linea_actual else palabra
                if FUENTE_PEQUEÑA.size(test_linea)[0] < self.ancho_card - 20:
                    linea_actual = test_linea
                else:
                    lineas.append(linea_actual)
                    linea_actual = palabra
            if linea_actual:
                lineas.append(linea_actual)

            for j, linea in enumerate(lineas):
                texto = FUENTE_PEQUEÑA.render(linea, True, NEGRO)
                ventana.blit(texto, (x + self.ancho_card//2 - texto.get_width()//2, y + 80 + j * 25))

        # Forzar actualización de la pantalla
        pygame.display.flip()

    def manejar_eventos(self, evento):
        if not self.activo:
            print("MenuMejoras no está activo para manejar eventos")  # Debug
            return None

        print("Manejando eventos del menú de mejoras")  # Debug

        if evento.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for i in range(len(self.mejoras)):
                x = ANCHO//2 - (self.ancho_card * 1.5 + self.espacio) + i * (self.ancho_card + self.espacio)
                y = ALTO//2 - self.alto_card//2
                if (x <= mouse_x <= x + self.ancho_card and 
                    y <= mouse_y <= y + self.alto_card):
                    self.seleccionado = i
                    print(f"Mejora seleccionada: {self.mejoras[i].nombre}")  # Debug
                    return self.mejoras[i]

        return None

    def activar(self):
        print("Activando menú de mejoras")  # Debug
        self.activo = True
        self.seleccionado = None

    def desactivar(self):
        print("Desactivando menú de mejoras")  # Debug
        self.activo = False
        self.seleccionado = None 