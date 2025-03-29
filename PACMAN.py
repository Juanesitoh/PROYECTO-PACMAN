import pygame
import random
import math
import heapq
from pygame.locals import *
from collections import deque

# Inicializacion
pygame.init()
ANCHO = 800
ALTO = 600
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption('PACMAN - ACTIVIDAD #8 - METODOLOGIAS DE SOFTWARE')
reloj = pygame.time.Clock()

# Colores
NEGRO = (0, 0, 0)
AMARILLO = (255, 255, 0)
AZUL = (0, 0, 255)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
ROSA = (255, 192, 203)
CELESTE = (0, 255, 255)
NARANJA = (255, 165, 0)

# Tamaños
TAMANO_PACMAN = 30
TAMANO_FANTASMA = 30
TAMANO_PUNTO = 8
TAMANO_PUNTO_PODER = 15

# Velocidades
VELOCIDAD_PACMAN = 3
VELOCIDAD_FANTASMA = 2

# Dirección
ARRIBA = 0
DERECHA = 1
ABAJO = 2
IZQUIERDA = 3

FILAS = 15
COLUMNAS = 15
TAMANO_CELDA = 40
ANCHO = COLUMNAS * TAMANO_CELDA
ALTO = FILAS * TAMANO_CELDA

def crear_laberinto():
    # Inicializar matriz llena de paredes
    laberinto = [[1 for _ in range(COLUMNAS)] for _ in range(FILAS)]
    
    # Función para verificar límites del área navegable
    def dentro_limites(x, y):
        return 0 < x < FILAS-1 and 0 < y < COLUMNAS-1
    
    # Algoritmo para generación de laberintos
    paredes = []
    inicio = (1, 1)
    laberinto[inicio[0]][inicio[1]] = 0  # Celda inicial libre
    # Añadir paredes adyacentes a la celda inicial
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx = inicio[0] + dx
        ny = inicio[1] + dy
        if dentro_limites(nx, ny):
            paredes.append((nx, ny, inicio[0], inicio[1]))
    
    while paredes:
        # Elegir una pared aleatoria
        random.shuffle(paredes)
        x, y, px, py = paredes.pop()
        
        # Verificar si la celda opuesta está bloqueada
        ox = x + (x - px)
        oy = y + (y - py)
        
        if dentro_limites(ox, oy):
            if laberinto[ox][oy] == 1 and laberinto[x][y] == 1:
                # Abrir pasaje
                laberinto[x][y] = 0
                laberinto[ox][oy] = 0
                
                # Añadir nuevas paredes
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx = ox + dx
                    ny = oy + dy
                    if dentro_limites(nx, ny) and laberinto[nx][ny] == 1:
                        paredes.append((nx, ny, ox, oy))

    # Añadir puntos y asegurar conectividad
    for i in range(FILAS):
        for j in range(COLUMNAS):
            if laberinto[i][j] == 0 and (i, j) != inicio:
                # 5% de probabilidad para punto especial
                laberinto[i][j] = 3 if random.random() < 0.05 else 2
                
    # Asegurar bordes sólidos
    for i in range(FILAS):
        laberinto[i][0] = 1
        laberinto[i][-1] = 1
    for j in range(COLUMNAS):
        laberinto[0][j] = 1
        laberinto[-1][j] = 1
    
    # Posición inicial siempre libre
    laberinto[inicio[0]][inicio[1]] = 0
    
    return laberinto

laberinto = crear_laberinto()

# Clases
# Colores 
AMARILLO = (255, 255, 0)
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
AZUL_OSCURO = (0, 0, 139)

class Pacman:
    def __init__(self):
        self.x = TAMANO_CELDA + TAMANO_CELDA // 2
        self.y = TAMANO_CELDA + TAMANO_CELDA // 2
        self.direccion = DERECHA
        self.siguiente_direccion = DERECHA
        self.radio = TAMANO_PACMAN // 2
        self.velocidad = VELOCIDAD_PACMAN
        self.mouth_angle = 30  # Ángulo inicial de la boca
        self.mouth_speed = 0.3  # Velocidad de animación de la boca
        self.puntuacion = 0
        self.vidas = 3
        self.poder_activo = False
        self.tiempo_poder = 0
        self.eye_radius = int(self.radio * 0.15)
        self.mouth_depth = 0.85  # Profundidad de la boca (0-1)

    def update(self):
        self.mouth_angle = 30 + 25 * math.sin(pygame.time.get_ticks() * self.mouth_speed / 200)
        self.mouth_angle = max(20, min(50, self.mouth_angle))

    def dibujar(self):
        # Cuerpo principal con efecto de profundidad
        pygame.draw.circle(ventana, AMARILLO, (self.x, self.y), self.radio)
        
        # Boca 
        self.dibujar_boca()
        
        # Reflejo 
        self.dibujar_reflejo()

    def dibujar_boca(self):
        base_angle = {
            DERECHA: 0,
            IZQUIERDA: 180,
            ARRIBA: 90,
            ABAJO: 270
        }[self.direccion]

        start_angle = math.radians(base_angle - self.mouth_angle/2)
        end_angle = math.radians(base_angle + self.mouth_angle/2)
        
        # Calcular puntos para la forma de la boca
        points = [(self.x, self.y)]
        steps = 10
        for i in range(steps + 1):
            angle = start_angle + (end_angle - start_angle) * i / steps
            dx = math.cos(angle) * self.radio * self.mouth_depth
            dy = -math.sin(angle) * self.radio * self.mouth_depth  # Invertir eje Y
            points.append((self.x + dx, self.y + dy))
        
        # Dibujar boca como polígono
        pygame.draw.polygon(ventana, NEGRO, points)

    def dibujar_reflejo(self):
        offset = self.radio * 0.3
        reflection_pos = {
            DERECHA: (self.x + offset, self.y - offset),
            IZQUIERDA: (self.x - offset, self.y - offset),
            ARRIBA: (self.x - offset/2, self.y - offset),
            ABAJO: (self.x + offset/2, self.y + offset)
        }[self.direccion]
        
        pygame.draw.circle(ventana, (255, 255, 200), reflection_pos, int(self.radio * 0.15))

    def mover(self):
        # Intentar cambiar la dirección si hay una nueva dirección solicitada
        self.intentar_cambiar_direccion()
        
        # Calcular nueva posición según la dirección actual
        x_nuevo, y_nuevo = self.x, self.y
        if self.direccion == DERECHA:
            x_nuevo += self.velocidad
        elif self.direccion == IZQUIERDA:
            x_nuevo -= self.velocidad
        elif self.direccion == ARRIBA:
            y_nuevo -= self.velocidad
        elif self.direccion == ABAJO:
            y_nuevo += self.velocidad
        
        # Verificar colisión con paredes
        celda_x = x_nuevo // TAMANO_CELDA
        celda_y = y_nuevo // TAMANO_CELDA
        
        # Verificar límites del laberinto
        if 0 <= celda_x < COLUMNAS and 0 <= celda_y < FILAS:
            # Verificar si hay colisión con una pared
            if not self.hay_colision_pared(x_nuevo, y_nuevo):
                self.x, self.y = x_nuevo, y_nuevo
        
        # Verificar colisión con puntos
        self.verificar_colision_puntos()
        
        # Actualizar tiempo de poder
        if self.poder_activo:
            self.tiempo_poder -= 1
            if self.tiempo_poder <= 0:
                self.poder_activo = False

    def intentar_cambiar_direccion(self):
        if self.siguiente_direccion != self.direccion:
            x_nuevo, y_nuevo = self.x, self.y
            if self.siguiente_direccion == DERECHA:
                x_nuevo += self.velocidad
            elif self.siguiente_direccion == IZQUIERDA:
                x_nuevo -= self.velocidad
            elif self.siguiente_direccion == ARRIBA:
                y_nuevo -= self.velocidad
            elif self.siguiente_direccion == ABAJO:
                y_nuevo += self.velocidad
            
            if not self.hay_colision_pared(x_nuevo, y_nuevo):
                self.direccion = self.siguiente_direccion

    def hay_colision_pared(self, x, y):
        # Verificar colisión con pared 
        puntos_a_verificar = [
            (x, y),  # Centro
            (x + self.radio * 0.8, y),  # Derecha
            (x - self.radio * 0.8, y),  # Izquierda
            (x, y + self.radio * 0.8),  # Abajo
            (x, y - self.radio * 0.8),  # Arriba
        ]
        
        for px, py in puntos_a_verificar:
            celda_x = int(px // TAMANO_CELDA)
            celda_y = int(py // TAMANO_CELDA)
            if 0 <= celda_x < COLUMNAS and 0 <= celda_y < FILAS:
                if laberinto[celda_y][celda_x] == 1:
                    return True
        return False

    def verificar_colision_puntos(self):
        celda_x = int(self.x // TAMANO_CELDA)
        celda_y = int(self.y // TAMANO_CELDA)
        
        if 0 <= celda_x < COLUMNAS and 0 <= celda_y < FILAS:
            if laberinto[celda_y][celda_x] == 2:  # Punto normal
                laberinto[celda_y][celda_x] = 0
                self.puntuacion += 10
            elif laberinto[celda_y][celda_x] == 3:  # Punto de poder
                laberinto[celda_y][celda_x] = 0
                self.puntuacion += 50
                self.poder_activo = True
                self.tiempo_poder = 200  # Duración del poder

# Colores 
AZUL = (0, 0, 255)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

class Fantasma:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.direccion = random.randint(0, 3)
        self.velocidad = VELOCIDAD_FANTASMA
        self.radio = TAMANO_FANTASMA // 2
        self.comido = False
        self.tiempo_respawn = 0

    def dibujar(self, poder_activo):
        if self.comido:
            return  # fantasmas comidos
        
        color_actual = AZUL if poder_activo else self.color
        
        # Cuerpo del fantasma
        pygame.draw.circle(ventana, color_actual, (self.x, self.y - self.radio * 0.5), self.radio)
        pygame.draw.rect(ventana, color_actual, (
            self.x - self.radio,
            self.y - self.radio * 0.5,
            self.radio * 2,
            self.radio * 1.5
        ))
        
        # Picos inferiores
        picos = 3
        ancho_pico = (self.radio * 2) / picos
        for i in range(picos):
            pygame.draw.polygon(ventana, color_actual, [
                (self.x - self.radio + i * ancho_pico, self.y + self.radio),
                (self.x - self.radio + (i + 0.5) * ancho_pico, self.y + self.radio * 1.3),
                (self.x - self.radio + (i + 1) * ancho_pico, self.y + self.radio)
            ])
        
        # Ojos
        # Ojos base (siempre blancos)
        ojo_y = self.y - self.radio * 0.3
        pygame.draw.circle(ventana, BLANCO, (int(self.x - self.radio * 0.4), int(ojo_y)), int(self.radio * 0.3))
        pygame.draw.circle(ventana, BLANCO, (int(self.x + self.radio * 0.4), int(ojo_y)), int(self.radio * 0.3))
        
        # Pupilas direccionales
        direccion_offset = {
            DERECHA: (0.20, 0),
            IZQUIERDA: (-0.20, 0),
            ARRIBA: (0, -0.1),
            ABAJO: (0, 0.1)
        }
        
        # Offset basado en la dirección actual
        offset_x, offset_y = direccion_offset.get(self.direccion, (0, 0))
        
        # Ojo izquierdo
        pygame.draw.circle(ventana, AZUL, (
            int(self.x - self.radio * 0.4 + offset_x * self.radio),
            int(ojo_y + offset_y * self.radio)
        ), int(self.radio * 0.30))
        
        # Ojo derecho
        pygame.draw.circle(ventana, AZUL, (
            int(self.x + self.radio * 0.4 + offset_x * self.radio),
            int(ojo_y + offset_y * self.radio)
        ), int(self.radio * 0.30))

    def mover(self, pacman):
        if self.comido:
            self.tiempo_respawn -= 1
            if self.tiempo_respawn <= 0:
                self.comido = False
                celdas_validas = [(x, y) for y in range(FILAS) for x in range(COLUMNAS) if laberinto[y][x] != 1]
                if celdas_validas:
                    x, y = random.choice(celdas_validas)
                    self.x = x * TAMANO_CELDA + TAMANO_CELDA // 2
                    self.y = y * TAMANO_CELDA + TAMANO_CELDA // 2
            return

        # persecución 
        if random.random() < 0.70:  #PROBABILIDAD de persecucion 
            objetivo_x = pacman.x
            objetivo_y = pacman.y
            if pacman.poder_activo:
                objetivo_x = self.x * 2 - pacman.x  # Invertir dirección para huir
                objetivo_y = self.y * 2 - pacman.y
            mejor_direccion = None
            mejor_distancia = float('inf') if not pacman.poder_activo else -float('inf')
            
            # Evaluar todas las direcciones posibles
            for direccion in [DERECHA, IZQUIERDA, ARRIBA, ABAJO]:
                x_temp, y_temp = self.x, self.y
                if direccion == DERECHA:
                    x_temp += self.velocidad
                elif direccion == IZQUIERDA:
                    x_temp -= self.velocidad
                elif direccion == ARRIBA:
                    y_temp -= self.velocidad
                elif direccion == ABAJO:
                    y_temp += self.velocidad
                
                if not self.hay_colision_pared(x_temp, y_temp):
                    distancia = ((x_temp - objetivo_x)**2 + (y_temp - objetivo_y)**2)**0.5
                    
                    if (not pacman.poder_activo and distancia < mejor_distancia) or \
                    (pacman.poder_activo and distancia > mejor_distancia):
                        mejor_distancia = distancia
                        mejor_direccion = direccion

            if mejor_direccion is not None:
                self.direccion = mejor_direccion

        # Movimiento continuo en la dirección actual si es válida
        x_nuevo, y_nuevo = self.x, self.y
        if self.direccion == DERECHA:
            x_nuevo += self.velocidad
        elif self.direccion == IZQUIERDA:
            x_nuevo -= self.velocidad
        elif self.direccion == ARRIBA:
            y_nuevo -= self.velocidad
        elif self.direccion == ABAJO:
            y_nuevo += self.velocidad

        # Manejo de colisiones 
        if not self.hay_colision_pared(x_nuevo, y_nuevo):
            self.x, self.y = x_nuevo, y_nuevo
        else:
            direcciones_posibles = []
            for direccion in [DERECHA, IZQUIERDA, ARRIBA, ABAJO]:
                x_temp, y_temp = self.x, self.y
                if direccion == DERECHA:
                    x_temp += self.velocidad
                elif direccion == IZQUIERDA:
                    x_temp -= self.velocidad
                elif direccion == ARRIBA:
                    y_temp -= self.velocidad
                elif direccion == ABAJO:
                    y_temp += self.velocidad
                
                if not self.hay_colision_pared(x_temp, y_temp) and direccion != self.direccion:
                    direcciones_posibles.append(direccion)
            
            if direcciones_posibles:
                self.direccion = random.choice(direcciones_posibles)
            else:
                self.direccion = (self.direccion + 2) % 4  # Voltear 180 grados

    def hay_colision_pared(self, x, y):
        # Verificar colisión con pared usando múltiples puntos del cuerpo del fantasma
        puntos_a_verificar = [
            (x, y),  # Centro
            (x + self.radio * 0.8, y),  # Derecha
            (x - self.radio * 0.8, y),  # Izquierda
            (x, y + self.radio * 0.8),  # Abajo
            (x, y - self.radio * 0.8),  # Arriba
        ]
        
        for px, py in puntos_a_verificar:
            celda_x = int(px // TAMANO_CELDA)
            celda_y = int(py // TAMANO_CELDA)
            if 0 <= celda_x < COLUMNAS and 0 <= celda_y < FILAS:
                if laberinto[celda_y][celda_x] == 1:
                    return True
        return False

    def verificar_colision_pacman(self, pacman):
        distancia = ((self.x - pacman.x) ** 2 + (self.y - pacman.y) ** 2) ** 0.5
        if distancia < self.radio + pacman.radio * 0.8:
            if pacman.poder_activo:
                self.comido = True
                self.tiempo_respawn = 180  # Tiempo antes de reaparecer (frames)
                return 200  # Puntos por comer un fantasma
            else:
                return -1  # Pacman pierde una vida
        return 0


# Crear instancias
pacman = Pacman()
# En la creación de fantasmas:
fantasmas = [
        Fantasma(TAMANO_CELDA * (COLUMNAS - 2) + TAMANO_CELDA // 2, TAMANO_CELDA * (FILAS - 2) + TAMANO_CELDA // 2, ROJO),
        Fantasma(TAMANO_CELDA * (COLUMNAS - 2) + TAMANO_CELDA // 2, TAMANO_CELDA + TAMANO_CELDA // 2, ROSA),
        Fantasma(TAMANO_CELDA + TAMANO_CELDA // 2, TAMANO_CELDA * (FILAS - 2) + TAMANO_CELDA // 2, CELESTE),
        Fantasma(TAMANO_CELDA * (COLUMNAS // 2) + TAMANO_CELDA // 2, TAMANO_CELDA * (FILAS // 2) + TAMANO_CELDA // 2, NARANJA)
    ]


# Variables de juego
juego_activo = True
pausa = False
nivel = 1
vidas_restantes = 3
game_over = False
pantalla_inicio = True
contador_victoria = 0

# Fuentes
fuente_pequena = pygame.font.SysFont('Arial', 20)
fuente_mediana = pygame.font.SysFont('Arial', 30)
fuente_grande = pygame.font.SysFont('Arial', 40)

# Función para dibujar el laberinto
def dibujar_laberinto():
    for y in range(FILAS):
        for x in range(COLUMNAS):
            rect = (x * TAMANO_CELDA, y * TAMANO_CELDA, TAMANO_CELDA, TAMANO_CELDA)
            
            if laberinto[y][x] == 1:  # Pared
                pygame.draw.rect(ventana, AZUL, rect)
                # Efecto 3D para las paredes
                pygame.draw.rect(ventana, (70, 70, 200), (rect[0] + 2, rect[1] + 2, rect[2] - 4, rect[3] - 4))
            elif laberinto[y][x] == 2:  # Punto normal
                punto_x = x * TAMANO_CELDA + TAMANO_CELDA // 2
                punto_y = y * TAMANO_CELDA + TAMANO_CELDA // 2
                pygame.draw.circle(ventana, AMARILLO, (punto_x, punto_y), TAMANO_PUNTO)
            elif laberinto[y][x] == 3:  # Punto de poder
                punto_x = x * TAMANO_CELDA + TAMANO_CELDA // 2
                punto_y = y * TAMANO_CELDA + TAMANO_CELDA // 2
                pygame.draw.circle(ventana, AMARILLO, (punto_x, punto_y), TAMANO_PUNTO_PODER)
                # Efecto brillante para los puntos de poder
                pygame.draw.circle(ventana, BLANCO, (punto_x, punto_y), TAMANO_PUNTO_PODER // 2)

# Función para verificar si quedan puntos
def quedan_puntos():
    for y in range(len(laberinto)):  # Usar longitud real del laberinto
        for x in range(len(laberinto[y])):  # Usar longitud real de cada fila
            if laberinto[y][x] in [2, 3]:
                return True
    return False

# Función para reiniciar el juego
def reiniciar_nivel():
    global laberinto, pacman, fantasmas
    laberinto = crear_laberinto()
    pacman = Pacman()
    pacman.vidas = vidas_restantes
    fantasmas = [
        Fantasma(TAMANO_CELDA * (COLUMNAS - 2) + TAMANO_CELDA // 2, TAMANO_CELDA * (FILAS - 2) + TAMANO_CELDA // 2, ROJO),
        Fantasma(TAMANO_CELDA * (COLUMNAS - 2) + TAMANO_CELDA // 2, TAMANO_CELDA + TAMANO_CELDA // 2, ROSA),
        Fantasma(TAMANO_CELDA + TAMANO_CELDA // 2, TAMANO_CELDA * (FILAS - 2) + TAMANO_CELDA // 2, CELESTE),
        Fantasma(TAMANO_CELDA * (COLUMNAS // 2) + TAMANO_CELDA // 2, TAMANO_CELDA * (FILAS // 2) + TAMANO_CELDA // 2, NARANJA)
    ]

# Bucle principal del juego
ejecutando = True
while ejecutando:
    reloj.tick(60)
    
    # Gestión de eventos
    for evento in pygame.event.get():
        if evento.type == QUIT:
            ejecutando = False
        
        # Control del teclado
        if evento.type == KEYDOWN:
            if pantalla_inicio:
                pantalla_inicio = False
            elif game_over:
                game_over = False
                nivel = 1
                vidas_restantes = 3
                pacman.puntuacion = 0
                reiniciar_nivel()
            elif evento.key == K_p:
                pausa = not pausa
            elif not pausa and juego_activo:
                if evento.key == K_UP:
                    pacman.siguiente_direccion = ARRIBA
                elif evento.key == K_DOWN:
                    pacman.siguiente_direccion = ABAJO
                elif evento.key == K_LEFT:
                    pacman.siguiente_direccion = IZQUIERDA
                elif evento.key == K_RIGHT:
                    pacman.siguiente_direccion = DERECHA
    VERDE = (0, 255, 0)
    GRIS = (150, 150, 150)
    # Pantalla de inicio
    if pantalla_inicio:
        ventana.fill(NEGRO)
        
        # Configuraciones de posición
        MARGEN = 20
        POS_Y = ALTO // 4  # Empezamos más arriba

        # Título principal con efecto de sombra
        titulo = fuente_grande.render("PACMAN - Hard Mode", True, AMARILLO)

        # Integrantes del equipo con saltos de línea
        integrantes = fuente_pequena.render(
            "Juan Esteban Montilla         "
            "Salomé Álvarez          "
            "Nathalia Garcés", 
            True, BLANCO)
        
        # Instrucción principal 
        instrucciones = fuente_mediana.render("Presiona cualquier tecla para comenzar", True, VERDE)
        
        # Controles 
        controles = fuente_pequena.render("Controles: Flechas para mover | P: Pausa ", True, GRIS)

        # Dibujar elementos

        # Título principal
        ventana.blit(titulo, (ANCHO//2 - titulo.get_width()//2, POS_Y))
        # Integrantes 
        ventana.blit(integrantes, (ANCHO//2 - integrantes.get_width()//2, POS_Y + 100))
        
        # Instrucción parpadeante (usar con temporizador para efecto)
        if pygame.time.get_ticks() % 1000 < 500:  # Parpadeo cada 500ms
            ventana.blit(instrucciones, (ANCHO//2 - instrucciones.get_width()//2, ALTO - 150))
        
        # Controles en la parte inferior
        ventana.blit(controles, (ANCHO//2 - controles.get_width()//2, ALTO - 50))

        pygame.display.flip()
        continue
    
    # Pantalla de Game Over
    if game_over:
        ventana.fill(NEGRO)
        texto_go = fuente_grande.render("GAME OVER", True, ROJO)
        texto_puntaje = fuente_mediana.render(f"Puntuación final: {pacman.puntuacion}", True, BLANCO)
        texto_reinicio = fuente_pequena.render("Vueva a ejecutar nuevamente el juego", True, BLANCO)
        
        ventana.blit(texto_go, (ANCHO // 2 - texto_go.get_width() // 2, ALTO // 3))
        ventana.blit(texto_puntaje, (ANCHO // 2 - texto_puntaje.get_width() // 2, ALTO // 2))
        ventana.blit(texto_reinicio, (ANCHO // 2 - texto_reinicio.get_width() // 2, ALTO // 2 + 50))
        
        pygame.display.flip()
        continue
    
    # Pausa
    if pausa:
        texto_pausa = fuente_grande.render("PAUSA", True, AMARILLO)
        ventana.blit(texto_pausa, (ANCHO // 2 - texto_pausa.get_width() // 2, ALTO // 2))
        pygame.display.flip()
        continue
    
    # Lógica del juego (solo cuando está activo)
    if juego_activo:
        # Mover Pacman
        pacman.mover()
        
        # Verificar victoria (se comieron todos los puntos)
        if not quedan_puntos():
            contador_victoria += 1
            if contador_victoria > 180:  # Esperar 3 segundos después de comer todos los puntos
                nivel += 1
                vidas_restantes = pacman.vidas
                reiniciar_nivel()
                contador_victoria = 0
        
        # Mover fantasmas y verificar colisiones
        for fantasma in fantasmas:
            fantasma.mover(pacman)
            resultado = fantasma.verificar_colision_pacman(pacman)
            
            if resultado > 0:
                pacman.puntuacion += resultado
            elif resultado < 0:
                pacman.vidas -= 1
                if pacman.vidas <= 0:
                    juego_activo = False
                    game_over = True
                else:
                    # Resetear posiciones pero mantener puntuación y vidas
                    pacman.x = TAMANO_CELDA + TAMANO_CELDA // 2
                    pacman.y = TAMANO_CELDA + TAMANO_CELDA // 2
                    fantasmas = [
                        Fantasma(TAMANO_CELDA * (COLUMNAS - 2) + TAMANO_CELDA // 2, TAMANO_CELDA * (FILAS - 2) + TAMANO_CELDA // 2, ROJO),
                        Fantasma(TAMANO_CELDA * (COLUMNAS - 2) + TAMANO_CELDA // 2, TAMANO_CELDA + TAMANO_CELDA // 2, ROSA),
                        Fantasma(TAMANO_CELDA + TAMANO_CELDA // 2, TAMANO_CELDA * (FILAS - 2) + TAMANO_CELDA // 2, CELESTE),
                        Fantasma(TAMANO_CELDA * (COLUMNAS // 2) + TAMANO_CELDA // 2, TAMANO_CELDA * (FILAS // 2) + TAMANO_CELDA // 2, NARANJA)
                            ]                      
    # Dibujar
    ventana.fill(NEGRO)
    dibujar_laberinto()
    
    # Dibujar fantasmas
    for fantasma in fantasmas:
        fantasma.dibujar(pacman.poder_activo)
    
    # Dibujar Pacman
    pacman.dibujar()
    
    # Dibujar información del juego
    texto_puntaje = fuente_mediana.render(f"PUNTUACION: {pacman.puntuacion}", True, BLANCO)
    texto_nivel = fuente_mediana.render(f"NIVEL: {nivel}", True, BLANCO)
    texto_vidas = fuente_mediana.render(f"VIDAS: {pacman.vidas}", True, BLANCO)
    
    ventana.blit(texto_puntaje, (10, 10))
    ventana.blit(texto_nivel, (ANCHO - texto_nivel.get_width() - 10, 10))
    ventana.blit(texto_vidas, (10, ALTO - texto_vidas.get_height() - 10))
    
    # Efecto visual para cuando Pacman tiene poder
    if pacman.poder_activo:
        tiempo_restante = fuente_pequena.render(f"PODER: {pacman.tiempo_poder // 60 + 1}s", True, AMARILLO)
        ventana.blit(tiempo_restante, (ANCHO - tiempo_restante.get_width() - 10, ALTO - tiempo_restante.get_height() - 10))
    
    # Mensaje de victoria
    if contador_victoria > 0:
        texto_victoria = fuente_grande.render("¡NIVEL COMPLETADO!", True, AMARILLO)
        if contador_victoria > 60:  # Parpadeo del texto
            if contador_victoria % 30 < 15:
                ventana.blit(texto_victoria, (ANCHO // 2 - texto_victoria.get_width() // 2, ALTO // 2))
    
    pygame.display.flip()

pygame.quit()