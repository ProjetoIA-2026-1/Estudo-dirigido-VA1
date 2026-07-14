import pygame


class MenuPrincipal:
    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura

        self.COR_FUNDO = (15, 18, 25)
        self.BRANCO = (240, 240, 245)
        self.CINZA = (100, 110, 120)
        self.AZUL_DESTAQUE = (0, 180, 255)
        self.VERDE_FACIL = (40, 180, 80)
        self.VERMELHO_DIFICIL = (220, 50, 60)

        self.fonte_titulo = pygame.font.SysFont("Segoe UI", 48, bold=True)
        self.fonte_botoes = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.fonte_sub = pygame.font.SysFont("Segoe UI", 16)

        largura_botao = 300
        altura_botao = 60
        centro_x = (self.largura // 2) - (largura_botao // 2)

        # Botões do Menu Principal
        self.botoes_main = {
            "JOGAR_MANUAL": pygame.Rect(centro_x, 300, largura_botao, altura_botao),
            "TREINAMENTO_IA": pygame.Rect(centro_x, 390, largura_botao, altura_botao),
            "SAIR": pygame.Rect(centro_x, 480, largura_botao, altura_botao)
        }

        # Botões da Tela de Dificuldade
        self.botoes_dificuldade = {
            "FACIL": pygame.Rect(centro_x, 280, largura_botao, altura_botao),
            "MEDIO": pygame.Rect(centro_x, 370, largura_botao, altura_botao),
            "DIFICIL": pygame.Rect(centro_x, 460, largura_botao, altura_botao),
            "VOLTAR": pygame.Rect(centro_x, 570, largura_botao, altura_botao)
        }

    # ==========================================
    # LÓGICA DO MENU PRINCIPAL
    # ==========================================
    def processar_eventos(self, eventos):
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                pos_mouse = pygame.mouse.get_pos()
                if self.botoes_main["JOGAR_MANUAL"].collidepoint(pos_mouse):
                    return "SELECIONAR_DIF_MANUAL"
                elif self.botoes_main["TREINAMENTO_IA"].collidepoint(pos_mouse):
                    return "SELECIONAR_DIF_IA"
                elif self.botoes_main["SAIR"].collidepoint(pos_mouse):
                    return "SAIR"
        return "ESTADO_MENU"

    def desenhar(self, tela):
        tela.fill(self.COR_FUNDO)
        texto_titulo = self.fonte_titulo.render("RESGATE TÁTICO: IA", True, self.BRANCO)
        tela.blit(texto_titulo, texto_titulo.get_rect(center=(self.largura // 2, 150)))

        texto_sub = self.fonte_botoes.render("Selecione o Modo de Simulação", True, self.CINZA)
        tela.blit(texto_sub, texto_sub.get_rect(center=(self.largura // 2, 200)))

        textos = ["Simulação Manual", "Painel de Agentes (IA)", "Sair"]
        chaves = ["JOGAR_MANUAL", "TREINAMENTO_IA", "SAIR"]
        self._desenhar_botoes(tela, self.botoes_main, chaves, textos)

    # ==========================================
    # LÓGICA DA TELA DE DIFICULDADE
    # ==========================================
    def processar_eventos_dificuldade(self, eventos):
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                pos_mouse = pygame.mouse.get_pos()
                if self.botoes_dificuldade["FACIL"].collidepoint(pos_mouse):
                    return "FACIL"
                elif self.botoes_dificuldade["MEDIO"].collidepoint(pos_mouse):
                    return "MEDIO"
                elif self.botoes_dificuldade["DIFICIL"].collidepoint(pos_mouse):
                    return "DIFICIL"
                elif self.botoes_dificuldade["VOLTAR"].collidepoint(pos_mouse):
                    return "VOLTAR"
        return "AGUARDANDO"

    def desenhar_dificuldade(self, tela, modo_origem):
        tela.fill(self.COR_FUNDO)

        titulo_texto = "SIMULAÇÃO MANUAL" if modo_origem == "MANUAL" else "TREINAMENTO DE IA"
        img_titulo = self.fonte_titulo.render(titulo_texto, True, self.BRANCO)
        tela.blit(img_titulo, img_titulo.get_rect(center=(self.largura // 2, 120)))

        img_sub = self.fonte_botoes.render("Selecione o Nível de Dificuldade da Pista", True, self.AZUL_DESTAQUE)
        tela.blit(img_sub, img_sub.get_rect(center=(self.largura // 2, 170)))

        # Dicas técnicas para o usuário
        dicas = [
            "(FÁCIL) 60 Blocos",
            "(MÉDIO) 80 Blocos",
            "(DIFÍCIL) 100 Blocos"
        ]

        for i, dica in enumerate(dicas):
            img_dica = self.fonte_sub.render(dica, True, self.CINZA)
            tela.blit(img_dica, img_dica.get_rect(center=(self.largura // 2, 220 + (i * 25))))

        textos = ["Modo Fácil", "Modo Médio", "Modo Difícil", "<- Voltar ao Menu"]
        chaves = ["FACIL", "MEDIO", "DIFICIL", "VOLTAR"]
        self._desenhar_botoes(tela, self.botoes_dificuldade, chaves, textos)

    # Função Auxiliar de Renderização
    def _desenhar_botoes(self, tela, dic_botoes, chaves, textos):
        pos_mouse = pygame.mouse.get_pos()
        for i, chave in enumerate(chaves):
            rect = dic_botoes[chave]

            if rect.collidepoint(pos_mouse):
                pygame.draw.rect(tela, self.AZUL_DESTAQUE, rect, border_radius=8)
                cor_texto = self.COR_FUNDO
            else:
                pygame.draw.rect(tela, (35, 42, 55), rect, border_radius=8)
                pygame.draw.rect(tela, self.CINZA, rect, 2, border_radius=8)
                cor_texto = self.BRANCO

            texto_btn = self.fonte_botoes.render(textos[i], True, cor_texto)
            tela.blit(texto_btn, texto_btn.get_rect(center=rect.center))