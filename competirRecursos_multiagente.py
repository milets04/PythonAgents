import random

class AgenteCooperativo:
    """Agente que puede comunicarse con otros para evitar objetivos duplicados"""

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
        """Procesa mensajes recibidos, separando comida de objetivos reclamados"""
        comida_reportada = []
        ### Lista para guardar objetivos que otros agentes ya eligieron
        objetivos_reclamados = []
        
        for msg in self.mensajes:
            if msg['tipo'] == 'comida_encontrada':
                comida_reportada.append(msg['contenido'])
            ### Procesar el nuevo tipo de mensaje
            elif msg['tipo'] == 'voy_a':
                objetivos_reclamados.append(msg['contenido'])
                
        self.mensajes.clear()
        
        ### Retorna ambas listas
        return comida_reportada, objetivos_reclamados

    def percibir(self):
        """Percibe comida cercana"""
        return self.entorno.obtener_comida_cercana(self.x, self.y, radio=3)

    def decidir_y_actuar(self, otros_agentes):
        """Ciclo de decisión mejorado con evitación de objetivos"""
        
        # Procesar comunicaciones
        ### Recibe dos listas
        comida_compartida, objetivos_reclamados = self.procesar_mensajes()

        # Percibir entorno local
        comida_local = self.percibir()

        # Compartir descubrimientos con otros 
        if comida_local and otros_agentes:
            for pos in comida_local:
                self.enviar_mensaje(otros_agentes, 'comida_encontrada', pos)

        # Decidir objetivo
        
        ### Verificar si el objetivo actual sigue siendo válido
        if self.objetivo:
            # Si la comida ya no está (otro agente la tomó), borra el objetivo
            if not self.entorno.hay_comida(self.objetivo[0], self.objetivo[1]):
                print(f"Agente {self.id}: Mi objetivo {self.objetivo} ya fue tomado. Buscando uno nuevo.")
                self.objetivo = None

        # Si no tiene un objetivo válido, buscar uno nuevo
        if not self.objetivo:
            # Combina la comida local y la compartida
            todas_opciones = list(set(comida_local + comida_compartida))
            
            ### Lógica de evitación
            # Filtra la lista, quitando objetivos ya reclamados por otros
            opciones_disponibles = [
                pos for pos in todas_opciones
                if pos not in objetivos_reclamados
            ]

            # Elige el objetivo más cercano de la lista disponible
            if opciones_disponibles:
                self.objetivo = min(opciones_disponibles,
                                    key=lambda p: abs(p[0] - self.x) + abs(p[1] - self.y))
                
                ### Comunica la decisión a otros agentes
                print(f"Agente {self.id}: Objetivo fijado en {self.objetivo}. Comunicando...")
                self.enviar_mensaje(otros_agentes, 'voy_a', self.objetivo)

        # Moverse hacia el objetivo
        if self.objetivo:
            if (self.x, self.y) == self.objetivo:
                # Llegó al objetivo
                if self.entorno.recolectar_comida(self.x, self.y):
                    self.comida_recolectada += 1
                    print(f"Agente {self.id}: ¡Recolecté comida en {self.objetivo}!")
                self.objetivo = None # Limpiar objetivo
            else:
                # Movimiento simple paso a paso (eje X, luego eje Y)
                nx, ny = self.x, self.y
                dx = 1 if self.objetivo[0] > self.x else (-1 if self.objetivo[0] < self.x else 0)
                dy = 1 if self.objetivo[1] > self.y else (-1 if self.objetivo[1] < self.y else 0)

                # Moverse primero en X, si no, en Y
                if dx != 0 and self.entorno.es_valido(self.x + dx, self.y):
                    self.x += dx
                elif dy != 0 and self.entorno.es_valido(self.x, self.y + dy):
                    self.y += dy
        else:
            # Movimiento aleatorio si no hay objetivo
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

    ### Método para que los agentes verifiquen la comida
    def hay_comida(self, x, y):
        return (x, y) in self.comida

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
        
        # Mostrar agentes
        for agente in agentes:
            # El ID se cambió por emojis
            emoji_id = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣"}.get(agente.id, f"{agente.id}")
            grid[agente.y][agente.x] = emoji_id
            
        for fila in grid:
            print(" ".join(fila))
        print()


# Simulación multi-agente
def simular_multi_agente(num_agentes=3, pasos=25):
    entorno = EntornoMultiAgente(10, 10)
    agentes = []
    for i in range(num_agentes):
        while True:
            x, y = random.randint(0, 9), random.randint(0, 9)
            # Asegurar que no inicien sobre comida
            if (x,y) not in entorno.comida:
                agentes.append(AgenteCooperativo(i+1, x, y, entorno))
                break

    print("=== SIMULACIÓN: SISTEMA MULTI-AGENTE (EVITACIÓN DE OBJETIVOS) ===\n")
    print("Estado inicial:")
    entorno.mostrar(agentes)

    for paso in range(pasos):
        print(f"\n--- Paso {paso + 1} ---") 
        
        # Reordenar agentes aleatoriamente en cada paso
        # Esto evita que el Agente 1 siempre tenga la "ventaja" de actuar primero
        agentes_mezclados = random.sample(agentes, len(agentes))
        
        for agente in agentes_mezclados:
            otros = [a for a in agentes if a.id != agente.id]
            agente.decidir_y_actuar(otros)

        # Mostrar el entorno en pasos clave
        if (paso + 1) % 5 == 0 or len(entorno.comida) == 0:
            print(f"\nEstado en Paso {paso + 1}:")
            entorno.mostrar(agentes)
            for agente in agentes:
                print(f"Agente {agente.id}: {agente.comida_recolectada} comida | Objetivo: {agente.objetivo}")

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