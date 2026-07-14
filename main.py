import pygame
import sys
from environment import CampoBatalhaEnv
from interface.dashboard import Dashboard
from interface.menu import MenuPrincipal
from agent_astar import AgenteAStar
from agent_genetic import AlgoritmoGenetico


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

    ag_instancia = None
    dados_geracao_ag = None

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
                pygame.quit(); sys.exit()
            elif novo_estado in ["SELECIONAR_DIF_MANUAL", "ESTADO_SELECIONAR_AGENTE"]:
                estado_atual = novo_estado
            menu.desenhar(tela)

        # ==========================================
        # 1.5. ESTADO: TELA DE SELEÇÃO DE AGENTE IA
        # ==========================================
        elif estado_atual == "ESTADO_SELECIONAR_AGENTE":
            escolha_agente = menu.processar_eventos_agentes(eventos)
            if escolha_agente == "VOLTAR":
                estado_atual = "ESTADO_MENU"
            elif escolha_agente in ["ASTAR", "GENETICO"]:
                agente_selecionado = "A*" if escolha_agente == "ASTAR" else "Algoritmo Genético"
                estado_atual = "SELECIONAR_DIF_IA"
            elif escolha_agente == "QLEARNING":
                agente_selecionado = "Q-Learning"
                estado_atual = "ESTADO_EM_DESENVOLVIMENTO"
            menu.desenhar_agentes(tela)

        # ==========================================
        # 1.6. ESTADO: TELA "EM DESENVOLVIMENTO"
        # ==========================================
        elif estado_atual == "ESTADO_EM_DESENVOLVIMENTO":
            if menu.processar_eventos_wip(eventos) == "VOLTAR": estado_atual = "ESTADO_SELECIONAR_AGENTE"
            for evento in eventos:
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE: estado_atual = "ESTADO_SELECIONAR_AGENTE"
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
                ia_em_execucao = False

                if estado_atual == "SELECIONAR_DIF_MANUAL":
                    acao_str = "Nova Simulação"
                    estado_atual = "ESTADO_JOGAR"
                else:
                    if agente_selecionado == "Algoritmo Genético":
                        ag_instancia = AlgoritmoGenetico(env)
                        ag_instancia.inicializar_populacao()
                        estado_atual = "ESTADO_TREINANDO_IA"
                    else:
                        acao_str = f"[{agente_selecionado}] Prontidão"
                        estado_atual = "ESTADO_AGENTES"

            menu.desenhar_dificuldade(tela, "MANUAL" if estado_atual == "SELECIONAR_DIF_MANUAL" else "IA")

        # ==========================================
        # 3. ESTADO: TREINAMENTO DO GENÉTICO (BACKGROUND)
        # ==========================================
        elif estado_atual == "ESTADO_TREINANDO_IA":
            for evento in eventos:
                # O ESC agora volta um passo para trás (escolher dificuldade)
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    estado_atual = "SELECIONAR_DIF_IA"

            if estado_atual == "ESTADO_TREINANDO_IA":
                terminou, dados_geracao_ag = ag_instancia.treinar_uma_geracao()
                menu.desenhar_treinamento_ag(tela, dados_geracao_ag)

                # Aumentamos o limite para 800 gerações!
                if terminou or ag_instancia.geracao_atual > 800:
                    menu.preparar_galeria(ag_instancia.historico)
                    estado_atual = "ESTADO_GALERIA_AG"

        # ==========================================
        # 4. ESTADO: GALERIA DE REPLAYS (JSON)
        # ==========================================
        elif estado_atual == "ESTADO_GALERIA_AG":
            escolha = menu.processar_eventos_galeria(eventos)
            # Voltar daqui vai para a tela de dificuldade do Agente Genético
            if escolha == "VOLTAR":
                estado_atual = "SELECIONAR_DIF_IA"
            elif isinstance(escolha, dict):
                env = CampoBatalhaEnv(dificuldade=escolha["dificuldade"], seed=escolha["semente_mapa"])
                env.reset()
                rota_ia = escolha["cromossomo"]
                pontuacao = 0
                status_jogo = "Correndo"
                acao_str = "Pronto para Replay!"
                ia_em_execucao = False
                indice_rota = 0
                ultimo_tempo_mov = tempo_atual
                estado_atual = "ESTADO_AGENTES"

            menu.desenhar_galeria(tela)

        # ==========================================
        # 5. ESTADO: SIMULAÇÃO MANUAL
        # ==========================================
        elif estado_atual == "ESTADO_JOGAR":
            tomou_acao = False;
            acao = -1
            for evento in eventos:
                if evento.type == pygame.KEYDOWN:
                    # ESC volta pra dificuldade
                    if evento.key == pygame.K_ESCAPE:
                        estado_atual = "SELECIONAR_DIF_MANUAL"
                    elif evento.key == pygame.K_r:
                        env.reset(); pontuacao = 0; status_jogo = "Correndo"; acao_str = "Nova Simulação"
                    elif evento.key == pygame.K_n and "VITÓRIA" in status_jogo:
                        if env.dificuldade == "FACIL":
                            env = CampoBatalhaEnv(dificuldade="MEDIO")
                        elif env.dificuldade == "MEDIO":
                            env = CampoBatalhaEnv(dificuldade="DIFICIL")
                        env.reset();
                        pontuacao = 0;
                        status_jogo = "Correndo";
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
                if done: status_jogo = "VITÓRIA!" if recompensa == 100 else "GAME OVER"
            tela.fill((0, 0, 0))
            dashboard.renderizar_frame(tela, env, pontuacao, acao_str, status_jogo, modo="MANUAL")

        # ==========================================
        # 6. ESTADO: TELA DOS AGENTES (IA E REPLAY)
        # ==========================================
        elif estado_atual == "ESTADO_AGENTES":
            for evento in eventos:
                if evento.type == pygame.KEYDOWN:

                    # ESC Inteligente
                    if evento.key == pygame.K_ESCAPE:
                        if agente_selecionado == "A*":
                            estado_atual = "SELECIONAR_DIF_IA"
                        else:
                            estado_atual = "ESTADO_GALERIA_AG"  # Replay volta pra Galeria
                        ia_em_execucao = False

                    elif evento.key == pygame.K_r:
                        env.reset();
                        pontuacao = 0;
                        status_jogo = "Correndo";
                        acao_str = f"[{agente_selecionado}] Prontidão";
                        ia_em_execucao = False

                    # Tecla M: Novo mapa (Apenas para o A*)
                    elif evento.key == pygame.K_m and agente_selecionado == "A*":
                        env = CampoBatalhaEnv(dificuldade=env.dificuldade)
                        env.reset()
                        pontuacao = 0;
                        status_jogo = "Correndo";
                        acao_str = "Novo Mapa Gerado!"
                        ia_em_execucao = False;
                        rota_ia = []

                    elif evento.key == pygame.K_a and status_jogo == "Correndo" and not ia_em_execucao:
                        if agente_selecionado == "A*":
                            agente = AgenteAStar(env)
                            acao_str = "A* Calculando Rota..."
                            # Mostramos "IA_ASTAR" no rodapé para exibir a opção [M]
                            dashboard.renderizar_frame(tela, env, pontuacao, acao_str, status_jogo, modo="IA_ASTAR")
                            pygame.display.flip()
                            rota_ia = agente.planejar_rota()
                            if not rota_ia: acao_str = "A* Erro: Sem Saída!"

                        if rota_ia:
                            ia_em_execucao = True
                            indice_rota = 0
                            ultimo_tempo_mov = tempo_atual

            if ia_em_execucao and status_jogo == "Correndo":
                if tempo_atual - ultimo_tempo_mov > delay_passo_ia:
                    if indice_rota < len(rota_ia):
                        acao = rota_ia[indice_rota]
                        mapa_acoes = {0: "Avançar", 1: "Esquerda", 2: "Direita", 3: "Recuar"}
                        acao_str = f"IA -> {mapa_acoes[acao]}"

                        _, recompensa, done, _ = env.step(acao)
                        pontuacao += recompensa

                        if done:
                            status_jogo = "VITÓRIA!" if recompensa == 100 else "GAME OVER"
                            ia_em_execucao = False

                        indice_rota += 1
                        ultimo_tempo_mov = tempo_atual

            tela.fill((0, 0, 0))
            # Ajusta o rodapé do Dashboard de forma contextual
            modo_painel = "IA_ASTAR" if agente_selecionado == "A*" else "IA_REPLAY"
            dashboard.renderizar_frame(tela, env, pontuacao, acao_str, status_jogo, modo=modo_painel)

        pygame.display.flip()
        relogio.tick(30)


if __name__ == "__main__":
    main()