import heapq

class AgenteAStar:
    def __init__(self, ambiente):
        self.env = ambiente

    def heuristica(self, pos_atual, pos_objetivo):
        return abs(pos_atual[0] - pos_objetivo[0]) + abs(pos_atual[1] - pos_objetivo[1])

    def planejar_rota(self, mapa_customizado=None, modo="TATICO"):
        """
        Modos disponíveis:
        - "TATICO": Evita lama e busca chocolate (Custo variável). Usado para gameplay.
        - "VALIDADOR": Ignora terreno, busca apenas o caminho geométrico mais curto. Usado para gerar mapas.
        """
        if mapa_customizado is not None:
            mapa_alvo = mapa_customizado
        else:
            mapa_alvo = getattr(self.env, 'mapa', self.env.mapa_original)

        inicio_x = self.env.largura // 2
        inicio_y = 0

        objetivo_x = getattr(self.env, 'objetivo_x', self.env.largura // 2)
        objetivo_y = self.env.comprimento - 1

        fila = []
        contador = 0
        h_inicial = self.heuristica((inicio_x, inicio_y), (objetivo_x, objetivo_y))

        # (f, g, contador, x, y, caminho)
        heapq.heappush(fila, (h_inicial, 0, contador, inicio_x, inicio_y, []))

        visitados = {}

        while fila:
            f, g, _, x, y, caminho = heapq.heappop(fila)

            if mapa_alvo[y][x] == self.env.OBJETIVO:
                return caminho

            if (x, y) in visitados and visitados[(x, y)] <= g:
                continue
            visitados[(x, y)] = g

            acoes = [
                (0, x, y + 1),
                (1, x - 1, y),
                (2, x + 1, y),
                (3, x, y - 1)
            ]

            for acao, nx, ny in acoes:
                if 0 <= nx < self.env.largura and 0 <= ny < self.env.comprimento:
                    terreno = mapa_alvo[ny][nx]

                    if terreno == self.env.MINA:
                        continue

                    custo_passo = 1

                    # Aplica as personalidades do A*
                    if modo == "TATICO":
                        if terreno == self.env.LAMA:
                            custo_passo = 6  # Evitará a lama a todo custo
                        elif terreno == self.env.CHOCOLATE:
                            custo_passo = 0  # Custo zerado cria atração magnética

                    # O Modo VALIDADOR mantém o custo 1 para todos os blocos válidos

                    novo_g = g + custo_passo
                    novo_h = self.heuristica((nx, ny), (objetivo_x, objetivo_y))
                    novo_f = novo_g + novo_h

                    novo_caminho = caminho + [acao]
                    contador += 1
                    heapq.heappush(fila, (novo_f, novo_g, contador, nx, ny, novo_caminho))

        return []