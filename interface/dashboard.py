import pygame

class Dashboard:
    def __init__(self):
        # ---- CONFIGURAÇÕES VISUAIS ----
        self.LARGURA_CELULA = 35
        self.ALTURA_TELA = 720
        # As larguras agora começam zeradas e serão calculadas dinamicamente
        self.LARGURA_JOGO = 0
        self.LARGURA_PAINEL = 0

        # ---- CORES (Paleta Moderna) ----
        self.COR_FUNDO = (15, 18, 25)
        self.COR_PAINEL = (22, 26, 36)
        self.COR_CARD = (32, 38, 50)
        self.BRANCO = (240, 240, 245)
        self.CINZA_TEXTO = (170, 180, 190)
        self.VERDE_GRAMA = (40, 50, 45)
        self.MARROM_LAMA = (80, 55, 35)
        self.OURO_CHOCOLATE = (255, 190, 50)
        self.VERMELHO_MINA = (220, 50, 60)
        self.AZUL_OBJETIVO = (0, 180, 255)
        self.VERMELHO_FOGO = (255, 60, 0, 120)

        # Inicialização das Fontes
        pygame.font.init()
        self.fonte_titulo = pygame.font.SysFont("Segoe UI", 32, bold=True)
        self.fonte_texto = pygame.font.SysFont("Segoe UI", 16, bold=True)
        self.fonte_grande = pygame.font.SysFont("Consolas", 30, bold=True)
        self.fonte_gigante = pygame.font.SysFont("Segoe UI", 48, bold=True)

    def _desenhar_icone_mina(self, tela, x, y, tamanho):
        centro = (x + tamanho // 2, y + tamanho // 2)
        pygame.draw.circle(tela, (20, 20, 20), centro, tamanho // 2.5)
        pygame.draw.line(tela, self.VERMELHO_MINA, (x + 8, y + 8), (x + tamanho - 8, y + tamanho - 8), 3)
        pygame.draw.line(tela, self.VERMELHO_MINA, (x + tamanho - 8, y + 8), (x + 8, y + tamanho - 8), 3)

    def _desenhar_icone_chocolate(self, tela, x, y, tamanho):
        pontos = [
            (x + tamanho // 2, y + 6),
            (x + tamanho - 6, y + tamanho // 2),
            (x + tamanho // 2, y + tamanho - 6),
            (x + 6, y + tamanho // 2)
        ]
        pygame.draw.polygon(tela, self.OURO_CHOCOLATE, pontos)

    def _desenhar_jogo(self, tela, env, tempo):
        pygame.draw.rect(tela, self.COR_FUNDO, (0, 0, self.LARGURA_JOGO, self.ALTURA_TELA))

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

                pygame.draw.rect(tela, cor_base, rect_celula)
                pygame.draw.rect(tela, (25, 30, 35), rect_celula, 1)

                if terreno == env.MINA:
                    self._desenhar_icone_mina(tela, px, py, self.LARGURA_CELULA)
                elif terreno == env.CHOCOLATE:
                    self._desenhar_icone_chocolate(tela, px, py, self.LARGURA_CELULA)
                elif terreno == env.OBJETIVO:
                    centro = (px + self.LARGURA_CELULA // 2, py + self.LARGURA_CELULA // 2)
                    pulso = abs((tempo % 1000) - 500) / 500.0
                    pygame.draw.circle(tela, self.AZUL_OBJETIVO, centro, int(self.LARGURA_CELULA // 2.5))
                    pygame.draw.circle(tela, self.AZUL_OBJETIVO, centro, int(self.LARGURA_CELULA // 2 * pulso), 2)

                if y <= env.linha_tiros_y:
                    s_fogo = pygame.Surface((self.LARGURA_CELULA, self.LARGURA_CELULA), pygame.SRCALPHA)
                    s_fogo.fill(self.VERMELHO_FOGO)
                    tela.blit(s_fogo, (px, py))

                if abs(x - env.posicao_x) > 2 or abs(y - env.posicao_y) > 2:
                    s_fog = pygame.Surface((self.LARGURA_CELULA, self.LARGURA_CELULA), pygame.SRCALPHA)
                    s_fog.fill((10, 12, 15, 200))
                    tela.blit(s_fog, (px, py))

        agente_px = env.posicao_x * self.LARGURA_CELULA
        py_agente = (env.comprimento - 1 - env.posicao_y) * self.LARGURA_CELULA - offset_y
        centro = (agente_px + self.LARGURA_CELULA // 2, py_agente + self.LARGURA_CELULA // 2)

        # CORREÇÃO: Lendo a variável visual
        cor_agente = self.OURO_CHOCOLATE if env.bonus_visual else self.BRANCO
        pygame.draw.circle(tela, cor_agente, centro, self.LARGURA_CELULA // 2.5)
        pygame.draw.circle(tela, (20, 20, 20), centro, self.LARGURA_CELULA // 5)

    def _desenhar_card(self, tela, x, y, largura, altura, titulo, valor, cor_valor):
        rect = pygame.Rect(x, y, largura, altura)
        pygame.draw.rect(tela, self.COR_CARD, rect, border_radius=10)

        img_titulo = self.fonte_texto.render(titulo, True, self.CINZA_TEXTO)
        tela.blit(img_titulo, (x + 15, y + 15))

        img_valor = self.fonte_grande.render(str(valor), True, cor_valor)
        tela.blit(img_valor, (x + 15, y + 45))

    def _desenhar_painel(self, tela, env, pontuacao, acao_str, status):
        pygame.draw.rect(tela, self.COR_PAINEL, (self.LARGURA_JOGO, 0, self.LARGURA_PAINEL, self.ALTURA_TELA))
        pygame.draw.line(tela, self.COR_CARD, (self.LARGURA_JOGO, 0), (self.LARGURA_JOGO, self.ALTURA_TELA), 5)

        margem_x = self.LARGURA_JOGO + 30
        img_titulo = self.fonte_titulo.render("TELEMETRIA DA SIMULAÇÃO", True, self.BRANCO)
        tela.blit(img_titulo, (margem_x, 30))
        pygame.draw.line(tela, self.CINZA_TEXTO, (margem_x, 75), (tela.get_width() - 30, 75), 1)

        largura_total = self.LARGURA_PAINEL - 60
        largura_metade = (largura_total - 20) // 2

        cor_status = self.VERDE_GRAMA if status == "Correndo" else (
            self.AZUL_OBJETIVO if "VITÓRIA" in status else self.VERMELHO_MINA)
        self._desenhar_card(tela, margem_x, 100, largura_total, 90, "STATUS DO AGENTE", status, cor_status)

        # CORREÇÃO: Lê o limite real do mapa dinamicamente
        self._desenhar_card(tela, margem_x, 210, largura_metade, 90, "AVANÇO (EIXO Y)", f"{env.posicao_y} / {env.comprimento - 1}",
                            self.BRANCO)
        dist_tiros = env.posicao_y - env.linha_tiros_y
        cor_dist = self.VERMELHO_MINA if dist_tiros < 4 else self.BRANCO
        self._desenhar_card(tela, margem_x + largura_metade + 20, 210, largura_metade, 90, "DIST. AMEAÇA",
                            f"{dist_tiros} blocos", cor_dist)

        self._desenhar_card(tela, margem_x, 320, largura_metade, 90, "FITNESS (PONTOS)", f"{pontuacao}",
                            self.OURO_CHOCOLATE)
        self._desenhar_card(tela, margem_x + largura_metade + 20, 320, largura_metade, 90, "ÚLTIMA AÇÃO", acao_str,
                            self.AZUL_OBJETIVO)

        y_ia = 450
        pygame.draw.rect(tela, (25, 30, 42), (margem_x, y_ia, largura_total, 180), border_radius=10)
        pygame.draw.rect(tela, self.AZUL_OBJETIVO, (margem_x, y_ia, largura_total, 180), 2, border_radius=10)

        img_ia_titulo = self.fonte_texto.render("PARÂMETROS DE APRENDIZADO DA IA", True, self.AZUL_OBJETIVO)
        tela.blit(img_ia_titulo, (margem_x + 15, y_ia + 15))

        textos_ia = ["Geração Atual: ---", "Melhor Fitness Global: ---", "Taxa de Exploração (Epsilon): ---",
                     "Penalidades Sofridas: ---"]
        for i, texto in enumerate(textos_ia):
            img_texto = self.fonte_texto.render(texto, True, self.CINZA_TEXTO)
            tela.blit(img_texto, (margem_x + 15, y_ia + 55 + (i * 28)))

        img_dica = self.fonte_texto.render(
            "[Setas] Controle Manual    |    [R] Nova Simulação    |    [ESC] Voltar ao Menu", True, self.CINZA_TEXTO)
        tela.blit(img_dica, (margem_x, self.ALTURA_TELA - 40))

    def _desenhar_overlay_fim_jogo(self, tela, status, env):
        s_overlay = pygame.Surface((self.LARGURA_JOGO, self.ALTURA_TELA), pygame.SRCALPHA)
        s_overlay.fill((0, 0, 0, 180))
        tela.blit(s_overlay, (0, 0))

        cor = self.AZUL_OBJETIVO if "VITÓRIA" in status else self.VERMELHO_MINA
        texto = "OBJETIVO ALCANÇADO" if "VITÓRIA" in status else "AGENTE ABATIDO"

        img = self.fonte_gigante.render(texto, True, cor)
        rect = img.get_rect(center=(self.LARGURA_JOGO // 2, self.ALTURA_TELA // 2))

        pygame.draw.rect(tela, (20, 20, 25), rect.inflate(40, 40), border_radius=10)
        pygame.draw.rect(tela, cor, rect.inflate(40, 40), 2, border_radius=10)
        tela.blit(img, rect)

        # Aviso padrão (Tecla R)
        img_dica = self.fonte_texto.render("Pressione [ R ] para jogar novamente", True, self.BRANCO)
        rect_dica = img_dica.get_rect(center=(self.LARGURA_JOGO // 2, (self.ALTURA_TELA // 2) + 60))
        tela.blit(img_dica, rect_dica)

        # --- NOVIDADE: Aviso de Próximo Nível (Tecla N) ---
        if "VITÓRIA" in status and env.dificuldade in ["FACIL", "MEDIO"]:
            prox_nivel = "MÉDIO" if env.dificuldade == "FACIL" else "DIFÍCIL"
            img_next = self.fonte_texto.render(f"Pressione [ N ] para avançar ao nível {prox_nivel}", True,
                                               self.OURO_CHOCOLATE)
            rect_next = img_next.get_rect(center=(self.LARGURA_JOGO // 2, (self.ALTURA_TELA // 2) + 90))
            tela.blit(img_next, rect_next)

    def renderizar_frame(self, tela, env, pontuacao, acao_str, status):
        self.LARGURA_JOGO = env.largura * self.LARGURA_CELULA
        self.LARGURA_PAINEL = tela.get_width() - self.LARGURA_JOGO

        tempo = pygame.time.get_ticks()
        self._desenhar_jogo(tela, env, tempo)
        self._desenhar_painel(tela, env, pontuacao, acao_str, status)

        if status != "Correndo":
            # Passamos o 'env' agora para ele saber em qual dificuldade estamos
            self._desenhar_overlay_fim_jogo(tela, status, env)