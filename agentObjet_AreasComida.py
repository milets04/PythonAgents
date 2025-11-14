import random
import numpy as np                 # Para el heatmap
from collections import deque
import matplotlib.pyplot as plt    # Para graficar

class AgenteRecolector:
    """Agente que aprende un mapa de calor sobre las zonas ricas en comida,
    y actualiza el mapa al recolectar."""

    def __init__(self, x, y, entorno):
        self.x = x
        self.y = y
        self.entorno = entorno
        self.energia = 100
        self.puntos_recolectados = 0 # Se usan puntos
        self.plan = []

        # Memoria espacial (mapa de calor)
        # Inicia un mapa de 8x8 lleno de ceros.
        self.mapa_comida = np.zeros((entorno.ancho, entorno.alto))

    def percibir(self):
        """Percibe la comida visible y REFUERZA el mapa de calor"""
        comida_visible = self.entorno.obtener_comida_visible(self.x, self.y, radio=5)

        # Aprendizaje: reforzar memoria espacial
        for (cx, cy) in comida_visible:
            # Refuerza la creencia de que esta celda es buena
            self.mapa_comida[cx, cy] += 1 
            
        return comida_visible

    def planificar_ruta(self, objetivo):
        """Ruta al objetivo mediante BFS"""
        if objetivo is None:
            return []
        cola = deque([(self.x, self.y, [])])
        visitados = {(self.x, self.y)}
        while cola:
            x, y, camino = cola.popleft()
            if (x, y) == objetivo:
                return camino
            for dx, dy, direccion in [(0, -1, "arriba"), (0, 1, "abajo"),
                                      (-1, 0, "izquierda"), (1, 0, "derecha")]:
                nx, ny = x + dx, y + dy
                if (self.entorno.es_valido(nx, ny) and
                    (nx, ny) not in visitados and
                    not self.entorno.hay_obstaculo(nx, ny)):
                    visitados.add((nx, ny))
                    cola.append((nx, ny, camino + [direccion]))
        return []

    def decidir(self, comida_visible):
        """Decide hacia dónde ir, priorizando la comida visible,
        luego la memoria (heatmap)."""

        if self.plan:
            return self.plan.pop(0)

        # Ir a la comida visible más cercana
        if comida_visible:
            objetivo = min(comida_visible,
                           key=lambda c: abs(c[0] - self.x) + abs(c[1] - self.y))
            self.plan = self.planificar_ruta(objetivo)
            if self.plan:
                return self.plan.pop(0)

        # Si no ve nada, consultar el "mapa de calor"
        max_valor_memoria = np.max(self.mapa_comida)
        
        if max_valor_memoria > 0:
            # Ir al punto más "caliente" del mapa
            # np.unravel_index convierte el índice lineal en coordenadas (ej. (3, 2))
            objetivo = np.unravel_index(np.argmax(self.mapa_comida), self.mapa_comida.shape)
            
            # Asegurarse de que el objetivo no sea él mismo 
            if objetivo == (self.x, self.y):
                # Si está sobre la mejor opción, pero no hay comida, la resetea
                self.mapa_comida[self.x, self.y] = 0
            else:
                print(f"Agente en ({self.x},{self.y}): No ve comida. Usando memoria: ir a {objetivo} (Valor: {max_valor_memoria})")
                self.plan = self.planificar_ruta(objetivo)
                if self.plan:
                    return self.plan.pop(0)

        # Si no ve nada y su memoria está vacía (todo 0), explora
        return random.choice(["arriba", "abajo", "izquierda", "derecha"])

    def actuar(self, accion):
        """Mueve el agente, recolecta comida y ACTUALIZA (reduce) el mapa de calor"""

        # Determinar la posición objetivo
        nx, ny = self.x, self.y
        if accion == "arriba": ny -= 1
        elif accion == "abajo": ny += 1
        elif accion == "izquierda": nx -= 1
        elif accion == "derecha": nx += 1

        # Validar la posición objetivo antes de moverse
        if self.entorno.es_valido(nx, ny) and not self.entorno.hay_obstaculo(nx, ny):
            self.x, self.y = nx, ny
        
        # Recolectar comida y actualizar memoria
        valor_comida = self.entorno.recolectar_comida(self.x, self.y)
        
        if valor_comida > 0:
            self.puntos_recolectados += valor_comida
            self.energia += 20
            self.plan = [] # Borra el plan
            
            # Resetea el valor de esta celda a 0 porque ya no es prometedora.
            print(f"Agente: ¡Comida encontrada en ({self.x}, {self.y})! +{valor_comida}. Reseteando heatmap.")
            self.mapa_comida[self.x, self.y] = 0

        self.energia -= 1

    def update(self):
        """Ciclo del agente"""
        if self.energia > 0:
            comida_visible = self.percibir()
            decision = self.decidir(comida_visible)
            self.actuar(decision)

# ENTORNO 
class EntornoRecoleccion:
    """Entorno con comida (con valor) y obstáculos"""

    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.comida = {}  
        self.obstaculos = set()

        # Generar comida
        for _ in range(10):
            x, y = random.randint(0, ancho-1), random.randint(0, alto-1)
            self.comida[(x, y)] = random.randint(1, 3) # Valor

        # Generar obstáculos
        for _ in range(8):
            while True:
                x, y = random.randint(0, ancho-1), random.randint(0, alto-1)
                if (x, y) not in self.comida:
                    self.obstaculos.add((x, y))
                    break

    def es_valido(self, x, y):
        return 0 <= x < self.ancho and 0 <= y < self.alto

    def hay_obstaculo(self, x, y):
        return (x, y) in self.obstaculos

    def hay_comida(self, x, y):
        return (x, y) in self.comida

    def recolectar_comida(self, x, y):
        # pop elimina y retorna el valor
        if (x, y) in self.comida:
            valor = self.comida.pop((x, y)) 
            return valor
        return 0

    def obtener_comida_visible(self, x, y, radio):
        visible = []
        for (fx, fy) in list(self.comida.keys()):
            dist = abs(fx - x) + abs(fy - y)
            if dist <= radio:
                visible.append((fx, fy))
        return visible
    
    # Función 'mostrar' del entorno 
    def mostrar(self, agente):
        """Muestra el entorno en la consola con emojis"""
        for y in range(self.alto):
            for x in range(self.ancho):
                if x == agente.x and y == agente.y:
                    print("🤖", end=" ")
                elif (x, y) in self.obstaculos:
                    print("🧱", end=" ")
                elif (x, y) in self.comida:
                    print("🍎", end=" ")
                else:
                    print("⬜", end=" ")
            print()
        print()

# SIMULACIÓN 
def simular_recoleccion(pasos=30):
    entorno = EntornoRecoleccion(8, 8)
    
    while True:
        x_ini, y_ini = random.randint(0, 7), random.randint(0, 7)
        if (x_ini, y_ini) not in entorno.obstaculos and (x_ini, y_ini) not in entorno.comida:
            agente = AgenteRecolector(x_ini, y_ini, entorno)
            break

    print("=== SIMULACIÓN: AGENTE CON APRENDIZAJE (HEATMAP) ===\n")
    print("Estado inicial:")
    
    ### Configuración inicial de Matplotlib
    plt.ion()  # Activar modo interactivo
    fig, ax = plt.subplots() # Crear figura y ejes
    # Usamos .T (transpuesto) para que (x,y) de numpy coincida con (x,y) visual
    im = ax.imshow(agente.mapa_comida.T, cmap='viridis', vmin=0, vmax=5) 
    fig.colorbar(im, ax=ax) # barra de color
    ax.set_title("Mapa de Calor del Agente (Aprendizaje)")

    for paso in range(pasos):
        agente.update()

        # Actualiza el log Y el gráfico cada 5 pasos
        if (paso + 1) % 5 == 0:
            print(f"\nPaso {paso + 1} | Energía: {agente.energia} | Puntos: {agente.puntos_recolectados}")
            
            entorno.mostrar(agente) 
            
            ### Actualizar el gráfico
            ax.set_title(f"Mapa de Calor (Paso {paso + 1})")
            im.set_data(agente.mapa_comida.T) # Actualizar datos del heatmap
            fig.canvas.draw()
            fig.canvas.flush_events()
            
            # tiempo de pausa
            plt.pause(2.0) # Pausa de 2 segundos para ver el gráfico

        if agente.energia <= 0:
            print("\nEl agente se quedó sin energía.")
            break
        if len(entorno.comida) == 0:
            print("\nToda la comida ha sido recolectada.")
            break

    print(f"\nResultado final:")
    print(f"Puntos recolectados: {agente.puntos_recolectados}")
    print(f"Energía restante: {agente.energia}")

    # Imprimir el mapa de calor final en la consola
    print("\nMapa de calor final (creencias del agente):\n", agente.mapa_comida.T)

    # Mostrar gráfico final estático
    plt.ioff() # Desactivar modo interactivo
    plt.figure() # Crear una nueva figura final
    plt.title("Mapa de Calor Final")
    plt.imshow(agente.mapa_comida.T, cmap='viridis', vmin=0, vmax=5)
    plt.colorbar()
    print("Mostrando gráfico final. Cierra la ventana del gráfico para terminar.")
    plt.show() # Mostrar hasta que el usuario cierre


if __name__ == "__main__":
    simular_recoleccion()