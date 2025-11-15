import random

class AgenteCooperativo:
    """Agente que puede comunicarse con otros"""

    def __init__(self, id, x, y, entorno):
        self.id = id
        self.x = x
        self.y = y
        self.entorno = entorno
        self.comida_recolectada = 0
        self.objetivo = None
        self.mensajes = []  # Mensajes recibidos

    def enviar_mensaje(self, destinatarios, tipo, contenido):
        """Comunica información a otros agentes"""
        for agente in destinatarios:
            agente.recibir_mensaje(self.id, tipo, contenido)

    def recibir_mensaje(self, remitente, tipo, contenido):
        """Recibe mensajes de otros agentes"""
        self.mensajes.append({
            'de': remitente,
            'tipo': tipo,
            'contenido': contenido
        })

    def procesar_mensajes(self):
        """Procesa mensajes recibidos"""
        comida_reportada = []
        for msg in self.mensajes:
            if msg['tipo'] == 'comida_encontrada':
                comida_reportada.append(msg['contenido'])
        self.mensajes.clear()
        return comida_reportada

    def percibir(self):
        """Percibe comida cercana"""
        return self.entorno.obtener_comida_cercana(self.x, self.y, radio=3)

    def decidir_y_actuar(self, otros_agentes):
        """Ciclo de decisión"""
        # Procesar comunicaciones
        comida_compartida = self.procesar_mensajes()

        # Percibir entorno local
        comida_local = self.percibir()

        # Compartir descubrimientos con otros
        if comida_local and otros_agentes:
            for pos in comida_local:
                self.enviar_mensaje(otros_agentes, 'comida_encontrada', pos)

        # Decidir objetivo (evitar duplicados gracias a la comunicación)
        todas_opciones = list(set(comida_local + comida_compartida))
        if todas_opciones and not self.objetivo:
            # Elegir comida más cercana
            self.objetivo = min(todas_opciones,
                               key=lambda p: abs(p[0] - self.x) + abs(p[1] - self.y))

        # Moverse hacia objetivo
        if self.objetivo:
            if (self.x, self.y) == self.objetivo:
                if self.entorno.recolectar_comida(self.x, self.y):
                    self.comida_recolectada += 1
                self.objetivo = None
            else:
                # Movimiento simple hacia objetivo
                dx = 1 if self.objetivo[0] > self.x else (-1 if self.objetivo[0] < self.x else 0)
                dy = 1 if self.objetivo[1] > self.y else (-1 if self.objetivo[1] < self.y else 0)

                if dx != 0:
                    nx, ny = self.x + dx, self.y
                elif dy != 0:
                    nx, ny = self.x, self.y + dy
                else:
                    nx, ny = self.x, self.y

                if self.entorno.es_valido(nx, ny):
                    self.x, self.y = nx, ny
        else:
            # Movimiento aleatorio
            direccion = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            nx, ny = self.x + direccion[0], self.y + direccion[1]
            if self.entorno.es_valido(nx, ny):
                self.x, self.y = nx, ny


class EntornoMultiAgente:
    """Entorno para múltiples agentes"""

    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.comida = set()
        for _ in range(15):
            x, y = random.randint(0, ancho-1), random.randint(0, alto-1)
            self.comida.add((x, y))

    def es_valido(self, x, y):
        return 0 <= x < self.ancho and 0 <= y < self.alto

    def obtener_comida_cercana(self, x, y, radio):
        return [pos for pos in self.comida
                if abs(pos[0] - x) + abs(pos[1] - y) <= radio]

    def recolectar_comida(self, x, y):
        if (x, y) in self.comida:
            self.comida.remove((x, y))
            return True
        return False

    def mostrar(self, agentes):
        grid = [["⬜" for _ in range(self.ancho)] for _ in range(self.alto)]
        for pos in self.comida:
            grid[pos[1]][pos[0]] = "🍎"
        for agente in agentes:
            # si hay colisión, mostrará el último agente iterado
            grid[agente.y][agente.x] = f"{agente.id}"
        for fila in grid:
            print(" ".join(fila))
        print()


# Simulación multi-agente
def simular_multi_agente(num_agentes=3, pasos=25):
    entorno = EntornoMultiAgente(10, 10)
    agentes = []
    for i in range(num_agentes):
        x, y = random.randint(0, 9), random.randint(0, 9)
        agentes.append(AgenteCooperativo(i+1, x, y, entorno))

    print("=== SIMULACIÓN: SISTEMA MULTI-AGENTE COOPERATIVO ===\n")
    print("Estado inicial:")
    entorno.mostrar(agentes)

    for paso in range(pasos):
        for agente in agentes:
            otros = [a for a in agentes if a.id != agente.id]
            agente.decidir_y_actuar(otros)

        if paso % 5 == 0:
            print(f"\nPaso {paso + 1}:")
            entorno.mostrar(agentes)
            for agente in agentes:
                print(f"Agente {agente.id}: {agente.comida_recolectada} comida")

        if len(entorno.comida) == 0:
            print("\n¡Toda la comida ha sido recolectada!")
            break

    print("\nResultado final:")
    total = sum(a.comida_recolectada for a in agentes)
    for agente in agentes:
        print(f"Agente {agente.id}: {agente.comida_recolectada} comida")
    print(f"Total recolectado: {total}")


if __name__ == "__main__":
    simular_multi_agente()
