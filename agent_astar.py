import heapq


class AgenteAStar:
    def __init__(self, ambiente):
        # Recebe o ambiente para poder "espiar" o self.env.mapa_original
        self.env = ambiente

    def heuristica(self, pos_atual, pos_objetivo):
        """
        Calcula a Distância de Manhattan.
        Garante que a IA sempre expanda primeiro os caminhos que vão para frente.
        """
        return abs(pos_atual[0] - pos_objetivo[0]) + abs(pos_atual[1] - pos_objetivo[1])

    def planejar_rota(self):
        # Coordenadas Iniciais e Finais baseadas no tamanho dinâmico da pista
        inicio_x = self.env.largura // 2
        inicio_y = 0
        objetivo_x = self.env.largura // 2
        objetivo_y = self.env.comprimento - 1

        # Pega a distância original da ameaça
        linha_tiros_inicial = self.env.cfg["tiros_y"]

        # Fila de prioridade armazenará tuplas:
        # (f_score, g_score, contador_desempate, x, y, linha_tiros_y, caminho_de_acoes)
        fila = []
        contador = 0  # Evita erro no heapq se houver empate nos scores

        h_inicial = self.heuristica((inicio_x, inicio_y), (objetivo_x, objetivo_y))
        heapq.heappush(fila, (h_inicial, 0, contador, inicio_x, inicio_y, linha_tiros_inicial, []))

        # Dicionário para evitar loops infinitos (Chave: (x, y) -> Valor: menor_g)
        visitados = {}

        while fila:
            f, g, _, x, y, linha_tiros, caminho = heapq.heappop(fila)

            # Condição de Morte Mental (Se o fogo me alcançou nessa simulação, descarta a rota)
            if y <= linha_tiros:
                continue

            # Condição de Vitória Mental (Chegou no objetivo)
            if y == objetivo_y and x == objetivo_x:
                return caminho

            # Se já estivemos nessa casa com um custo de tempo menor, não compensa reexplorar
            if (x, y) in visitados and visitados[(x, y)] <= g:
                continue
            visitados[(x, y)] = g

            # Mapeamento de Movimentos: Frente(0), Esquerda(1), Direita(2), Trás(3)
            acoes = [
                (0, x, y + 1),
                (1, x - 1, y),
                (2, x + 1, y),
                (3, x, y - 1)
            ]

            for acao, nx, ny in acoes:
                # Verifica se o próximo passo está dentro dos limites do mapa
                if 0 <= nx < self.env.largura and 0 <= ny < self.env.comprimento:
                    terreno = self.env.mapa_original[ny][nx]

                    # A IA nunca pisa em minas
                    if terreno == self.env.MINA:
                        continue

                    # --- SIMULAÇÃO DA FÍSICA DO AMBIENTE ---
                    nova_linha_tiros = linha_tiros
                    custo_passo = 1

                    if terreno == self.env.LAMA:
                        nova_linha_tiros += 2  # O fogo acelera
                        custo_passo = 2  # Punição no custo matemático
                    elif terreno == self.env.CHOCOLATE:
                        nova_linha_tiros -= 1  # O fogo recua
                        custo_passo = 0  # Bonificação (passo de tempo "grátis")
                    else:
                        nova_linha_tiros += 1  # Fogo avança normalmente
                        custo_passo = 1

                    # Poda da Árvore: Se ao dar o passo o fogo me engole, ignora essa ramificação
                    if ny <= nova_linha_tiros:
                        continue

                    # Cálculos do A* para o próximo nó
                    novo_g = g + custo_passo
                    novo_h = self.heuristica((nx, ny), (objetivo_x, objetivo_y))
                    novo_f = novo_g + novo_h

                    # Salva a lista de ações que levou até aqui
                    novo_caminho = caminho + [acao]

                    contador += 1
                    heapq.heappush(fila, (novo_f, novo_g, contador, nx, ny, nova_linha_tiros, novo_caminho))

        # Se esgotar todas as possibilidades e não achar saída (não deve acontecer com o Caminho Dourado)
        return []