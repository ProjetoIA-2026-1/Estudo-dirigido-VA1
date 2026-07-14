import pygame
import sys
from environment import CampoBatalhaEnv
from interface.dashboard import Dashboard
from interface.menu import MenuPrincipal


def main():
    pygame.init()

    LARGURA_TELA = 1280
    ALTURA_TELA = 720
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("Resgate Tático: Inteligência Artificial")

    menu = MenuPrincipal(LARGURA_TELA, ALTURA_TELA)
    dashboard = Dashboard()

    # Inicia com um ambiente padrão apenas para existir na memória
    env = CampoBatalhaEnv(dificuldade="MEDIO")

    estado_atual = "ESTADO_MENU"
    pontuacao = 0
    status_jogo = "Correndo"
    acao_str = "Aguardando..."

    fonte_tit_ag = pygame.font.SysFont("Segoe UI", 40, bold=True)
    fonte_sub_ag = pygame.font.SysFont("Segoe UI", 20)
    img_tit_ag = fonte_tit_ag.render("PAINEL DOS AGENTES IA (EM CONSTRUÇÃO)", True, (0, 180, 255))
    img_sub_ag = fonte_sub_ag.render("Aqui visualizaremos o A*, Algoritmo Genético e Q-Learning.", True,
                                     (170, 180, 190))
    img_esc_ag = fonte_sub_ag.render("Pressione [ESC] para retornar ao Menu.", True, (240, 240, 245))

    relogio = pygame.time.Clock()

    while True:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # ==========================================
        # 1. ESTADO: MENU PRINCIPAL
        # ==========================================
        if estado_atual == "ESTADO_MENU":
            novo_estado = menu.processar_eventos(eventos)
            if novo_estado == "SAIR":
                pygame.quit()
                sys.exit()
            elif novo_estado in ["SELECIONAR_DIF_MANUAL", "SELECIONAR_DIF_IA"]:
                estado_atual = novo_estado

            menu.desenhar(tela)

        # ==========================================
        # 2. ESTADO: TELA DE SELEÇÃO DE DIFICULDADE
        # ==========================================
        elif estado_atual in ["SELECIONAR_DIF_MANUAL", "SELECIONAR_DIF_IA"]:
            escolha = menu.processar_eventos_dificuldade(eventos)

            if escolha == "VOLTAR":
                estado_atual = "ESTADO_MENU"
            elif escolha in ["FACIL", "MEDIO", "DIFICIL"]:
                # É AQUI QUE A MÁGICA ACONTECE! Recriamos o mapa com a dificuldade escolhida.
                env = CampoBatalhaEnv(dificuldade=escolha)
                env.reset()
                pontuacao = 0
                status_jogo = "Correndo"
                acao_str = "Nova Simulação"

                # Encaminha para o modo correto
                if estado_atual == "SELECIONAR_DIF_MANUAL":
                    estado_atual = "ESTADO_JOGAR"
                else:
                    estado_atual = "ESTADO_AGENTES"

            modo_origem = "MANUAL" if estado_atual == "SELECIONAR_DIF_MANUAL" else "IA"
            menu.desenhar_dificuldade(tela, modo_origem)

        # ==========================================
        # 3. ESTADO: SIMULAÇÃO MANUAL
        # ==========================================
        elif estado_atual == "ESTADO_JOGAR":
            tomou_acao = False
            acao = -1

            for evento in eventos:
                if evento.type == pygame.KEYDOWN:

                    # 1. ESC Volta ao Menu
                    if evento.key == pygame.K_ESCAPE:
                        estado_atual = "ESTADO_MENU"

                    # 2. R Reinicia o mesmo nível
                    elif evento.key == pygame.K_r:
                        env.reset()
                        pontuacao = 0
                        status_jogo = "Correndo"
                        acao_str = "Nova Simulação"

                    # --- NOVIDADE: N Avança para o próximo nível ---
                    elif evento.key == pygame.K_n and "VITÓRIA" in status_jogo:
                        if env.dificuldade == "FACIL":
                            env = CampoBatalhaEnv(dificuldade="MEDIO")
                        elif env.dificuldade == "MEDIO":
                            env = CampoBatalhaEnv(dificuldade="DIFICIL")

                        env.reset()
                        pontuacao = 0
                        status_jogo = "Correndo"
                        acao_str = "Avançou de Nível"

                    # 3. Teclas de Movimento (Só operam se estiver vivo)
                    elif status_jogo == "Correndo":
                        if evento.key == pygame.K_UP:
                            acao = 0
                            acao_str = "Avançar"
                            tomou_acao = True
                        elif evento.key == pygame.K_LEFT:
                            acao = 1
                            acao_str = "Esquerda"
                            tomou_acao = True
                        elif evento.key == pygame.K_RIGHT:
                            acao = 2
                            acao_str = "Direita"
                            tomou_acao = True
                        elif evento.key == pygame.K_DOWN:
                            acao = 3
                            acao_str = "Recuar"
                            tomou_acao = True

            if tomou_acao and status_jogo == "Correndo":
                _, recompensa, done, _ = env.step(acao)
                pontuacao += recompensa
                if done:
                    status_jogo = "VITÓRIA!" if recompensa == 100 else "GAME OVER"

            tela.fill((0, 0, 0))
            dashboard.renderizar_frame(tela, env, pontuacao, acao_str, status_jogo)

        # ==========================================
        # 4. ESTADO: TELA DOS AGENTES
        # ==========================================
        elif estado_atual == "ESTADO_AGENTES":
            for evento in eventos:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        estado_atual = "ESTADO_MENU"

            tela.fill((15, 18, 25))
            tela.blit(img_tit_ag, (LARGURA_TELA // 2 - img_tit_ag.get_width() // 2, ALTURA_TELA // 2 - 60))
            tela.blit(img_sub_ag, (LARGURA_TELA // 2 - img_sub_ag.get_width() // 2, ALTURA_TELA // 2 + 10))

            # Mostra a dificuldade escolhida
            img_dif = fonte_sub_ag.render(f"Dificuldade Selecionada: {env.dificuldade}", True, (255, 190, 50))
            tela.blit(img_dif, (LARGURA_TELA // 2 - img_dif.get_width() // 2, ALTURA_TELA // 2 + 40))

            tela.blit(img_esc_ag, (LARGURA_TELA // 2 - img_esc_ag.get_width() // 2, ALTURA_TELA // 2 + 90))

        pygame.display.flip()
        relogio.tick(30)


if __name__ == "__main__":
    main()