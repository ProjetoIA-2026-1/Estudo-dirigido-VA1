import random
import json
import os


class Individuo:
    def __init__(self, tamanho_cromossomo):
        self.cromossomo = [random.randint(0, 3) for _ in range(tamanho_cromossomo)]
        self.fitness = -9999
        self.chegou_objetivo = False
        self.passos_sobrevividos = 0


class AlgoritmoGenetico:
    def __init__(self, env, tamanho_populacao=200):
        self.env = env
        self.tamanho_populacao = tamanho_populacao
        self.tamanho_cromossomo = env.comprimento * 2

        self.populacao = []
        self.historico = []

        self.geracao_atual = 1
        self.geracoes_consecutivas_vencedoras = 0

        # --- MONITORES DE ESTAGNAÇÃO ---
        self.melhor_fitness_global = -999999
        self.geracoes_sem_melhora = 0

    def inicializar_populacao(self):
        self.populacao = [Individuo(self.tamanho_cromossomo) for _ in range(self.tamanho_populacao)]
        self.historico = []
        self.geracoes_consecutivas_vencedoras = 0
        self.geracao_atual = 1
        self.melhor_fitness_global = -999999
        self.geracoes_sem_melhora = 0

    def carregar_checkpoint(self):
        """Lê o último JSON, pega o DNA campeão e inicia uma nova época evolutiva baseada nele."""
        pasta_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(pasta_atual, "historico_ag.json")

        try:
            with open(caminho_arquivo, "r") as f:
                historico_antigo = json.load(f)

            ultimo_campeao = historico_antigo[-1]
            dna_base = ultimo_campeao["cromossomo"]

            self.populacao = []
            campeao = Individuo(self.tamanho_cromossomo)
            campeao.cromossomo = list(dna_base)
            self.populacao.append(campeao)

            # Preenche a população com mutações agressivas do campeão
            while len(self.populacao) < self.tamanho_populacao:
                clone = Individuo(self.tamanho_cromossomo)
                clone.cromossomo = list(dna_base)
                for i in range(self.tamanho_cromossomo):
                    if random.random() < 0.15:  # 15% para quebrar os vícios
                        clone.cromossomo[i] = random.randint(0, 3)
                self.populacao.append(clone)

            self.historico = historico_antigo
            self.geracao_atual = ultimo_campeao["geracao"] + 1
            self.geracoes_consecutivas_vencedoras = 0

            # Reseta os monitores de estagnação do novo ciclo
            self.melhor_fitness_global = ultimo_campeao["fitness_campeao"]
            self.geracoes_sem_melhora = 0

            self.env.seed_atual = ultimo_campeao["semente_mapa"]
            random.seed(self.env.seed_atual)
            print(f"[TRANSFER LEARNING] Sucesso! Iniciando Geração {self.geracao_atual} baseada no Campeão.")
            return True

        except Exception as e:
            print(f"[TRANSFER LEARNING] Falha. Arquivo não encontrado ou corrompido: {e}")
            return False

    def calcular_fitness(self, cromossomo):
        self.env.reset()
        pontuacao_total = 0
        chegou = False
        passos_dados = 0

        for acao in cromossomo:
            passos_dados += 1
            _, recompensa, done, _ = self.env.step(acao)
            pontuacao_total += recompensa
            if done:
                if recompensa == 100: chegou = True
                break

        avanco = self.env.posicao_y * 10
        fitness = avanco + pontuacao_total - (passos_dados * 0.1)

        if chegou: fitness += 1000

        return fitness, chegou, passos_dados

    def treinar_uma_geracao(self, paciencia=5, limiar_sucesso=0.90):
        sucessos = 0
        melhor_individuo = None
        melhor_fitness_geracao = -999999

        # 1. Avaliação
        for ind in self.populacao:
            fit, chegou, passos = self.calcular_fitness(ind.cromossomo)
            ind.fitness = fit
            ind.chegou_objetivo = chegou
            ind.passos_sobrevividos = passos

            if chegou: sucessos += 1
            if fit > melhor_fitness_geracao:
                melhor_fitness_geracao = fit
                melhor_individuo = ind

        taxa_sucesso = sucessos / self.tamanho_populacao

        # --- MONITORAMENTO DE ESTAGNAÇÃO ---
        if melhor_fitness_geracao > self.melhor_fitness_global:
            self.melhor_fitness_global = melhor_fitness_geracao
            self.geracoes_sem_melhora = 0
        else:
            self.geracoes_sem_melhora += 1

        # 2. Persistência
        dados_campeao = {
            "geracao": self.geracao_atual,
            "dificuldade": self.env.dificuldade,
            "semente_mapa": self.env.seed_atual,
            "fitness_campeao": melhor_fitness_geracao,
            "taxa_sucesso": taxa_sucesso,
            "cromossomo": melhor_individuo.cromossomo
        }
        self.historico.append(dados_campeao)

        # 3. Early Stopping
        terminou = False
        if taxa_sucesso >= limiar_sucesso:
            self.geracoes_consecutivas_vencedoras += 1
        else:
            self.geracoes_consecutivas_vencedoras = 0

        if self.geracoes_consecutivas_vencedoras >= paciencia:
            terminou = True

        if not terminou:
            # --- O CATACLISMO (Reinicialização Controlada) ---
            if self.geracoes_sem_melhora >= 40:
                print(
                    f"[GENÉTICO] ☄️ CATACLISMO na Geração {self.geracao_atual}! Platô detectado. Reiniciando diversidade...")
                nova_populacao = [melhor_individuo]  # Elitismo do único sobrevivente
                while len(nova_populacao) < self.tamanho_populacao:
                    nova_populacao.append(Individuo(self.tamanho_cromossomo))
                self.populacao = nova_populacao
                self.geracoes_sem_melhora = 0
                self.geracao_atual += 1
                return terminou, dados_campeao

            # 4. Evolução Normal
            nova_populacao = [melhor_individuo]  # Elitismo moderado

            # Flag de Mutação Adaptativa
            estagnado = self.geracoes_sem_melhora > 15
            if estagnado and self.geracao_atual % 5 == 0:
                print(f"[GENÉTICO] ⚠️ Mutação Adaptativa ativada na geração {self.geracao_atual}.")

            while len(nova_populacao) < self.tamanho_populacao:
                pai1 = self._selecao_torneio()
                pai2 = self._selecao_torneio()
                filho1, filho2 = self._crossover(pai1, pai2)

                media_passos_pais = max(pai1.passos_sobrevividos, pai2.passos_sobrevividos)

                self._mutacao_inteligente(filho1, media_passos_pais, estagnado)
                self._mutacao_inteligente(filho2, media_passos_pais, estagnado)

                nova_populacao.extend([filho1, filho2])

            self.populacao = nova_populacao[:self.tamanho_populacao]
            self.geracao_atual += 1

        return terminou, dados_campeao

    def salvar_historico(self):
        pasta_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(pasta_atual, "historico_ag.json")
        try:
            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                json.dump(self.historico, f, indent=4)
            print(f"\n[SISTEMA] Histórico salvo em:\n -> {caminho_arquivo}\n")
        except Exception as e:
            print(f"\n[SISTEMA] ERRO ao salvar:\n -> {e}\n")

    # --- TÉCNICA: Menor pressão de seleção (k reduzido de 5 para 3) ---
    def _selecao_torneio(self, k=3):
        torneio = random.sample(self.populacao, k)
        return max(torneio, key=lambda ind: ind.fitness)

    # --- TÉCNICA: Cruzamento de 2 Pontos (Maior mistura genética) ---
    def _crossover(self, pai1, pai2):
        pt1 = random.randint(1, self.tamanho_cromossomo - 3)
        pt2 = random.randint(pt1 + 1, self.tamanho_cromossomo - 1)

        filho1 = Individuo(self.tamanho_cromossomo)
        filho2 = Individuo(self.tamanho_cromossomo)

        # DNA Sanduíche
        filho1.cromossomo = pai1.cromossomo[:pt1] + pai2.cromossomo[pt1:pt2] + pai1.cromossomo[pt2:]
        filho2.cromossomo = pai2.cromossomo[:pt1] + pai1.cromossomo[pt1:pt2] + pai2.cromossomo[pt2:]

        return filho1, filho2

    # --- TÉCNICA: Mutação Dinâmica/Adaptativa ---
    def _mutacao_inteligente(self, individuo, passos_seguros, estagnado):
        # Se estagnou, a mutação base sobe 6x (0.06) e o lixo vira puro caos (0.70)
        taxa_base = 0.01 if not estagnado else 0.06
        taxa_lixo = 0.40 if not estagnado else 0.70

        for i in range(self.tamanho_cromossomo):
            if i < passos_seguros - 2:
                if random.random() < taxa_base:
                    individuo.cromossomo[i] = random.randint(0, 3)
            else:
                if random.random() < taxa_lixo:
                    individuo.cromossomo[i] = random.randint(0, 3)