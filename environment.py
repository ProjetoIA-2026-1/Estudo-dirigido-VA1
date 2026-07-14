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

        # Se nenhuma semente for fornecida, gera uma nova e a salva
        if seed is None:
            self.seed_atual = random.randint(10000, 99999)
        else:
            self.seed_atual = seed

        random.seed(self.seed_atual)
        np.random.seed(self.seed_atual)

        self.configs = {
            "FACIL": {"comprimento": 60, "mina": 0.02, "lama": 0.10, "choco": 0.01, "tiros_y": -3, "caminhos": 2},
            "MEDIO": {"comprimento": 80, "mina": 0.05, "lama": 0.20, "choco": 0.03, "tiros_y": -8, "caminhos": 2},
            "DIFICIL": {"comprimento": 100, "mina": 0.10, "lama": 0.28, "choco": 0.06, "tiros_y": -12, "caminhos": 1}
        }

        if self.dificuldade not in self.configs:
            self.dificuldade = "MEDIO"

        self.cfg = self.configs[self.dificuldade]
        self.comprimento = self.cfg["comprimento"]

        self.mapa_original = self._orquestrar_geracao()
        self.mapa = np.copy(self.mapa_original)

        self.posicao_x = None
        self.posicao_y = None
        self.linha_tiros_y = None
        self.bonus_visual = False

    def _orquestrar_geracao(self):
        from agent_astar import AgenteAStar
        agente_juiz = AgenteAStar(self)

        tentativas_maximas = 3

        for tentativa in range(tentativas_maximas):
            mapa_teste = self._gerar_aleatorio()
            rota_primaria = agente_juiz.planejar_rota(mapa_customizado=mapa_teste)

            if not rota_primaria: continue

            if self.dificuldade == "DIFICIL":
                return mapa_teste

            mapa_bloqueado = np.copy(mapa_teste)
            px, py = self.largura // 2, 0

            for acao in rota_primaria:
                if acao == 0: py += 1
                elif acao == 1: px -= 1
                elif acao == 2: px += 1
                elif acao == 3: py -= 1

                if py != self.comprimento - 1:
                    mapa_bloqueado[py][px] = self.MINA

            rota_secundaria = agente_juiz.planejar_rota(mapa_customizado=mapa_bloqueado)

            if rota_secundaria:
                return mapa_teste

        return self._gerar_golden_path()

    def _gerar_aleatorio(self):
        mapa = np.zeros((self.comprimento, self.largura), dtype=int)
        limite_mina = self.cfg["mina"]
        limite_lama = limite_mina + self.cfg["lama"]
        limite_choco = limite_lama + self.cfg["choco"]

        for y in range(5, self.comprimento - 5):
            for x in range(self.largura):
                chance = random.random()
                if chance < limite_mina: mapa[y][x] = self.MINA
                elif chance < limite_lama: mapa[y][x] = self.LAMA
                elif chance < limite_choco: mapa[y][x] = self.CHOCOLATE

        mapa[self.comprimento - 1][self.largura // 2] = self.OBJETIVO
        return mapa

    def _gerar_golden_path(self):
        mapa = np.zeros((self.comprimento, self.largura), dtype=int)
        caminhos_seguros = set()
        chocolates_salvadores = set()

        for _ in range(self.cfg["caminhos"]):
            x_atual = self.largura // 2
            linha_tiros_simulada = self.cfg["tiros_y"]

            for y_atual in range(self.comprimento):
                caminhos_seguros.add((y_atual, x_atual))
                linha_tiros_simulada += 1

                if linha_tiros_simulada >= y_atual - 2:
                    chocolates_salvadores.add((y_atual, x_atual))
                    linha_tiros_simulada -= 1

                chance_mov = random.random()
                fez_curva = False

                if chance_mov < 0.15 and x_atual > 0:
                    x_atual -= 1
                    fez_curva = True
                elif chance_mov > 0.85 and x_atual < self.largura - 1:
                    x_atual += 1
                    fez_curva = True

                if fez_curva:
                    caminhos_seguros.add((y_atual, x_atual))
                    linha_tiros_simulada += 1
                    if linha_tiros_simulada >= y_atual - 2:
                        chocolates_salvadores.add((y_atual, x_atual))
                        linha_tiros_simulada -= 1

        limite_mina = self.cfg["mina"]
        limite_lama = limite_mina + self.cfg["lama"]
        limite_choco = limite_lama + self.cfg["choco"]

        for y in range(5, self.comprimento - 5):
            for x in range(self.largura):
                if (y, x) in chocolates_salvadores:
                    mapa[y][x] = self.CHOCOLATE
                    continue
                if (y, x) in caminhos_seguros:
                    if random.random() < self.cfg["choco"]: mapa[y][x] = self.CHOCOLATE
                    continue

                chance = random.random()
                if chance < limite_mina: mapa[y][x] = self.MINA
                elif chance < limite_lama: mapa[y][x] = self.LAMA
                elif chance < limite_choco: mapa[y][x] = self.CHOCOLATE

        mapa[self.comprimento - 1][self.largura // 2] = self.OBJETIVO
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

        if acao == 0: novo_y += 1
        elif acao == 1: novo_x -= 1
        elif acao == 2: novo_x += 1
        elif acao == 3: novo_y -= 1

        self.posicao_x = max(0, min(self.largura - 1, novo_x))
        self.posicao_y = max(0, min(self.comprimento - 1, novo_y))

        terreno = self.mapa[self.posicao_y][self.posicao_x]

        if terreno == self.LAMA: self.linha_tiros_y += 2
        elif terreno == self.CHOCOLATE: self.linha_tiros_y -= 1
        else: self.linha_tiros_y += 1

        done = False
        recompensa = -1

        if terreno == self.LAMA: recompensa = -3
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