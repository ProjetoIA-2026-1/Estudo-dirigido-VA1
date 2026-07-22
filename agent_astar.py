import heapq


class AgenteAStar:
    def __init__(self, ambiente):
        self.env = ambiente

    def heuristica(self, pos_atual, pos_objetivo):
        # Distância de Manhattan
        return abs(pos_atual[0] - pos_objetivo[0]) + abs(pos_atual[1] - pos_objetivo[1])

    def planejar_rota(self, mapa_customizado=None):
        if mapa_customizado is not None:
            mapa_alvo = mapa_customizado
        else:
            mapa_alvo = getattr(self.env, 'mapa', self.env.mapa_original)

        inicio_x = self.env.largura // 2
        inicio_y = 0

        # A heurística ainda usa o centro do objetivo dinâmico como guia
        objetivo_x = getattr(self.env, 'objetivo_x', self.env.largura // 2)
        objetivo_y = self.env.comprimento - 1

        linha_tiros_inicial = self.env.cfg["tiros_y"]

        fila = []
        contador = 0
        h_inicial = self.heuristica((inicio_x, inicio_y), (objetivo_x, objetivo_y))

        heapq.heappush(fila, (h_inicial, 0, contador, inicio_x, inicio_y, linha_tiros_inicial, []))

        visitados = {}

        while fila:
            f, g, _, x, y, linha_tiros, caminho = heapq.heappop(fila)

            if y <= linha_tiros:
                continue

            # --- CORREÇÃO DE OURO: Condição de Vitória Flexível ---
            # Se pisar em qualquer bloco da Zona de Resgate (Heliponto), venceu!
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

                    nova_linha_tiros = linha_tiros
                    custo_passo = 1

                    if terreno == self.env.LAMA:
                        nova_linha_tiros += 2
                        custo_passo = 2
                    elif terreno == self.env.CHOCOLATE:
                        nova_linha_tiros -= 1
                        custo_passo = 0
                    else:
                        nova_linha_tiros += 1
                        custo_passo = 1

                    if ny <= nova_linha_tiros:
                        continue

                    novo_g = g + custo_passo
                    novo_h = self.heuristica((nx, ny), (objetivo_x, objetivo_y))
                    novo_f = novo_g + novo_h

                    novo_caminho = caminho + [acao]
                    contador += 1
                    heapq.heappush(fila, (novo_f, novo_g, contador, nx, ny, nova_linha_tiros, novo_caminho))

        return []