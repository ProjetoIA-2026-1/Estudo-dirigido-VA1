import numpy as np
import random


class CampoBatalhaEnv:
    def __init__(self, largura=21, dificuldade="MEDIO", seed=None):
        self.largura = largura
        self.dificuldade = dificuldade.upper()

        self.VAZIO = 0
        self.LAMA = 1
        self.CHOCOLATE = 2
        self.MINA = 3
        self.OBJETIVO = 4

        if seed is None:
            self.seed_atual = random.randint(10000, 99999)
        else:
            self.seed_atual = seed

        random.seed(self.seed_atual)
        np.random.seed(self.seed_atual)

        self.configs = {
            "FACIL": {"comprimento": 60, "mina": 0.04, "lama": 0.10, "choco": 0.02, "tiros_y": -3, "caminhos": 2},
            "MEDIO": {"comprimento": 80, "mina": 0.06, "lama": 0.15, "choco": 0.03, "tiros_y": -6, "caminhos": 2},
            "DIFICIL": {"comprimento": 100, "mina": 0.10, "lama": 0.23, "choco": 0.04, "tiros_y": -10, "caminhos": 2}
        }

        if self.dificuldade not in self.configs:
            self.dificuldade = "MEDIO"

        self.cfg = self.configs[self.dificuldade]
        self.comprimento = self.cfg["comprimento"]

        self.objetivo_x = random.randint(2, self.largura - 3)

        self.mapa_original = self._orquestrar_geracao()
        self.mapa = np.copy(self.mapa_original)

        self.posicao_x = None
        self.posicao_y = None
        self.linha_tiros_y = None
        self.bonus_visual = False

    def _orquestrar_geracao(self):
        from agent_astar import AgenteAStar
        agente_juiz = AgenteAStar(self)

        tentativas_maximas = 5

        for tentativa in range(tentativas_maximas):
            mapa_teste = self._gerar_aleatorio()
            rota_primaria = agente_juiz.planejar_rota(mapa_customizado=mapa_teste)

            if rota_primaria:
                mapa_teste = self._alargar_rota(mapa_teste, rota_primaria)

                if self.dificuldade == "DIFICIL" and self.cfg["caminhos"] > 1:
                    mapa_bloqueado = np.copy(mapa_teste)
                    px, py = self.largura // 2, 0

                    for acao in rota_primaria:
                        if acao == 0:
                            py += 1
                        elif acao == 1:
                            px -= 1
                        elif acao == 2:
                            px += 1
                        elif acao == 3:
                            py -= 1

                        if py != self.comprimento - 1 and py % 8 == 0:
                            mapa_bloqueado[py][px] = self.MINA

                    rota_secundaria = agente_juiz.planejar_rota(mapa_customizado=mapa_bloqueado)
                    if not rota_secundaria:
                        continue

                return mapa_teste

        return self._gerar_golden_path()

    def _alargar_rota(self, mapa, rota):
        px, py = self.largura // 2, 0
        coordenadas_rota = [(py, px)]

        for acao in rota:
            if acao == 0:
                py += 1
            elif acao == 1:
                px -= 1
            elif acao == 2:
                px += 1
            elif acao == 3:
                py -= 1
            coordenadas_rota.append((py, px))

        for y, x in coordenadas_rota:
            for dx in [-1, 1]:
                nx = x + dx
                if 0 <= nx < self.largura:
                    if mapa[y][nx] == self.MINA:
                        mapa[y][nx] = self.LAMA if random.random() < 0.7 else self.VAZIO
        return mapa

    def _gerar_aleatorio(self):
        mapa = np.zeros((self.comprimento, self.largura), dtype=int)
        limite_mina = self.cfg["mina"]
        limite_lama = limite_mina + self.cfg["lama"]
        limite_choco = limite_lama + self.cfg["choco"]

        for y in range(4, self.comprimento - 4):
            for x in range(self.largura):
                chance = random.random()
                if chance < limite_mina:
                    mapa[y][x] = self.MINA
                elif chance < limite_lama:
                    mapa[y][x] = self.LAMA
                elif chance < limite_choco:
                    mapa[y][x] = self.CHOCOLATE

        num_clusters = int(
            self.comprimento * (0.05 if self.dificuldade == "FACIL" else 0.08 if self.dificuldade == "MEDIO" else 0.12))

        for _ in range(num_clusters):
            cy = random.randint(10, self.comprimento - 10)
            cx = random.randint(2, self.largura - 3)
            raio = random.randint(1, 3)
            tipo_cluster = self.MINA if random.random() < 0.5 else self.LAMA

            for dy in range(-raio, raio + 1):
                for dx in range(-raio, raio + 1):
                    if abs(dx) + abs(dy) <= raio:
                        ny, nx = cy + dy, cx + dx
                        if 4 <= ny < self.comprimento - 4 and 0 <= nx < self.largura:
                            mapa[ny][nx] = tipo_cluster

        # --- A NOVA ZONA DE RESGATE (3x2) ---
        for dy in range(1, 3):  # Ocupa as duas últimas linhas
            for dx in range(-1, 2):  # 3 blocos de largura
                nx = self.objetivo_x + dx
                if 0 <= nx < self.largura:
                    mapa[self.comprimento - dy][nx] = self.OBJETIVO

        return mapa

    def _gerar_golden_path(self):
        mapa = np.zeros((self.comprimento, self.largura), dtype=int)
        x_atual = self.largura // 2

        caminho_seguro = set()

        for y in range(self.comprimento):
            caminho_seguro.add((y, x_atual))

            if x_atual < self.objetivo_x and random.random() > 0.4:
                x_atual += 1
                caminho_seguro.add((y, x_atual))
            elif x_atual > self.objetivo_x and random.random() > 0.4:
                x_atual -= 1
                caminho_seguro.add((y, x_atual))
            elif random.random() < 0.2 and x_atual > 1:
                x_atual -= 1
                caminho_seguro.add((y, x_atual))
            elif random.random() > 0.8 and x_atual < self.largura - 2:
                x_atual += 1
                caminho_seguro.add((y, x_atual))

        limite_mina = self.cfg["mina"]
        limite_lama = limite_mina + self.cfg["lama"]
        limite_choco = limite_lama + self.cfg["choco"]

        for y in range(4, self.comprimento - 4):
            for x in range(self.largura):
                if (y, x) in caminho_seguro:
                    continue

                chance = random.random()
                if chance < limite_mina:
                    mapa[y][x] = self.MINA
                elif chance < limite_lama:
                    mapa[y][x] = self.LAMA
                elif chance < limite_choco:
                    mapa[y][x] = self.CHOCOLATE

        # --- A NOVA ZONA DE RESGATE (3x2) NO GOLDEN PATH ---
        for dy in range(1, 3):
            for dx in range(-1, 2):
                nx = self.objetivo_x + dx
                if 0 <= nx < self.largura:
                    mapa[self.comprimento - dy][nx] = self.OBJETIVO

        return mapa

    def reset(self):
        self.mapa = np.copy(self.mapa_original)
        self.posicao_x = self.largura // 2
        self.posicao_y = 0
        self.linha_tiros_y = self.cfg["tiros_y"]
        self.bonus_visual = False
        return self.get_visao_local()

    def get_visao_local(self, raio=2):
        visao = np.full((raio * 2 + 1, raio * 2 + 1), -1)
        for dy in range(-raio, raio + 1):
            for dx in range(-raio, raio + 1):
                mapa_y = self.posicao_y + dy
                mapa_x = self.posicao_x + dx
                if 0 <= mapa_y < self.comprimento and 0 <= mapa_x < self.largura:
                    visao[dy + raio][dx + raio] = self.mapa[mapa_y][mapa_x]
        return visao, self.posicao_y - self.linha_tiros_y

    def step(self, acao):
        novo_x = self.posicao_x
        novo_y = self.posicao_y
        self.bonus_visual = False

        if acao == 0:
            novo_y += 1
        elif acao == 1:
            novo_x -= 1
        elif acao == 2:
            novo_x += 1
        elif acao == 3:
            novo_y -= 1

        self.posicao_x = max(0, min(self.largura - 1, novo_x))
        self.posicao_y = max(0, min(self.comprimento - 1, novo_y))

        terreno = self.mapa[self.posicao_y][self.posicao_x]

        if terreno == self.LAMA:
            self.linha_tiros_y += 2
        elif terreno == self.CHOCOLATE:
            self.linha_tiros_y -= 1
        else:
            self.linha_tiros_y += 1

        done = False
        recompensa = -1

        if terreno == self.LAMA:
            recompensa = -3
        elif terreno == self.CHOCOLATE:
            recompensa = 5
            self.bonus_visual = True
            self.mapa[self.posicao_y][self.posicao_x] = self.VAZIO

        if terreno == self.MINA or self.posicao_y <= self.linha_tiros_y:
            recompensa = -100
            done = True
        elif terreno == self.OBJETIVO:
            recompensa = 100
            done = True

        return self.get_visao_local(), recompensa, done, {"pos_y": self.posicao_y, "pos_x": self.posicao_x}