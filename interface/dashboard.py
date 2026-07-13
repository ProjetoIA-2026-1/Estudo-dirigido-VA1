import pygame


class Dashboard:
    def __init__(self):
        # ---- CONFIGURAÇÕES VISUAIS ----
        self.LARGURA_CELULA = 25
        self.LARGURA_JOGO = 20 * self.LARGURA_CELULA  # 500px
        self.LARGURA_PAINEL = 320
        self.LARGURA_TELA = self.LARGURA_JOGO + self.LARGURA_PAINEL  # 820px
        self.ALTURA_TELA = 650

        # ---- CORES (Paleta Moderna) ----
        self.COR_FUNDO = (15, 18, 25)
        self.COR_PAINEL = (25, 30, 40)
        self.COR_CARD = (35, 42, 55)
        self.BRANCO = (240, 240, 245)
        self.CINZA_TEXTO = (170, 180, 190)
        self.VERDE_GRAMA = (40, 50, 45)
        self.MARROM_LAMA = (80, 55, 35)
        self.OURO_CHOCOLATE = (255, 190, 50)
        self.VERMELHO_MINA = (220, 50, 60)
        self.AZUL_OBJETIVO = (0, 180, 255)
        self.VERMELHO_FOGO = (255, 60, 0, 120)

        # ---- INICIALIZAÇÃO PYGAME ----
        pygame.init()
        self.tela = pygame.display.set_mode((self.LARGURA_TELA, self.ALTURA_TELA))
        pygame.display.set_caption("Treinamento Militar IA - V2.0")

        self.fonte_titulo = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.fonte_texto = pygame.font.SysFont("Segoe UI", 14, bold=True)
        self.fonte_grande = pygame.font.SysFont("Consolas", 26, bold=True)
        self.fonte_gigante = pygame.font.SysFont("Segoe UI", 32, bold=True)

    def _desenhar_icone_mina(self, x, y, tamanho):
        centro = (x + tamanho // 2, y + tamanho // 2)
        pygame.draw.circle(self.tela, (20, 20, 20), centro, tamanho // 2.5)
        pygame.draw.line(self.tela, self.VERMELHO_MINA, (x + 6, y + 6), (x + tamanho - 6, y + tamanho - 6), 3)
        pygame.draw.line(self.tela, self.VERMELHO_MINA, (x + tamanho - 6, y + 6), (x + 6, y + tamanho - 6), 3)

    def _desenhar_icone_chocolate(self, x, y, tamanho):
        pontos = [
            (x + tamanho // 2, y + 4),
            (x + tamanho - 4, y + tamanho // 2),
            (x + tamanho // 2, y + tamanho - 4),
            (x + 4, y + tamanho // 2)
        ]
        pygame.draw.polygon(self.tela, self.OURO_CHOCOLATE, pontos)

    def _desenhar_jogo(self, env, tempo):
        pygame.draw.rect(self.tela, self.COR_FUNDO, (0, 0, self.LARGURA_JOGO, self.ALTURA_TELA))

        agente_py_visual = (env.comprimento - 1 - env.posicao_y) * self.LARGURA_CELULA
        offset_y = agente_py_visual - (self.ALTURA_TELA * 0.70)
        offset_y = max(0, min(env.comprimento * self.LARGURA_CELULA - self.ALTURA_TELA, offset_y))

        for y in range(env.comprimento):
            for x in range(env.largura):
                px = x * self.LARGURA_CELULA
                py_visual_absoluto = (env.comprimento - 1 - y) * self.LARGURA_CELULA
                py = py_visual_absoluto - offset_y

                if py < -self.LARGURA_CELULA or py > self.ALTURA_TELA:
                    continue

                terreno = env.mapa[y][x]
                cor_base = self.MARROM_LAMA if terreno == env.LAMA else self.VERDE_GRAMA
                rect_celula = (px, py, self.LARGURA_CELULA, self.LARGURA_CELULA)

                pygame.draw.rect(self.tela, cor_base, rect_celula)
                pygame.draw.rect(self.tela, (25, 30, 35), rect_celula, 1)

                if terreno == env.MINA:
                    self._desenhar_icone_mina(px, py, self.LARGURA_CELULA)
                elif terreno == env.CHOCOLATE:
                    self._desenhar_icone_chocolate(px, py, self.LARGURA_CELULA)
                elif terreno == env.OBJETIVO:
                    centro = (px + self.LARGURA_CELULA // 2, py + self.LARGURA_CELULA // 2)
                    pulso = abs((tempo % 1000) - 500) / 500.0
                    pygame.draw.circle(self.tela, self.AZUL_OBJETIVO, centro, int(self.LARGURA_CELULA // 2.5))
                    pygame.draw.circle(self.tela, self.AZUL_OBJETIVO, centro, int(self.LARGURA_CELULA // 2 * pulso), 2)

                if y <= env.linha_tiros_y:
                    s_fogo = pygame.Surface((self.LARGURA_CELULA, self.LARGURA_CELULA), pygame.SRCALPHA)
                    s_fogo.fill(self.VERMELHO_FOGO)
                    self.tela.blit(s_fogo, (px, py))

                if abs(x - env.posicao_x) > 2 or abs(y - env.posicao_y) > 2:
                    s_fog = pygame.Surface((self.LARGURA_CELULA, self.LARGURA_CELULA), pygame.SRCALPHA)
                    s_fog.fill((10, 12, 15, 200))
                    self.tela.blit(s_fog, (px, py))

        agente_px = env.posicao_x * self.LARGURA_CELULA
        py_agente = (env.comprimento - 1 - env.posicao_y) * self.LARGURA_CELULA - offset_y
        centro = (agente_px + self.LARGURA_CELULA // 2, py_agente + self.LARGURA_CELULA // 2)

        cor_agente = self.OURO_CHOCOLATE if env.bonus_movimento else self.BRANCO
        pygame.draw.circle(self.tela, cor_agente, centro, self.LARGURA_CELULA // 2.5)
        pygame.draw.circle(self.tela, (20, 20, 20), centro, self.LARGURA_CELULA // 5)

    def _desenhar_card(self, x, y, largura, altura, titulo, valor, cor_valor):
        rect = pygame.Rect(x, y, largura, altura)
        pygame.draw.rect(self.tela, self.COR_CARD, rect, border_radius=10)

        img_titulo = self.fonte_texto.render(titulo, True, self.CINZA_TEXTO)
        self.tela.blit(img_titulo, (x + 15, y + 10))

        img_valor = self.fonte_grande.render(str(valor), True, cor_valor)
        self.tela.blit(img_valor, (x + 15, y + 35))

    def _desenhar_painel(self, env, pontuacao, acao_str, status):
        pygame.draw.rect(self.tela, self.COR_PAINEL, (self.LARGURA_JOGO, 0, self.LARGURA_PAINEL, self.ALTURA_TELA))
        pygame.draw.line(self.tela, self.COR_CARD, (self.LARGURA_JOGO, 0), (self.LARGURA_JOGO, self.ALTURA_TELA), 4)

        img_titulo = self.fonte_titulo.render("MONITORAMENTO IA", True, self.BRANCO)
        self.tela.blit(img_titulo, (self.LARGURA_JOGO + 20, 25))
        pygame.draw.line(self.tela, self.CINZA_TEXTO, (self.LARGURA_JOGO + 20, 60), (self.LARGURA_TELA - 20, 60), 1)

        margem = self.LARGURA_JOGO + 20
        larg_card = self.LARGURA_PAINEL - 40

        cor_status = self.VERDE_GRAMA if status == "Correndo" else (
            self.AZUL_OBJETIVO if "VITÓRIA" in status else self.VERMELHO_MINA)
        self._desenhar_card(margem, 80, larg_card, 70, "STATUS DA SIMULAÇÃO", status, cor_status)

        self._desenhar_card(margem, 165, larg_card, 70, "COORDENADA Y (AVANÇO)", f"{env.posicao_y} / 99", self.BRANCO)

        dist_tiros = env.posicao_y - env.linha_tiros_y
        cor_dist = self.VERMELHO_MINA if dist_tiros < 4 else self.BRANCO
        self._desenhar_card(margem, 250, larg_card, 70, "DISTÂNCIA PARA AMEAÇA", f"{dist_tiros} blocos", cor_dist)

        self._desenhar_card(margem, 335, larg_card, 70, "FITNESS (RECOMPENSA)", f"{pontuacao}", self.OURO_CHOCOLATE)

        self._desenhar_card(margem, 420, larg_card, 70, "AÇÃO EXECUTADA", acao_str, self.AZUL_OBJETIVO)

        img_dica = self.fonte_texto.render("Controles Manuais:", True, self.CINZA_TEXTO)
        self.tela.blit(img_dica, (margem, self.ALTURA_TELA - 90))
        img_teclas = self.fonte_texto.render("[Setas] Mover  |  [R] Resetar", True, self.BRANCO)
        self.tela.blit(img_teclas, (margem, self.ALTURA_TELA - 60))

    def _desenhar_overlay_fim_jogo(self, status):
        s_overlay = pygame.Surface((self.LARGURA_JOGO, self.ALTURA_TELA), pygame.SRCALPHA)
        s_overlay.fill((0, 0, 0, 180))
        self.tela.blit(s_overlay, (0, 0))

        cor = self.AZUL_OBJETIVO if "VITÓRIA" in status else self.VERMELHO_MINA
        texto = "OBJETIVO ALCANÇADO" if "VITÓRIA" in status else "AGENTE ABATIDO"

        img = self.fonte_gigante.render(texto, True, cor)
        rect = img.get_rect(center=(self.LARGURA_JOGO // 2, self.ALTURA_TELA // 2))

        pygame.draw.rect(self.tela, (20, 20, 25), rect.inflate(40, 40), border_radius=10)
        pygame.draw.rect(self.tela, cor, rect.inflate(40, 40), 2, border_radius=10)
        self.tela.blit(img, rect)

    def renderizar_frame(self, env, pontuacao, acao_str, status):
        tempo = pygame.time.get_ticks()

        self._desenhar_jogo(env, tempo)
        self._desenhar_painel(env, pontuacao, acao_str, status)

        if status != "Correndo":
            self._desenhar_overlay_fim_jogo(status)

        pygame.display.flip()