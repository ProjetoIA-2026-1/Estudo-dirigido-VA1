import random
import numpy as np


class AgenteQLearning:
    """
    Agente inteligente baseado em Aprendizado por Reforço tabular (Q-Learning).
    Especializado em aprender a rota e a política de sobrevivência para um único mapa/seed instanciado.
    """

    def __init__(
        self,
        env,
        alpha=None,
        gamma=None,
        epsilon_inicial=1.0,
        epsilon_min=0.05,
        epsilon_decay=None,
        episodios_totais=None
    ):
        self.env = env

        # Configurações de Hiperparâmetros padrão com base na dificuldade do ambiente
        # Orçamento mais generoso de episódios para preenchimento profundo da Tabela Q
        config_defaults = {
            "FACIL":   {"alpha": 0.20, "gamma": 0.95, "decay": 0.992, "episodios": 600},
            "MEDIO":   {"alpha": 0.15, "gamma": 0.98, "decay": 0.996, "episodios": 1500},
            "DIFICIL": {"alpha": 0.10, "gamma": 0.99, "decay": 0.998, "episodios": 3000}
        }

        dificuldade = getattr(self.env, "dificuldade", "MEDIO").upper()
        if dificuldade not in config_defaults:
            dificuldade = "MEDIO"

        cfg = config_defaults[dificuldade]

        self.alpha = alpha if alpha is not None else cfg["alpha"]
        self.gamma = gamma if gamma is not None else cfg["gamma"]
        self.epsilon = epsilon_inicial
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay if epsilon_decay is not None else cfg["decay"]
        self.episodios_totais = episodios_totais if episodios_totais is not None else cfg["episodios"]

        # Tabela Q: dicionário mapeando o estado `(x, y, dist_tiros_disc)` -> `[Q(0), Q(1), Q(2), Q(3)]`
        # Ações permitidas no ambiente: 0=Avançar, 1=Esquerda, 2=Direita, 3=Recuar
        self.q_tabela = {}

        # Telemetria e histórico para análises e gráficos futuros
        self.historico = []
        self.episodio_atual = 0
        self.treinado = False

    def _discretizar_distancia_tiros(self, dist):
        """
        Discretiza a distância dos tiros que vêm por trás para simplificar o espaço de estados (Opção A).
        - 0: PERIGO EXTREMO (dist <= 1) -> tiros imediatamente atrás ou na mesma linha.
        - 1: ALERTA (2 <= dist <= 3) -> pouca margem para manobras laterais ou recuo.
        - 2: SEGURO (dist >= 4) -> margem folgada para exploração ou busca por chocolate.
        """
        if dist <= 1:
            return 0
        elif dist <= 3:
            return 1
        else:
            return 2

    def get_estado(self):
        """
        Obtém a representação atual do estado (s) diretamente do ambiente:
        s = (pos_x, pos_y, dist_tiros_discretizada)
        """
        x = self.env.posicao_x
        y = self.env.posicao_y
        dist_tiros = y - self.env.linha_tiros_y
        dist_disc = self._discretizar_distancia_tiros(dist_tiros)
        return (x, y, dist_disc)

    def get_q_valores(self, estado):
        """
        Retorna os valores Q [Q(a0), Q(a1), Q(a2), Q(a3)] para um determinado estado.
        Se o estado for inédito, inicializa com valores otimistas para incentivar o avanço (a0)
        e exploração livre nas laterais, punindo levemente o recuo (a3) por padrão.
        """
        if estado not in self.q_tabela:
            self.q_tabela[estado] = [1.5, 0.5, 0.5, -1.0]
        return self.q_tabela[estado]

    def escolher_acao(self, estado, explorando=True):
        """
        Seleciona a ação usando política epsilon-greedy.
        Quando `explorando=False`, retorna estritamente a melhor ação (explotação/greedy).
        """
        if explorando and random.random() < self.epsilon:
            return random.randint(0, 3)

        q_valores = self.get_q_valores(estado)
        max_q = max(q_valores)

        # Se houver empates entre as melhores ações, escolhe aleatoriamente entre as empatadas
        # Isso garante exploração uniforme entre caminhos de mesmo valor no início do treino
        melhores_acoes = [i for i, q in enumerate(q_valores) if q == max_q]
        return random.choice(melhores_acoes)

    def _calcular_reward_shaping(self, acao, pos_y_anterior, pos_y_atual, recompensa_nativa, recorde_y):
        """
        Aplica o Reward Shaping (reforço heurístico) inteligente para guiar o aprendizado em mapas complexos.
        Mantém as recompensas/penalidades terminais intactas e lapida os passos intermediários.
        """
        # Se for recompensa terminal (Vitória ou Morte/Mina/Tiros) ou bônus de chocolate, mantém a nativa
        if recompensa_nativa == 100 or recompensa_nativa == -100 or recompensa_nativa == 5:
            return recompensa_nativa

        # Se está nas últimas linhas do mapa, incentiva o alinhamento com a coluna central (x=10) onde fica a bandeira
        if pos_y_atual >= self.env.comprimento - 6:
            obj_x = self.env.largura // 2
            x_ant = self.env.posicao_x - (1 if acao == 2 else (-1 if acao == 1 else 0))
            if abs(self.env.posicao_x - obj_x) < abs(x_ant - obj_x):
                return 2.0  # Bônus extra por se alinhar com a coluna do objetivo final

        # Reforço direcional pelo eixo vertical (Y)
        if pos_y_atual > pos_y_anterior:
            return 3.0 if pos_y_atual > recorde_y else 1.0  # Forte incentivo para desbravar e avançar
        elif pos_y_atual < pos_y_anterior:
            return -2.5  # Desincentivo para recuo rumo à enxurrada de tiros
        else:
            return -0.1  # Custo lateral quase neutro, permitindo que contorne minas sem penalidade horizontal artificial

    def treinar_um_episodio(self):
        """
        Executa um único episódio completo de treinamento (do reset até done ou limite de passos).
        Útil para ser acionado sequencialmente no loop da interface gráfica ou em batch.
        """
        self.env.reset()
        estado_atual = self.get_estado()

        pontuacao_total = 0
        recorde_y = self.env.posicao_y
        chegou_objetivo = False

        # Limite de segurança contra loops infinitos em um único episódio
        limite_passos = self.env.comprimento * 3
        passos = 0

        while passos < limite_passos:
            passos += 1
            pos_y_anterior = self.env.posicao_y

            acao = self.escolher_acao(estado_atual, explorando=True)
            _, recompensa_nativa, done, _ = self.env.step(acao)

            pos_y_atual = self.env.posicao_y
            if pos_y_atual > recorde_y:
                recorde_y = pos_y_atual

            recompensa = self._calcular_reward_shaping(
                acao, pos_y_anterior, pos_y_atual, recompensa_nativa, recorde_y
            )
            pontuacao_total += recompensa_nativa  # Armazenamos a pontuação real no histórico

            proximo_estado = self.get_estado()
            q_atual = self.get_q_valores(estado_atual)[acao]

            # Atualização da Tabela Q segundo a Equação de Bellman
            if done:
                alvo = recompensa
                if recompensa_nativa == 100:
                    chegou_objetivo = True
            else:
                max_q_proximo = max(self.get_q_valores(proximo_estado))
                alvo = recompensa + self.gamma * max_q_proximo

            self.q_tabela[estado_atual][acao] += self.alpha * (alvo - q_atual)
            estado_atual = proximo_estado

            if done:
                break

        # Decaimento de epsilon após o término do episódio
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        self.episodio_atual += 1

        dados_episodio = {
            "episodio": self.episodio_atual,
            "dificuldade": self.env.dificuldade,
            "semente_mapa": self.env.seed_atual,
            "pontuacao_real": pontuacao_total,
            "chegou_objetivo": chegou_objetivo,
            "passos": passos,
            "epsilon": round(self.epsilon, 4),
            "max_y_alcançado": recorde_y
        }
        self.historico.append(dados_episodio)

        if self.episodio_atual >= self.episodios_totais:
            self.treinado = True

        return done, dados_episodio

    def treinar(self, num_episodios=None, verbose=True):
        """
        Treina o agente sequencialmente pela quantidade especificada de episódios.
        """
        total = num_episodios if num_episodios is not None else self.episodios_totais
        sucessos = 0

        for ep in range(1, total + 1):
            _, dados = self.treinar_um_episodio()
            if dados["chegou_objetivo"]:
                sucessos += 1

            if verbose and (ep % (total // 10 or 1) == 0 or ep == total):
                taxa = (sucessos / ep) * 100
                print(f"[Q-Learning | {self.env.dificuldade}] Ep {ep}/{total} | "
                      f"Epsilon: {dados['epsilon']} | Max Y: {dados['max_y_alcançado']} | "
                      f"Sucessos acumulados: {taxa:.1f}%")

        self.treinado = True
        return self.historico

    def obter_melhor_acao(self, estado=None):
        """
        Retorna a melhor ação para o estado atual segundo a Tabela Q aprendida (sem exploração).
        Se `estado` não for passado, lê o estado diretamente do ambiente.
        """
        if estado is None:
            estado = self.get_estado()
        return self.escolher_acao(estado, explorando=False)

    def planejar_rota(self):
        """
        Simula a execução determinística (greedy) do agente a partir do início do mapa para extrair
        a rota de ações aprendida. Permite compatibilidade perfeita com a interface e com o main.py
        (similar ao planejar_rota() do AgenteAStar).
        """
        self.env.reset()
        caminho_acoes = []
        estado_atual = self.get_estado()

        limite_passos = self.env.comprimento * 3
        passos = 0

        while passos < limite_passos:
            passos += 1
            acao = self.obter_melhor_acao(estado_atual)
            caminho_acoes.append(acao)

            _, _, done, _ = self.env.step(acao)
            estado_atual = self.get_estado()

            if done:
                break

        return caminho_acoes
