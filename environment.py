import numpy as np
import random


class CampoBatalhaEnv:
    def __init__(self, largura=21, dificuldade="MEDIO"):
        self.largura = largura
        self.dificuldade = dificuldade.upper()

        # Definição dos códigos do terreno
        self.VAZIO = 0
        self.LAMA = 1
        self.CHOCOLATE = 2
        self.MINA = 3
        self.OBJETIVO = 4

        # ---- CONFIGURAÇÕES DE DIFICULDADE (ALTURAS DINÂMICAS) ----
        self.configs = {
            # Fácil: Pista curta, pouca bomba, muito fôlego, 2 caminhos garantidos
            "FACIL": {"comprimento": 60, "mina": 0.02, "lama": 0.10, "choco": 0.05, "tiros_y": -12, "caminhos": 2},
            # Médio: Pista normal, balanceado, 2 caminhos garantidos
            "MEDIO": {"comprimento": 80, "mina": 0.05, "lama": 0.20, "choco": 0.03, "tiros_y": -8, "caminhos": 2},
            # Difícil: Pista longa, funil de bombas, fôlego curto, apenas 1 caminho garantido
            "DIFICIL": {"comprimento": 100, "mina": 0.10, "lama": 0.28, "choco": 0.02, "tiros_y": -5, "caminhos": 1}
        }

        # Fallback de segurança
        if self.dificuldade not in self.configs:
            self.dificuldade = "MEDIO"

        self.cfg = self.configs[self.dificuldade]
        self.comprimento = self.cfg["comprimento"]

        # Geração do mapa estático com garantia matemática
        self.mapa_original = self._gerar_mapa()
        self.mapa = np.copy(self.mapa_original)

        # Variáveis de estado
        self.posicao_x = None
        self.posicao_y = None
        self.linha_tiros_y = None

        # Mantemos a variável apenas para a interface visual piscar o boneco em dourado
        self.bonus_visual = False

    def _gerar_caminho_dourado(self):
        """Tratores invisíveis que abrem rotas seguras até o objetivo."""
        caminhos_seguros = set()
        qtd_caminhos = self.cfg["caminhos"]

        for _ in range(qtd_caminhos):
            # O trator nasce no centro
            x_atual = self.largura // 2

            for y_atual in range(self.comprimento):
                caminhos_seguros.add((y_atual, x_atual))

                # O trator decide se desvia para os lados ou desce reto
                chance_mov = random.random()
                if chance_mov < 0.30 and x_atual > 0:
                    x_atual -= 1  # Vai pra esquerda
                elif chance_mov > 0.70 and x_atual < self.largura - 1:
                    x_atual += 1  # Vai pra direita

                # Marca o bloco desviado como seguro também
                caminhos_seguros.add((y_atual, x_atual))

        return caminhos_seguros

    def _gerar_mapa(self):
        mapa = np.zeros((self.comprimento, self.largura), dtype=int)

        # 1. Traça a Rota de Fuga Inviolável
        caminhos_seguros = self._gerar_caminho_dourado()

        limite_mina = self.cfg["mina"]
        limite_lama = limite_mina + self.cfg["lama"]
        limite_choco = limite_lama + self.cfg["choco"]

        # 2. Preenche o mapa aleatoriamente, mas respeitando o Caminho Dourado
        for y in range(5, self.comprimento - 5):
            for x in range(self.largura):
                # Blindagem Matemática: Se for o Caminho Dourado, fica VAZIO
                if (y, x) in caminhos_seguros:
                    continue

                chance = random.random()
                if chance < limite_mina:
                    mapa[y][x] = self.MINA
                elif chance < limite_lama:
                    mapa[y][x] = self.LAMA
                elif chance < limite_choco:
                    mapa[y][x] = self.CHOCOLATE

        centro_x = self.largura // 2
        mapa[self.comprimento - 1][centro_x] = self.OBJETIVO

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

        distancia_tiros = self.posicao_y - self.linha_tiros_y

        return visao, distancia_tiros

    def step(self, acao):
        novo_x = self.posicao_x
        novo_y = self.posicao_y
        self.bonus_visual = False  # Reseta o efeito visual

        # Movimento agora é sempre de 1 casa (Simplicidade e estabilidade)
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

        # --- NOVA MECÂNICA SIMÉTRICA DO AMBIENTE ---
        if terreno == self.LAMA:
            self.linha_tiros_y += 2  # Punição: Fogo acelera (+2 casas)
        elif terreno == self.CHOCOLATE:
            self.linha_tiros_y -= 1  # Recompensa Real: Fogo recua (-1 casa)
        else:
            self.linha_tiros_y += 1  # Padrão: Fogo avança normalmente (+1 casa)
        # -------------------------------------------

        done = False
        recompensa = -1

        if terreno == self.LAMA:
            recompensa = -3
        elif terreno == self.CHOCOLATE:
            recompensa = 5
            self.bonus_visual = True  # Apenas para o Dashboard acender a borda
            self.mapa[self.posicao_y][self.posicao_x] = self.VAZIO

        if terreno == self.MINA:
            recompensa = -100
            done = True
        elif self.posicao_y <= self.linha_tiros_y:
            recompensa = -100
            done = True
        elif terreno == self.OBJETIVO:
            recompensa = 100
            done = True

        return self.get_visao_local(), recompensa, done, {"pos_y": self.posicao_y, "pos_x": self.posicao_x}