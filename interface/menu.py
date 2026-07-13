import pygame


class MenuPrincipal:
    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura

        # Paleta de Cores do Menu
        self.COR_FUNDO = (15, 18, 25)
        self.BRANCO = (240, 240, 245)
        self.CINZA = (100, 110, 120)
        self.AZUL_DESTAQUE = (0, 180, 255)

        self.fonte_titulo = pygame.font.SysFont("Segoe UI", 48, bold=True)
        self.fonte_botoes = pygame.font.SysFont("Segoe UI", 24, bold=True)

        # Definição dos Botões (Texto, Retângulo)
        largura_botao = 300
        altura_botao = 60
        centro_x = (self.largura // 2) - (largura_botao // 2)

        self.botoes = {
            "JOGAR_MANUAL": pygame.Rect(centro_x, 300, largura_botao, altura_botao),
            "TREINAMENTO_IA": pygame.Rect(centro_x, 390, largura_botao, altura_botao),
            "SAIR": pygame.Rect(centro_x, 480, largura_botao, altura_botao)
        }

    def processar_eventos(self, eventos):
        """Verifica se algum botão foi clicado e retorna o novo estado."""
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Clique com botão esquerdo
                    pos_mouse = pygame.mouse.get_pos()

                    if self.botoes["JOGAR_MANUAL"].collidepoint(pos_mouse):
                        return "ESTADO_JOGAR"
                    elif self.botoes["TREINAMENTO_IA"].collidepoint(pos_mouse):
                        return "ESTADO_AGENTES"
                    elif self.botoes["SAIR"].collidepoint(pos_mouse):
                        return "SAIR"

        return "ESTADO_MENU"  # Mantém no menu se nada for clicado

    def desenhar(self, tela):
        tela.fill(self.COR_FUNDO)

        # Título do Jogo
        texto_titulo = self.fonte_titulo.render("RESGATE TÁTICO: IA", True, self.BRANCO)
        rect_titulo = texto_titulo.get_rect(center=(self.largura // 2, 150))
        tela.blit(texto_titulo, rect_titulo)

        # Subtítulo
        texto_sub = self.fonte_botoes.render("Selecione o Modo de Simulação", True, self.CINZA)
        rect_sub = texto_sub.get_rect(center=(self.largura // 2, 200))
        tela.blit(texto_sub, rect_sub)

        # Desenhar Botões
        pos_mouse = pygame.mouse.get_pos()

        textos = ["Simulação Manual", "Painel de Agentes (IA)", "Sair"]
        chaves = ["JOGAR_MANUAL", "TREINAMENTO_IA", "SAIR"]

        for i, chave in enumerate(chaves):
            rect = self.botoes[chave]

            # Efeito de Hover (Muda de cor se o mouse passar por cima)
            if rect.collidepoint(pos_mouse):
                pygame.draw.rect(tela, self.AZUL_DESTAQUE, rect, border_radius=8)
                cor_texto = self.COR_FUNDO
            else:
                pygame.draw.rect(tela, (35, 42, 55), rect, border_radius=8)
                pygame.draw.rect(tela, self.CINZA, rect, 2, border_radius=8)  # Borda
                cor_texto = self.BRANCO

            texto_btn = self.fonte_botoes.render(textos[i], True, cor_texto)
            rect_texto = texto_btn.get_rect(center=rect.center)
            tela.blit(texto_btn, rect_texto)