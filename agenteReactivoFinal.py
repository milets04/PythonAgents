import random
from collections import deque

class SimpleLimpiezaAgente:
    """Agente reactivo que limpia suciedad, con memoria y que acumula puntos por valor de suciedad."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.puntos_limpieza = 0  ### De 'suciedad_limpiada' a 'puntos_limpieza'
        self.visitados = set()    # Memoria de posiciones visitadas

    def percibir(self, entorno):
        """Percibe el VALOR de la suciedad en su posición actual"""
        ### Ahora percibe el valor (0 si no hay, 1, 2, 3... si hay)
        return entorno.valor_suciedad(self.x, self.y) 

    def decidir_y_actuar(self, percepcion, entorno):
        """Decide qué acción tomar según la percepción y la memoria"""
        posicion_actual = (self.x, self.y)
        if posicion_actual not in self.visitados:
            self.visitados.add(posicion_actual)
            print(f"Registrando nueva posición en memoria: {posicion_actual}") 
        else:
            print(f"Posición ya registrada: {posicion_actual}")
        
        ### Reacciona si la percepción es mayor que 0 (hay suciedad)
        if percepcion > 0:
            return "limpiar"

        # Posibles movimientos
        movimientos = {
            "arriba": (self.x, self.y - 1),
            "abajo": (self.x, self.y + 1),
            "izquierda": (self.x - 1, self.y),
            "derecha": (self.x + 1, self.y)
        }

        movimientos_validos = {
            d: pos for d, pos in movimientos.items()
            if entorno.es_valido(*pos)
        }

        no_visitados = {
            d: pos for d, pos in movimientos_validos.items()
            if pos not in self.visitados
        }

        if no_visitados:
            direccion = random.choice(list(no_visitados.keys()))
        elif movimientos_validos: # Asegurarse de que hay movimientos válidos
            direccion = random.choice(list(movimientos_validos.keys()))
        else:
            return "quieto" # No hay a dónde moverse

        return direccion


class EntornoGrid:
    """Entorno: Grid 2D con suciedad de diferentes valores"""
    def __init__(self, ancho, alto, num_suciedad):
        self.ancho = ancho
        self.alto = alto
        ### CAMBIO: 'suciedad' ahora es un diccionario { (x, y): valor }
        self.suciedad = {} 

        # Generar suciedad aleatoria con valores
        for _ in range(num_suciedad):
            # Para no sobreescribir
            while True:
                x = random.randint(0, ancho - 1)
                y = random.randint(0, alto - 1)
                if (x, y) not in self.suciedad:
                    ### NUEVO: Asigna un valor aleatorio (ej. 1, 2 o 3)
                    valor_suciedad = random.randint(1, 3) 
                    self.suciedad[(x, y)] = valor_suciedad
                    break

    def valor_suciedad(self, x, y):
        """Retorna el valor de la suciedad en (x, y), o 0 si no hay."""
        ### NUEVO: Método para obtener el valor
        return self.suciedad.get((x, y), 0)

    def limpiar(self, x, y):
        ### CAMBIO: Ahora retorna el valor de la suciedad eliminada
        if (x, y) in self.suciedad:
            valor = self.suciedad[(x, y)]
            del self.suciedad[(x, y)] # Elimina la suciedad del diccionario
            return valor
        return 0 # No había suciedad

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
        mapa_suciedad = {
            1: "💧", # Suciedad valor 1
            2: "💩", # Suciedad valor 2
            3: "☣️"  # Suciedad valor 3
        }
        for y in range(self.alto):
            for x in range(self.ancho):
                if x == agente.x and y == agente.y:
                    print("🤖", end=" ")
                ### CAMBIO: Mostrar ícono según el valor de la suciedad
                elif (x, y) in self.suciedad:
                    valor = self.suciedad[(x, y)]
                    print(mapa_suciedad.get(valor, "❓"), end=" ")
                else:
                    print("⬜", end=" ")
            print()
        print()


# Simulación
def simular_limpieza(pasos=20): 
    entorno = EntornoGrid(5, 5, 8)
    agente = SimpleLimpiezaAgente(2, 2)

    print("=== SIMULACIÓN: AGENTE CON MEMORIA Y SUCIEDAD POR VALOR ===\n")
    print("Estado inicial:")
    entorno.mostrar(agente)

    for paso in range(pasos):
        percepcion = agente.percibir(entorno)
        accion = agente.decidir_y_actuar(percepcion, entorno)

        if accion == "limpiar":
            ### CAMBIO: Capturar el valor retornado por 'limpiar'
            valor_limpiado = entorno.limpiar(agente.x, agente.y)
            if valor_limpiado > 0:
                ### CAMBIO: Sumar el valor a los puntos del agente
                agente.puntos_limpieza += valor_limpiado
                print(f"Paso {paso + 1}: Limpiando en ({agente.x}, {agente.y}). ¡+{valor_limpiado} puntos!")
        elif accion != "quieto":
            entorno.mover_agente(agente, accion)
            print(f"Paso {paso + 1}: Moviéndose {accion}")
        else:
            print(f"Paso {paso + 1}: Quieto.")


        # Mostrar entorno cada ciertos pasos
        if paso % 3 == 0:
            entorno.mostrar(agente)

        if len(entorno.suciedad) == 0:
            print("\n¡Toda la suciedad ha sido limpiada!")
            break

    print("\nEstado final:")
    entorno.mostrar(agente)
    ### CAMBIO: Mostrar puntos en lugar de cantidad
    print(f"Puntos de limpieza totales: {agente.puntos_limpieza}")
    print(f"Suciedad restante (items): {len(entorno.suciedad)}")
    print(f"Casillas visitadas: {len(agente.visitados)}")


if __name__ == "__main__":
    simular_limpieza()