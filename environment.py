import numpy as np
import random


class CampoBatalhaEnv:
    def __init__(self, largura=21, comprimento=100):
        self.largura = largura
        self.comprimento = comprimento

        # Definição dos códigos do terreno
        self.VAZIO = 0
        self.LAMA = 1
        self.CHOCOLATE = 2
        self.MINA = 3
        self.OBJETIVO = 4

        # Geração do mapa estático e backup do estado original
        self.mapa_original = self._gerar_mapa()
        self.mapa = np.copy(self.mapa_original)

        # Variáveis de estado do agente
        self.posicao_x = None
        self.posicao_y = None
        self.linha_tiros_y = None
        self.bonus_movimento = False  # Guarda o status do efeito do chocolate

    def _gerar_mapa(self):
        mapa = np.zeros((self.comprimento, self.largura), dtype=int)

        for y in range(5, self.comprimento - 5):
            for x in range(self.largura):
                chance = random.random()
                # 0.00 a 0.05 -> 5% de chance
                if chance < 0.05:
                    mapa[y][x] = self.MINA
                # 0.05 a 0.25 -> 20% de chance (0.05 + 0.20)
                elif chance < 0.25:
                    mapa[y][x] = self.LAMA
                # 0.25 a 0.27 -> 2% de chance (0.25 + 0.02)
                elif chance < 0.27:
                    mapa[y][x] = self.CHOCOLATE

        centro_x = self.largura // 2
        mapa[self.comprimento - 1][centro_x] = self.OBJETIVO

        return mapa

    def reset(self):
        # Restaura a matriz para garantir equidade entre episódios/gerações
        self.mapa = np.copy(self.mapa_original)
        self.posicao_x = self.largura // 2
        self.posicao_y = 0

        # Balanceamento: Distância da enxurrada travada em 7 blocos atrás do agente
        self.linha_tiros_y = -8
        self.bonus_movimento = False  # Reseta o bônus de velocidade

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

        # Define se o agente vai andar 1 casa ou dar um "salto" de 2 casas pelo chocolate
        passos = 2 if self.bonus_movimento else 1
        self.bonus_movimento = False  # Consome o bônus imediatamente neste turno

        # Mapeamento do espaço de ações aplicando os passos
        if acao == 0:
            novo_y += passos  # Frente
        elif acao == 1:
            novo_x -= passos  # Esquerda
        elif acao == 2:
            novo_x += passos  # Direita
        elif acao == 3:
            novo_y -= passos  # Trás (Recuar)

        # Restringe o agente para não sair do mapa por nenhum dos 4 lados
        self.posicao_x = max(0, min(self.largura - 1, novo_x))
        self.posicao_y = max(0, min(self.comprimento - 1, novo_y))

        terreno = self.mapa[self.posicao_y][self.posicao_x]

        # Balanceamento: Lama agora acelera a enxurrada em apenas 2 turnos (em vez de 3)
        self.linha_tiros_y += 2 if terreno == self.LAMA else 1

        done = False
        recompensa = -1

        # Avalia recompensas e mecânicas do terreno atual
        if terreno == self.LAMA:
            recompensa = -3
        elif terreno == self.CHOCOLATE:
            recompensa = 5
            self.bonus_movimento = True  # Ativa o boost de velocidade para o PRÓXIMO turno
            self.mapa[self.posicao_y][self.posicao_x] = self.VAZIO

        # Avalia condições de Fim de Jogo (Game Over ou Vitória)
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