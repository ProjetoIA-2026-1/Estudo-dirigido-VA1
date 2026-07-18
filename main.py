import pygame
import sys
from environment import CampoBatalhaEnv
from interface.dashboard import Dashboard
from interface.menu import MenuPrincipal
from agent_astar import AgenteAStar
from agent_genetic import AlgoritmoGenetico
from agent_qlearning import AgenteQLearning


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
    geracao_alvo_ag = 800

    ia_em_execucao = False
    rota_ia = []

    # --- NOVIDADE: Variável que guarda a visão atual do agente para o Replay ---
    estado_ia = None

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
                pygame.quit();
                sys.exit()
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
                estado_atual = "SELECIONAR_DIF_IA"
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
                estado_ia = env.reset()
                pontuacao = 0
                status_jogo = "Correndo"
                ia_em_execucao = False

                if estado_atual == "SELECIONAR_DIF_MANUAL":
                    acao_str = "Nova Simulação"
                    estado_atual = "ESTADO_JOGAR"
                else:
                    if agente_selecionado == "Algoritmo Genético":
                        acao_str = "[AG] Pressione T ou C"
                        estado_atual = "ESTADO_AGENTES"
                    elif agente_selecionado == "Q-Learning":
                        ag_instancia = AgenteQLearning(env)
                        estado_atual = "ESTADO_TREINANDO_QL"
                    else:
                        acao_str = f"[{agente_selecionado}] Prontidão"
                        estado_atual = "ESTADO_AGENTES"

            menu.desenhar_dificuldade(tela, "MANUAL" if estado_atual == "SELECIONAR_DIF_MANUAL" else "IA")

        # ==========================================
        # 3. ESTADO: TREINAMENTO DO GENÉTICO (BACKGROUND)
        # ==========================================
        elif estado_atual == "ESTADO_TREINANDO_IA":
            for evento in eventos:
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    estado_atual = "SELECIONAR_DIF_IA"

            if estado_atual == "ESTADO_TREINANDO_IA":
                terminou, dados_geracao_ag = ag_instancia.treinar_uma_geracao()
                menu.desenhar_treinamento_ag(tela, dados_geracao_ag)

                if terminou or ag_instancia.geracao_atual > geracao_alvo_ag:
                    ag_instancia.salvar_historico()
                    menu.preparar_galeria(ag_instancia.historico)
                    estado_atual = "ESTADO_GALERIA_AG"

        # ==========================================
        # 3.5. ESTADO: TREINAMENTO DO Q-LEARNING
        # ==========================================
        elif estado_atual == "ESTADO_TREINANDO_QL":
            for evento in eventos:
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    estado_atual = "SELECIONAR_DIF_IA"

            if estado_atual == "ESTADO_TREINANDO_QL":
                dados_ep = None
                for _ in range(40):
                    if not ag_instancia.treinado:
                        _, dados_ep = ag_instancia.treinar_um_episodio()
                    else:
                        break

                menu.desenhar_treinamento_ql(tela, dados_ep, ag_instancia.episodios_totais)

                if ag_instancia.treinado:
                    estado_ia = env.reset()
                    pontuacao = 0
                    status_jogo = "Correndo"
                    acao_str = "[Q-Learning] Prontidão para Execução!"
                    ia_em_execucao = False
                    rota_ia = []
                    estado_atual = "ESTADO_AGENTES"

        # ==========================================
        # 4. ESTADO: GALERIA DE REPLAYS (JSON)
        # ==========================================
        elif estado_atual == "ESTADO_GALERIA_AG":
            escolha = menu.processar_eventos_galeria(eventos)
            if escolha == "VOLTAR":
                estado_atual = "SELECIONAR_DIF_IA"
            elif isinstance(escolha, dict):
                env = CampoBatalhaEnv(dificuldade=escolha["dificuldade"], seed=escolha["semente_mapa"])

                # Reseta e já guarda a primeira visão que a Rede Neural vai precisar!
                estado_ia = env.reset()

                rota_ia = escolha["cromossomo"]  # O cromossomo aqui são os pesos!
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
            tomou_acao = False
            acao = -1
            for evento in eventos:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        estado_atual = "SELECIONAR_DIF_MANUAL"
                    elif evento.key == pygame.K_r:
                        estado_ia = env.reset();
                        pontuacao = 0;
                        status_jogo = "Correndo";
                        acao_str = "Nova Simulação"
                    elif evento.key == pygame.K_n and "VITÓRIA" in status_jogo:
                        if env.dificuldade == "FACIL":
                            env = CampoBatalhaEnv(dificuldade="MEDIO")
                        elif env.dificuldade == "MEDIO":
                            env = CampoBatalhaEnv(dificuldade="DIFICIL")
                        estado_ia = env.reset();
                        pontuacao = 0;
                        status_jogo = "Correndo";
                        acao_str = "Avançou de Nível"
                    elif status_jogo == "Correndo":
                        if evento.key == pygame.K_UP:
                            acao = 0;
                            acao_str = "Avançar";
                            tomou_acao = True
                        elif evento.key == pygame.K_LEFT:
                            acao = 1;
                            acao_str = "Esquerda";
                            tomou_acao = True
                        elif evento.key == pygame.K_RIGHT:
                            acao = 2;
                            acao_str = "Direita";
                            tomou_acao = True
                        elif evento.key == pygame.K_DOWN:
                            acao = 3;
                            acao_str = "Recuar";
                            tomou_acao = True

            if tomou_acao and status_jogo == "Correndo":
                estado_ia, recompensa, done, _ = env.step(acao)
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

                    if evento.key == pygame.K_ESCAPE:
                        if agente_selecionado in ["A*", "Q-Learning"]:
                            estado_atual = "SELECIONAR_DIF_IA"
                        elif agente_selecionado == "Algoritmo Genético" and acao_str in ["[AG] Pressione T ou C",
                                                                                         "Nenhum Checkpoint Encontrado!"]:
                            estado_atual = "SELECIONAR_DIF_IA"
                        else:
                            estado_atual = "ESTADO_GALERIA_AG"
                        ia_em_execucao = False

                    elif evento.key == pygame.K_r:
                        estado_ia = env.reset()
                        pontuacao = 0
                        status_jogo = "Correndo"
                        if acao_str != "Pronto para Replay!":
                            acao_str = f"[{agente_selecionado}] Prontidão"
                        ia_em_execucao = False

                    elif evento.key == pygame.K_m and agente_selecionado == "A*":
                        env = CampoBatalhaEnv(dificuldade=env.dificuldade)
                        estado_ia = env.reset()
                        pontuacao = 0
                        status_jogo = "Correndo"
                        acao_str = "Novo Mapa Gerado!"
                        ia_em_execucao = False
                        rota_ia = []

                    elif evento.key == pygame.K_m and agente_selecionado == "Q-Learning":
                        env = CampoBatalhaEnv(dificuldade=env.dificuldade)
                        estado_ia = env.reset()
                        ag_instancia = AgenteQLearning(env)
                        pontuacao = 0
                        status_jogo = "Correndo"
                        acao_str = "[Q-Learning] Retreinando em Novo Mapa..."
                        ia_em_execucao = False
                        rota_ia = []
                        estado_atual = "ESTADO_TREINANDO_QL"

                    elif evento.key == pygame.K_n and agente_selecionado == "Q-Learning":
                        if env.dificuldade in ["FACIL", "MEDIO"]:
                            nova_dif = "MEDIO" if env.dificuldade == "FACIL" else "DIFICIL"
                            env = CampoBatalhaEnv(dificuldade=nova_dif)
                            estado_ia = env.reset()
                            ag_instancia = AgenteQLearning(env)
                            pontuacao = 0
                            status_jogo = "Correndo"
                            acao_str = f"[Q-Learning] Retreinando no Nível {nova_dif}..."
                            ia_em_execucao = False
                            rota_ia = []
                            estado_atual = "ESTADO_TREINANDO_QL"

                    elif evento.key == pygame.K_t and agente_selecionado == "Algoritmo Genético":
                        ag_instancia = AlgoritmoGenetico(env)
                        ag_instancia.inicializar_populacao()
                        geracao_alvo_ag = 800
                        estado_atual = "ESTADO_TREINANDO_IA"

                    elif evento.key == pygame.K_c and agente_selecionado == "Algoritmo Genético":
                        ag_instancia = AlgoritmoGenetico(env)
                        if ag_instancia.carregar_checkpoint():
                            env = CampoBatalhaEnv(dificuldade=ag_instancia.historico[-1]["dificuldade"],
                                                  seed=ag_instancia.env.seed_atual)
                            estado_ia = env.reset()
                            ag_instancia.env = env
                            geracao_alvo_ag = ag_instancia.geracao_atual + 800
                            estado_atual = "ESTADO_TREINANDO_IA"
                        else:
                            acao_str = "Nenhum Checkpoint Encontrado!"

                    elif evento.key == pygame.K_a and not ia_em_execucao:
                        if status_jogo != "Correndo" and agente_selecionado == "Q-Learning":
                            estado_ia = env.reset()
                            pontuacao = 0
                            status_jogo = "Correndo"

                        if status_jogo == "Correndo":
                            # Quando aperta 'A', disparamos as IAs
                            if agente_selecionado == "A*":
                                agente = AgenteAStar(env)
                                acao_str = "A* Calculando Rota..."
                                dashboard.renderizar_frame(tela, env, pontuacao, acao_str, status_jogo, modo="IA_ASTAR")
                                pygame.display.flip()
                                rota_ia = agente.planejar_rota()
                                if not rota_ia: acao_str = "A* Erro: Sem Saída!"

                            elif agente_selecionado == "Q-Learning":
                                acao_str = "Q-Learning Planejando..."
                                dashboard.renderizar_frame(tela, env, pontuacao, acao_str, status_jogo,
                                                           modo="IA_QLEARNING", ag_instancia=ag_instancia)
                                pygame.display.flip()
                                rota_ia = ag_instancia.planejar_rota()
                                estado_ia = env.reset()
                                if not rota_ia: acao_str = "Q-Learning: Rota não encontrada!"

                            # Se for Genético, a "rota_ia" já está preenchida com os pesos que vieram do JSON!
                            if rota_ia:
                                ia_em_execucao = True
                                indice_rota = 0
                                ultimo_tempo_mov = tempo_atual

            if ia_em_execucao and status_jogo == "Correndo":
                if tempo_atual - ultimo_tempo_mov > delay_passo_ia:

                    # --- NOVIDADE: A bifurcação do cérebro Reativo vs Estático ---
                    if agente_selecionado == "Algoritmo Genético":
                        # Instancia um agente só pra usar a função matemática de pesos dele
                        ag_dummy = AlgoritmoGenetico(env)
                        visao_local, dist_fogo = estado_ia
                        # Rota_ia nesse contexto guarda os pesos da rede neural!
                        acao = ag_dummy._decidir_acao(rota_ia, visao_local, dist_fogo)
                    else:
                        if indice_rota < len(rota_ia):
                            acao = rota_ia[indice_rota]
                        else:
                            ia_em_execucao = False
                            continue  # Sai do loop se a rota estática acabou

                    mapa_acoes = {0: "Avançar", 1: "Esquerda", 2: "Direita", 3: "Recuar"}
                    acao_str = f"IA -> {mapa_acoes[acao]}"

                    # Atualiza o estado da IA com o que ela está enxergando agora
                    estado_ia, recompensa, done, _ = env.step(acao)
                    pontuacao += recompensa

                    if done:
                        status_jogo = "VITÓRIA!" if recompensa == 100 else "GAME OVER"
                        ia_em_execucao = False

                    indice_rota += 1
                    ultimo_tempo_mov = tempo_atual

            tela.fill((0, 0, 0))

            if agente_selecionado == "A*":
                modo_painel = "IA_ASTAR"
            elif agente_selecionado == "Q-Learning":
                modo_painel = "IA_QLEARNING"
            elif agente_selecionado == "Algoritmo Genético":
                if acao_str in ["[AG] Pressione T ou C", "Nenhum Checkpoint Encontrado!"]:
                    modo_painel = "IA_GENETICO"
                else:
                    modo_painel = "IA_REPLAY"
            else:
                modo_painel = "IA_REPLAY"

            dashboard.renderizar_frame(tela, env, pontuacao, acao_str, status_jogo, modo=modo_painel,
                                       ag_instancia=ag_instancia)

        pygame.display.flip()
        relogio.tick(30)


if __name__ == "__main__":
    main()