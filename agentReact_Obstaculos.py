import random
from collections import deque

class SimpleLimpiezaAgente:
    """Agente reactivo que limpia suciedad, con memoria y que evita obstáculos."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.puntos_limpieza = 0
        self.visitados = set()    # Memoria de posiciones visitadas

    def percibir(self, entorno):
        """Percibe el VALOR de la suciedad en su posición actual"""
        return entorno.valor_suciedad(self.x, self.y) 

    # Se añade 'paso_actual' para usarlo en los prints
    def decidir_y_actuar(self, percepcion, entorno, paso_actual):
        """Decide qué acción tomar según la percepción, memoria y obstáculos"""
        
        # Añadir posición actual a la memoria
        posicion_actual = (self.x, self.y)
        self.visitados.add(posicion_actual)
        
        if percepcion > 0:
            return "limpiar"

        # Posibles movimientos
        movimientos = {
            "arriba": (self.x, self.y - 1),
            "abajo": (self.x, self.y + 1),
            "izquierda": (self.x - 1, self.y),
            "derecha": (self.x + 1, self.y)
        }

        # Lógica de validación expandida para añadir el print
        movimientos_validos = {}
        for d, pos in movimientos.items():
            if not entorno.es_valido(*pos):
                continue # Movimiento fuera de los límites
            
            if entorno.hay_obstaculo(*pos):
                print(f"Paso {paso_actual}: Obstáculo percibido en {pos}, evitando.")
                continue # Es un obstáculo, no añadir a movimientos válidos
            
            # Si llega aquí, es válido y no es obstáculo
            movimientos_validos[d] = pos

        # Filtrar movimientos a casillas no visitadas
        no_visitados = {
            d: pos for d, pos in movimientos_validos.items()
            if pos not in self.visitados
        }

        # Lógica de decisión para evitar quedarse atrapado
        # Lógica para el "callejón sin salida"
        if no_visitados:
            # Moverse a un lugar nuevo
            direccion = random.choice(list(no_visitados.keys()))
        elif movimientos_validos: 
            # Si no hay nuevos, *debe* retroceder a un lugar ya visitado para escapar.
            print(f"Paso {paso_actual}: No hay celdas nuevas. Retrocediendo por {posicion_actual}...")
            direccion = random.choice(list(movimientos_validos.keys()))
        else:
            # No hay a dónde moverse
            return "quieto" 

        return direccion


class EntornoGrid:
    """Entorno: Grid 2D con suciedad, valores y múltiples tipos de obstáculos"""
    
    def __init__(self, ancho, alto, num_suciedad, num_obstaculos): 
        self.ancho = ancho
        self.alto = alto
        self.suciedad = {} 
        self.obstaculos = {} 
        
        ### Reducido a dos tipos de obstáculos
        self.tipos_obstaculos_posibles = ["🧱", "🌳"] 

        # Generar suciedad aleatoria con valores
        for _ in range(num_suciedad):
            while True:
                x = random.randint(0, ancho - 1)
                y = random.randint(0, alto - 1)
                if (x, y) not in self.suciedad:
                    valor_suciedad = random.randint(1, 3) 
                    self.suciedad[(x, y)] = valor_suciedad
                    break
        
        # Generar obstáculos aleatorios
        for _ in range(num_obstaculos):
            while True:
                x = random.randint(0, ancho - 1)
                y = random.randint(0, alto - 1)
                if (x, y) not in self.suciedad and (x, y) not in self.obstaculos:
                    tipo = random.choice(self.tipos_obstaculos_posibles)
                    self.obstaculos[(x, y)] = tipo
                    break

    def valor_suciedad(self, x, y):
        return self.suciedad.get((x, y), 0)

    def hay_obstaculo(self, x, y):
        return (x, y) in self.obstaculos

    def limpiar(self, x, y):
        if (x, y) in self.suciedad:
            valor = self.suciedad[(x, y)]
            del self.suciedad[(x, y)]
            return valor
        return 0

    def es_valido(self, x, y):
        return 0 <= x < self.ancho and 0 <= y < self.alto

    def mover_agente(self, agente, direccion):
        if direccion == "arriba" and agente.y > 0:
            agente.y -= 1
        elif direccion == "abajo" and agente.y < self.alto - 1:
            agente.y += 1
        elif direccion == "izquierda" and agente.x > 0:
            agente.x -= 1
        elif direccion == "derecha" and agente.x < self.ancho - 1:
            agente.x += 1

    def mostrar(self, agente):
        mapa_suciedad = {
            1: "💧", 2: "💩", 3: "☣️"
        }
        for y in range(self.alto):
            for x in range(self.ancho):
                if x == agente.x and y == agente.y:
                    print("🤖", end=" ")
                elif (x, y) in self.obstaculos:
                    print(self.obstaculos[(x, y)], end=" ")
                elif (x, y) in self.suciedad:
                    valor = self.suciedad[(x, y)]
                    print(mapa_suciedad.get(valor, "❓"), end=" ")
                else:
                    print("⬜", end=" ")
            print()
        print()


# Simulación (parámetros originales de pasos)
def simular_limpieza(pasos=20): 
    
    entorno = EntornoGrid(5, 5, num_suciedad=8, num_obstaculos=5)
    
    while True:
        x_ini = random.randint(0, entorno.ancho - 1)
        y_ini = random.randint(0, entorno.alto - 1)
        # Asegurar que no inicie sobre obstáculo O suciedad
        if not entorno.hay_obstaculo(x_ini, y_ini) and entorno.valor_suciedad(x_ini, y_ini) == 0:
            agente = SimpleLimpiezaAgente(x_ini, y_ini)
            break

    print("=== SIMULACIÓN: AGENTE CON MEMORIA, VALOR Y OBSTÁCULOS ===\n")
    print("Estado inicial:")
    entorno.mostrar(agente)

    for paso in range(pasos):
        percepcion = agente.percibir(entorno)
        
        ### Pasar 'paso + 1' a la función de decisión
        accion = agente.decidir_y_actuar(percepcion, entorno, paso + 1) 

        if accion == "limpiar":
            valor_limpiado = entorno.limpiar(agente.x, agente.y)
            if valor_limpiado > 0:
                agente.puntos_limpieza += valor_limpiado
                print(f"Paso {paso + 1}: Limpiando en ({agente.x}, {agente.y}). ¡+{valor_limpiado} puntos!")
        elif accion != "quieto":
            entorno.mover_agente(agente, accion)
            print(f"Paso {paso + 1}: Moviéndose {accion}")
        else:
            # Añadido número de paso
            print(f"Paso {paso + 1}: Quieto (atrapado).")


        # Mostrar entorno
        if (paso + 1) % 3 == 0 or paso == pasos - 1:
            print(f"--- Estado en paso {paso+1} ---")
            entorno.mostrar(agente)
    
        if len(entorno.suciedad) == 0:
            print("\n¡Toda la suciedad ha sido limpiada!")
            break

    print("\nEstado final:")
    entorno.mostrar(agente)
    print(f"Puntos de limpieza totales: {agente.puntos_limpieza}")
    print(f"Suciedad restante (items): {len(entorno.suciedad)}")
    print(f"Casillas visitadas: {len(agente.visitados)}")


if __name__ == "__main__":
    simular_limpieza()