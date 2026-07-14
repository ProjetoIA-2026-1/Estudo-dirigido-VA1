import pygame
import sys
from environment import CampoBatalhaEnv
from interface.dashboard import Dashboard
from interface.menu import MenuPrincipal
from agent_astar import AgenteAStar


def main():
    pygame.init()

    LARGURA_TELA = 1280
    ALTURA_TELA = 720
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("Resgate Tático: Inteligência Artificial")

    menu = MenuPrincipal(LARGURA_TELA, ALTURA_TELA)
    dashboard = Dashboard()

    env = CampoBatalhaEnv(dificuldade="MEDIO")

    estado_atual = "ESTADO_MENU"
    pontuacao = 0
    status_jogo = "Correndo"
    acao_str = "Aguardando..."

    agente_selecionado = None

    # Variáveis de Controle de Animação da IA
    ia_em_execucao = False
    rota_ia = []
    indice_rota = 0
    delay_passo_ia = 150
    ultimo_tempo_mov = 0

    relogio = pygame.time.Clock()

    while True:
        tempo_atual = pygame.time.get_ticks()
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
            elif novo_estado == "SELECIONAR_DIF_MANUAL":
                estado_atual = novo_estado
            elif novo_estado == "ESTADO_SELECIONAR_AGENTE":
                estado_atual = novo_estado

            menu.desenhar(tela)

        # ==========================================
        # 1.5. ESTADO: TELA DE SELEÇÃO DE AGENTE IA
        # ==========================================
        elif estado_atual == "ESTADO_SELECIONAR_AGENTE":
            escolha_agente = menu.processar_eventos_agentes(eventos)

            if escolha_agente == "VOLTAR":
                estado_atual = "ESTADO_MENU"
            elif escolha_agente == "ASTAR":
                agente_selecionado = "A*"
                estado_atual = "SELECIONAR_DIF_IA"
            elif escolha_agente in ["GENETICO", "QLEARNING"]:
                agente_selecionado = "Algoritmo Genético" if escolha_agente == "GENETICO" else "Q-Learning"
                estado_atual = "ESTADO_EM_DESENVOLVIMENTO"  # <-- Roteamento de Bloqueio

            menu.desenhar_agentes(tela)

        # ==========================================
        # 1.6. ESTADO: TELA "EM DESENVOLVIMENTO"
        # ==========================================
        elif estado_atual == "ESTADO_EM_DESENVOLVIMENTO":
            escolha = menu.processar_eventos_wip(eventos)
            if escolha == "VOLTAR":
                estado_atual = "ESTADO_SELECIONAR_AGENTE"

            # Permite voltar com ESC
            for evento in eventos:
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    estado_atual = "ESTADO_SELECIONAR_AGENTE"

            menu.desenhar_em_desenvolvimento(tela, agente_selecionado)

        # ==========================================
        # 2. ESTADO: TELA DE SELEÇÃO DE DIFICULDADE
        # ==========================================
        elif estado_atual in ["SELECIONAR_DIF_MANUAL", "SELECIONAR_DIF_IA"]:
            escolha = menu.processar_eventos_dificuldade(eventos)

            if escolha == "VOLTAR":
                estado_atual = "ESTADO_MENU" if estado_atual == "SELECIONAR_DIF_MANUAL" else "ESTADO_SELECIONAR_AGENTE"

            elif escolha in ["FACIL", "MEDIO", "DIFICIL"]:
                env = CampoBatalhaEnv(dificuldade=escolha)
                env.reset()
                pontuacao = 0
                status_jogo = "Correndo"
                acao_str = f"[{agente_selecionado}] Prontidão" if estado_atual == "SELECIONAR_DIF_IA" else "Nova Simulação"
                ia_em_execucao = False

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
                    if evento.key == pygame.K_ESCAPE:
                        estado_atual = "ESTADO_MENU"
                    elif evento.key == pygame.K_r:
                        env.reset()
                        pontuacao = 0
                        status_jogo = "Correndo"
                        acao_str = "Nova Simulação"
                    elif evento.key == pygame.K_n and "VITÓRIA" in status_jogo:
                        if env.dificuldade == "FACIL":
                            env = CampoBatalhaEnv(dificuldade="MEDIO")
                        elif env.dificuldade == "MEDIO":
                            env = CampoBatalhaEnv(dificuldade="DIFICIL")
                        env.reset()
                        pontuacao = 0
                        status_jogo = "Correndo"
                        acao_str = "Avançou de Nível"
                    elif status_jogo == "Correndo":
                        if evento.key == pygame.K_UP:
                            acao = 0; acao_str = "Avançar"; tomou_acao = True
                        elif evento.key == pygame.K_LEFT:
                            acao = 1; acao_str = "Esquerda"; tomou_acao = True
                        elif evento.key == pygame.K_RIGHT:
                            acao = 2; acao_str = "Direita"; tomou_acao = True
                        elif evento.key == pygame.K_DOWN:
                            acao = 3; acao_str = "Recuar"; tomou_acao = True

            if tomou_acao and status_jogo == "Correndo":
                _, recompensa, done, _ = env.step(acao)
                pontuacao += recompensa
                if done:
                    status_jogo = "VITÓRIA!" if recompensa == 100 else "GAME OVER"

            tela.fill((0, 0, 0))
            dashboard.renderizar_frame(tela, env, pontuacao, acao_str, status_jogo, modo="MANUAL")

        # ==========================================
        # 4. ESTADO: TELA DOS AGENTES (IA)
        # ==========================================
        elif estado_atual == "ESTADO_AGENTES":
            for evento in eventos:
                if evento.type == pygame.KEYDOWN:

                    if evento.key == pygame.K_ESCAPE:
                        estado_atual = "ESTADO_MENU"
                        ia_em_execucao = False
                    elif evento.key == pygame.K_r:
                        env.reset()
                        pontuacao = 0
                        status_jogo = "Correndo"
                        acao_str = f"[{agente_selecionado}] Prontidão"
                        ia_em_execucao = False
                    elif evento.key == pygame.K_n and "VITÓRIA" in status_jogo:
                        if env.dificuldade == "FACIL":
                            env = CampoBatalhaEnv(dificuldade="MEDIO")
                        elif env.dificuldade == "MEDIO":
                            env = CampoBatalhaEnv(dificuldade="DIFICIL")
                        env.reset()
                        pontuacao = 0
                        status_jogo = "Correndo"
                        acao_str = "Avançou de Nível"
                        ia_em_execucao = False

                    elif evento.key == pygame.K_a and status_jogo == "Correndo" and not ia_em_execucao:
                        agente = AgenteAStar(env)
                        acao_str = "A* Calculando Rota..."
                        dashboard.renderizar_frame(tela, env, pontuacao, acao_str, status_jogo, modo="IA")
                        pygame.display.flip()

                        rota_ia = agente.planejar_rota()
                        if rota_ia:
                            ia_em_execucao = True
                            indice_rota = 0
                            ultimo_tempo_mov = tempo_atual
                        else:
                            acao_str = "A* Erro: Sem Saída!"

            if ia_em_execucao and status_jogo == "Correndo":
                if tempo_atual - ultimo_tempo_mov > delay_passo_ia:
                    if indice_rota < len(rota_ia):
                        acao = rota_ia[indice_rota]
                        mapa_acoes = {0: "Avançar", 1: "Esquerda", 2: "Direita", 3: "Recuar"}
                        acao_str = f"A* -> {mapa_acoes[acao]}"

                        _, recompensa, done, _ = env.step(acao)
                        pontuacao += recompensa

                        if done:
                            status_jogo = "VITÓRIA!" if recompensa == 100 else "GAME OVER"
                            ia_em_execucao = False

                        indice_rota += 1
                        ultimo_tempo_mov = tempo_atual

            tela.fill((0, 0, 0))
            dashboard.renderizar_frame(tela, env, pontuacao, acao_str, status_jogo, modo="IA")

        pygame.display.flip()
        relogio.tick(30)


if __name__ == "__main__":
    main()