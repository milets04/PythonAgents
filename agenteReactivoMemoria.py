import random
from collections import deque

class SimpleLimpiezaAgente:
    """Agente reactivo que limpia suciedad cuando la detecta, con memoria de lugares visitados"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.suciedad_limpiada = 0
        self.visitados = set()  # Memoria de posiciones visitadas

    def percibir(self, entorno):
        """Percibe si hay suciedad en su posición actual"""
        return entorno.hay_suciedad(self.x, self.y)

    def decidir_y_actuar(self, percepcion, entorno):
        """Decide qué acción tomar según la percepción y la memoria"""
        # Guardar posición actual como visitada
        posicion_actual = (self.x, self.y)
        if posicion_actual not in self.visitados:
            self.visitados.add(posicion_actual)
            print(f"Registrando nueva posición en memoria: {posicion_actual}")
        else:
            print(f"Posición ya registrada: {posicion_actual}")

        if percepcion:
            return "limpiar"

        # Posibles movimientos
        movimientos = {
            "arriba": (self.x, self.y - 1),
            "abajo": (self.x, self.y + 1),
            "izquierda": (self.x - 1, self.y),
            "derecha": (self.x + 1, self.y)
        }

        # Filtrar movimientos válidos (dentro del entorno)
        movimientos_validos = {
            d: pos for d, pos in movimientos.items()
            if entorno.es_valido(*pos)
        }

        # Evitar volver a posiciones ya visitadas
        no_visitados = {
            d: pos for d, pos in movimientos_validos.items()
            if pos not in self.visitados
        }

        # Elegir movimiento
        if no_visitados:
            direccion = random.choice(list(no_visitados.keys()))
        else:
            # Si ya visitó todo alrededor, se mueve igual para evitar bloqueo
            direccion = random.choice(list(movimientos_validos.keys()))

        return direccion


class EntornoGrid:
    """Entorno: Grid 2D con suciedad"""
    def __init__(self, ancho, alto, num_suciedad):
        self.ancho = ancho
        self.alto = alto
        self.suciedad = set()

        # Generar suciedad aleatoria
        for _ in range(num_suciedad):
            x = random.randint(0, ancho - 1)
            y = random.randint(0, alto - 1)
            self.suciedad.add((x, y))

    def hay_suciedad(self, x, y):
        return (x, y) in self.suciedad

    def limpiar(self, x, y):
        if (x, y) in self.suciedad:
            self.suciedad.remove((x, y))
            return True
        return False

    def es_valido(self, x, y):
        """Verifica si la posición está dentro del grid"""
        return 0 <= x < self.ancho and 0 <= y < self.alto

    def mover_agente(self, agente, direccion):
        """Mueve el agente en la dirección especificada"""
        if direccion == "arriba" and agente.y > 0:
            agente.y -= 1
        elif direccion == "abajo" and agente.y < self.alto - 1:
            agente.y += 1
        elif direccion == "izquierda" and agente.x > 0:
            agente.x -= 1
        elif direccion == "derecha" and agente.x < self.ancho - 1:
            agente.x += 1

    def mostrar(self, agente):
        """Visualización simple en consola"""
        for y in range(self.alto):
            for x in range(self.ancho):
                if x == agente.x and y == agente.y:
                    print("🤖", end=" ")
                elif (x, y) in self.suciedad:
                    print("💩", end=" ")
                else:
                    print("⬜", end=" ")
            print()
        print()


# Simulación
def simular_limpieza(pasos=30):
    entorno = EntornoGrid(6, 6, 10)
    agente = SimpleLimpiezaAgente(2, 2)

    print("=== SIMULACIÓN: AGENTE REACTIVO CON MEMORIA ===\n")
    print("Estado inicial:")
    entorno.mostrar(agente)

    for paso in range(pasos):
        percepcion = agente.percibir(entorno)
        accion = agente.decidir_y_actuar(percepcion, entorno)

        if accion == "limpiar":
            if entorno.limpiar(agente.x, agente.y):
                agente.suciedad_limpiada += 1
                print(f"Paso {paso + 1}: Limpiando en ({agente.x}, {agente.y})")
        else:
            entorno.mover_agente(agente, accion)
            print(f"Paso {paso + 1}: Moviéndose {accion}")

        # Mostrar entorno cada ciertos pasos
        if paso % 5 == 0:
            entorno.mostrar(agente)

        if len(entorno.suciedad) == 0:
            print("\n¡Toda la suciedad ha sido limpiada!")
            break

    print("\nEstado final:")
    entorno.mostrar(agente)
    print(f"Suciedad limpiada: {agente.suciedad_limpiada}")
    print(f"Suciedad restante: {len(entorno.suciedad)}")
    print(f"Casillas visitadas: {len(agente.visitados)}")


if __name__ == "__main__":
    simular_limpieza()
