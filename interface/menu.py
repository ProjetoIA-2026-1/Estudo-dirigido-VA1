import pygame


class MenuPrincipal:
    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura

        self.COR_FUNDO = (15, 18, 25)
        self.BRANCO = (240, 240, 245)
        self.CINZA = (100, 110, 120)
        self.AZUL_DESTAQUE = (0, 180, 255)
        self.OURO = (255, 190, 50)
        self.VERDE = (40, 200, 80)

        self.fonte_titulo = pygame.font.SysFont("Segoe UI", 48, bold=True)
        self.fonte_botoes = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.fonte_sub = pygame.font.SysFont("Segoe UI", 16)

        largura_botao = 300
        altura_botao = 60
        centro_x = (self.largura // 2) - (largura_botao // 2)

        self.botoes_main = {
            "JOGAR_MANUAL": pygame.Rect(centro_x, 300, largura_botao, altura_botao),
            "TREINAMENTO_IA": pygame.Rect(centro_x, 390, largura_botao, altura_botao),
            "SAIR": pygame.Rect(centro_x, 480, largura_botao, altura_botao)
        }

        self.botoes_agentes = {
            "ASTAR": pygame.Rect(centro_x, 280, largura_botao, altura_botao),
            "GENETICO": pygame.Rect(centro_x, 370, largura_botao, altura_botao),
            "QLEARNING": pygame.Rect(centro_x, 460, largura_botao, altura_botao),
            "VOLTAR": pygame.Rect(centro_x, 570, largura_botao, altura_botao)
        }

        self.botoes_dificuldade = {
            "FACIL": pygame.Rect(centro_x, 280, largura_botao, altura_botao),
            "MEDIO": pygame.Rect(centro_x, 370, largura_botao, altura_botao),
            "DIFICIL": pygame.Rect(centro_x, 460, largura_botao, altura_botao),
            "VOLTAR": pygame.Rect(centro_x, 570, largura_botao, altura_botao)
        }

        self.botao_wip_voltar = pygame.Rect(centro_x, 500, largura_botao, altura_botao)

        # Variáveis dinâmicas para a Galeria
        self.botoes_galeria = []
        self.dados_galeria = []

    def processar_eventos(self, eventos):
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                pos_mouse = pygame.mouse.get_pos()
                if self.botoes_main["JOGAR_MANUAL"].collidepoint(pos_mouse):
                    return "SELECIONAR_DIF_MANUAL"
                elif self.botoes_main["TREINAMENTO_IA"].collidepoint(pos_mouse):
                    return "ESTADO_SELECIONAR_AGENTE"
                elif self.botoes_main["SAIR"].collidepoint(pos_mouse):
                    return "SAIR"
        return "ESTADO_MENU"

    def desenhar(self, tela):
        tela.fill(self.COR_FUNDO)
        texto_titulo = self.fonte_titulo.render("RESGATE TÁTICO: IA", True, self.BRANCO)
        tela.blit(texto_titulo, texto_titulo.get_rect(center=(self.largura // 2, 150)))
        texto_sub = self.fonte_botoes.render("Selecione o Modo de Simulação", True, self.CINZA)
        tela.blit(texto_sub, texto_sub.get_rect(center=(self.largura // 2, 200)))
        self._desenhar_botoes(tela, self.botoes_main, ["JOGAR_MANUAL", "TREINAMENTO_IA", "SAIR"],
                              ["Simulação Manual", "Painel de Agentes (IA)", "Sair"])

    def processar_eventos_agentes(self, eventos):
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                pos_mouse = pygame.mouse.get_pos()
                if self.botoes_agentes["ASTAR"].collidepoint(pos_mouse):
                    return "ASTAR"
                elif self.botoes_agentes["GENETICO"].collidepoint(pos_mouse):
                    return "GENETICO"
                elif self.botoes_agentes["QLEARNING"].collidepoint(pos_mouse):
                    return "QLEARNING"
                elif self.botoes_agentes["VOLTAR"].collidepoint(pos_mouse):
                    return "VOLTAR"
        return "AGUARDANDO"

    def desenhar_agentes(self, tela):
        tela.fill(self.COR_FUNDO)
        img_titulo = self.fonte_titulo.render("TREINAMENTO DE IA", True, self.BRANCO)
        tela.blit(img_titulo, img_titulo.get_rect(center=(self.largura // 2, 120)))
        img_sub = self.fonte_botoes.render("Selecione o Modelo de Inteligência Artificial", True, self.AZUL_DESTAQUE)
        tela.blit(img_sub, img_sub.get_rect(center=(self.largura // 2, 170)))
        self._desenhar_botoes(tela, self.botoes_agentes, ["ASTAR", "GENETICO", "QLEARNING", "VOLTAR"],
                              ["Agente A* (Busca)", "Algoritmo Genético", "Q-Learning (RL)", "<- Voltar ao Menu"])

    def processar_eventos_wip(self, eventos):
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if self.botao_wip_voltar.collidepoint(pygame.mouse.get_pos()): return "VOLTAR"
        return "AGUARDANDO"

    def desenhar_em_desenvolvimento(self, tela, nome_agente):
        tela.fill(self.COR_FUNDO)
        img_titulo = self.fonte_titulo.render("EM CONSTRUÇÃO", True, self.OURO)
        tela.blit(img_titulo, img_titulo.get_rect(center=(self.largura // 2, 250)))
        img_sub = self.fonte_botoes.render(f"A integração do modelo {nome_agente} será disponibilizada em breve.", True,
                                           self.CINZA)
        tela.blit(img_sub, img_sub.get_rect(center=(self.largura // 2, 320)))
        self._desenhar_botoes(tela, {"VOLTAR": self.botao_wip_voltar}, ["VOLTAR"], ["<- Voltar"])

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
        self._desenhar_botoes(tela, self.botoes_dificuldade, ["FACIL", "MEDIO", "DIFICIL", "VOLTAR"],
                              ["Modo Fácil", "Modo Médio", "Modo Difícil", "<- Voltar"])

    # --- NOVAS TELAS DO ALGORITMO GENÉTICO ---
    def desenhar_treinamento_ag(self, tela, dados_geracao):
        tela.fill(self.COR_FUNDO)
        img_titulo = self.fonte_titulo.render("Evoluindo População...", True, self.OURO)
        tela.blit(img_titulo, img_titulo.get_rect(center=(self.largura // 2, 250)))

        texto = f"Geração: {dados_geracao['geracao']}  |  Melhor Fitness: {dados_geracao['fitness_campeao']:.0f}  |  Taxa de Sobrevivência: {dados_geracao['taxa_sucesso'] * 100:.1f}%"
        img_sub = self.fonte_botoes.render(texto, True, self.BRANCO)
        tela.blit(img_sub, img_sub.get_rect(center=(self.largura // 2, 320)))

        img_aviso = self.fonte_sub.render(
            "Os cálculos pesados estão ocorrendo em background. Pressione [ESC] para abortar.", True, self.CINZA)
        tela.blit(img_aviso, img_aviso.get_rect(center=(self.largura // 2, 400)))

    def preparar_galeria(self, historico):
        """Seleciona de forma inteligente 4 marcos históricos para exibir na Galeria."""
        self.botoes_galeria = []
        self.dados_galeria = []
        if not historico: return

        indices = []
        if len(historico) <= 4:
            indices = list(range(len(historico)))
        else:
            indices = [0, len(historico) // 3, (len(historico) * 2) // 3, len(historico) - 1]

        largura_btn = 550
        centro_x = (self.largura // 2) - (largura_btn // 2)
        y_pos = 200

        for i in indices:
            self.botoes_galeria.append(pygame.Rect(centro_x, y_pos, largura_btn, 60))
            self.dados_galeria.append(historico[i])
            y_pos += 80

        self.botao_wip_voltar.y = y_pos + 40

    def processar_eventos_galeria(self, eventos):
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                pos_mouse = pygame.mouse.get_pos()
                for i, btn in enumerate(self.botoes_galeria):
                    if btn.collidepoint(pos_mouse): return self.dados_galeria[i]
                if self.botao_wip_voltar.collidepoint(pos_mouse): return "VOLTAR"
        return "AGUARDANDO"

    def desenhar_galeria(self, tela):
        tela.fill(self.COR_FUNDO)
        img_titulo = self.fonte_titulo.render("GALERIA DE REPLAYS EVOLUTIVOS", True, self.BRANCO)
        tela.blit(img_titulo, img_titulo.get_rect(center=(self.largura // 2, 100)))

        pos_mouse = pygame.mouse.get_pos()
        for i, rect in enumerate(self.botoes_galeria):
            dados = self.dados_galeria[i]
            if rect.collidepoint(pos_mouse):
                pygame.draw.rect(tela, self.VERDE, rect, border_radius=8)
                cor_txt = self.COR_FUNDO
            else:
                pygame.draw.rect(tela, (35, 42, 55), rect, border_radius=8)
                pygame.draw.rect(tela, self.CINZA, rect, 2, border_radius=8)
                cor_txt = self.BRANCO

            texto = f"Assistir Geração {dados['geracao']} (Fitness: {dados['fitness_campeao']:.0f})"
            img_txt = self.fonte_botoes.render(texto, True, cor_txt)
            tela.blit(img_txt, img_txt.get_rect(center=rect.center))

        self._desenhar_botoes(tela, {"VOLTAR": self.botao_wip_voltar}, ["VOLTAR"], ["<- Voltar"])

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