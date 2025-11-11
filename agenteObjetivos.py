import random
from collections import deque

class AgenteRecolector:
    """Agente que planifica rutas hacia comida usando búsqueda"""

    def __init__(self, x, y, entorno):
        self.x = x
        self.y = y
        self.entorno = entorno
        self.energia = 100
        self.comida_recolectada = 0
        self.plan = []  # Secuencia de acciones planificadas

    def percibir(self):
        """Percibe la comida visible en el entorno"""
        return self.entorno.obtener_comida_visible(self.x, self.y, radio=5)

    def planificar_ruta(self, objetivo):
        """Búsqueda para encontrar camino al objetivo (BFS)"""
        if objetivo is None:
            return []

        cola = deque([(self.x, self.y, [])])
        visitados = {(self.x, self.y)}

        while cola:
            x, y, camino = cola.popleft()

            # ¿Llegó al objetivo?
            if (x, y) == objetivo:
                return camino

            # Explorar vecinos
            for dx, dy, direccion in [(0, -1, "arriba"), (0, 1, "abajo"),
                                      (-1, 0, "izquierda"), (1, 0, "derecha")]:
                nx, ny = x + dx, y + dy
                if (self.entorno.es_valido(nx, ny) and
                    (nx, ny) not in visitados and
                    not self.entorno.hay_obstaculo(nx, ny)):
                    visitados.add((nx, ny))
                    cola.append((nx, ny, camino + [direccion]))

        return []  # No hay camino

    def decidir(self, comida_visible):
        """Decide qué comida perseguir y planifica ruta"""
        if not self.plan:  # Si no hay plan, crear uno nuevo
            if comida_visible:
                # Elegir comida más cercana (distancia Manhattan)
                objetivo = min(comida_visible,
                               key=lambda c: abs(c[0] - self.x) + abs(c[1] - self.y))
                self.plan = self.planificar_ruta(objetivo)

        if self.plan:
            return self.plan.pop(0)
        else:
            return random.choice(["arriba", "abajo", "izquierda", "derecha"])

    def actuar(self, accion):
        """Ejecuta la acción"""
        if accion == "arriba" and self.y > 0:
            self.y -= 1
        elif accion == "abajo" and self.y < self.entorno.alto - 1:
            self.y += 1
        elif accion == "izquierda" and self.x > 0:
            self.x -= 1
        elif accion == "derecha" and self.x < self.entorno.ancho - 1:
            self.x += 1

        # Recolectar comida si está en esta posición
        if self.entorno.hay_comida(self.x, self.y):
            self.entorno.recolectar_comida(self.x, self.y)
            self.comida_recolectada += 1
            self.energia += 20
            self.plan = []  # Limpiar plan actual

        self.energia -= 1

    def update(self):
        """Ciclo completo: Percibir → Decidir → Actuar"""
        if self.energia > 0:
            percepcion = self.percibir()
            decision = self.decidir(percepcion)
            self.actuar(decision)


class EntornoRecoleccion:
    """Entorno con comida y obstáculos"""

    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.comida = {}  # {(x, y): valor}
        self.obstaculos = set()

        # Generar comida
        for _ in range(10):
            x, y = random.randint(0, ancho-1), random.randint(0, alto-1)
            self.comida[(x, y)] = random.randint(1, 3)

        # Generar obstáculos
        for _ in range(8):
            x, y = random.randint(0, ancho-1), random.randint(0, alto-1)
            self.obstaculos.add((x, y))

    def es_valido(self, x, y):
        return 0 <= x < self.ancho and 0 <= y < self.alto

    def hay_obstaculo(self, x, y):
        return (x, y) in self.obstaculos

    def hay_comida(self, x, y):
        return (x, y) in self.comida

    def recolectar_comida(self, x, y):
        if (x, y) in self.comida:
            del self.comida[(x, y)]

    def obtener_comida_visible(self, x, y, radio):
        """Retorna comida dentro del radio de visión"""
        visible = []
        for (fx, fy) in list(self.comida.keys()):
            dist = abs(fx - x) + abs(fy - y)
            if dist <= radio:
                visible.append((fx, fy))
        return visible

    def mostrar(self, agente):
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


# Simulación
def simular_recoleccion(pasos=30):
    entorno = EntornoRecoleccion(8, 8)
    agente = AgenteRecolector(0, 0, entorno)
    print("=== SIMULACIÓN: AGENTE BASADO EN OBJETIVOS ===\n")
    print("Estado inicial:")
    entorno.mostrar(agente)

    for paso in range(pasos):
        agente.update()

        if paso % 5 == 0:
            print(f"\nPaso {paso + 1}:")
            entorno.mostrar(agente)
            print(f"Comida: {agente.comida_recolectada} | Energía: {agente.energia}")

        if agente.energia <= 0:
            print("\n¡El agente se quedó sin energía!")
            break

        if len(entorno.comida) == 0:
            print("\n¡Toda la comida ha sido recolectada!")
            break

    print(f"\nResultado final:")
    print(f"Comida recolectada: {agente.comida_recolectada}")
    print(f"Energía restante: {agente.energia}")


if __name__ == "__main__":
    simular_recoleccion()
