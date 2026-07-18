import random
import json
import os
import numpy as np


class Individuo:
    def __init__(self, tamanho_cromossomo):
        self.cromossomo = [random.uniform(-1.0, 1.0) for _ in range(tamanho_cromossomo)]
        self.fitness = -9999
        self.chegou_objetivo = False
        self.passos_sobrevividos = 0


class AlgoritmoGenetico:
    def __init__(self, env, tamanho_populacao=150):
        self.env = env
        self.tamanho_populacao = tamanho_populacao

        self.num_inputs = 10
        self.num_acoes = 4
        self.tamanho_cromossomo = self.num_inputs * self.num_acoes

        self.populacao = []
        self.historico = []

        self.geracao_atual = 1
        self.geracoes_consecutivas_vencedoras = 0

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
        pasta_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(pasta_atual, "historico_ag.json")

        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                historico_antigo = json.load(f)

            if not historico_antigo:
                return False

            ultimo_campeao = historico_antigo[-1]
            dna_base = ultimo_campeao["cromossomo"]

            if len(dna_base) != self.tamanho_cromossomo:
                print(
                    f"[SISTEMA] Arquitetura neural alterada (de {len(dna_base)} para {self.tamanho_cromossomo} genes). O Checkpoint antigo será ignorado.")
                return False

            self.populacao = []
            campeao = Individuo(self.tamanho_cromossomo)
            campeao.cromossomo = list(dna_base)
            self.populacao.append(campeao)

            while len(self.populacao) < self.tamanho_populacao:
                clone = Individuo(self.tamanho_cromossomo)
                clone.cromossomo = list(dna_base)
                for i in range(self.tamanho_cromossomo):
                    if random.random() < 0.20:
                        clone.cromossomo[i] += random.gauss(0, 0.2)
                        clone.cromossomo[i] = max(-1.0, min(1.0, clone.cromossomo[i]))
                self.populacao.append(clone)

            self.historico = historico_antigo
            self.geracao_atual = ultimo_campeao["geracao"] + 1
            self.geracoes_consecutivas_vencedoras = 0
            self.melhor_fitness_global = ultimo_campeao["fitness_campeao"]
            self.geracoes_sem_melhora = 0

            self.env.seed_atual = ultimo_campeao["semente_mapa"]
            random.seed(self.env.seed_atual)
            print(f"[TRANSFER LEARNING] Sucesso! Continuando a partir da Geração {self.geracao_atual}.")
            return True

        except Exception as e:
            print(f"[TRANSFER LEARNING] Falha ao carregar: {e}")
            return False

    def _decidir_acao(self, pesos, visao_local, dist_fogo):
        norte_oeste = visao_local[1][1]
        norte = visao_local[1][2]
        norte_leste = visao_local[1][3]
        oeste = visao_local[2][1]
        leste = visao_local[2][3]
        sul_oeste = visao_local[3][1]
        sul = visao_local[3][2]
        sul_leste = visao_local[3][3]

        inputs = np.array([
            norte / 4.0, sul / 4.0, leste / 4.0, oeste / 4.0,
            norte_oeste / 4.0, norte_leste / 4.0, sul_oeste / 4.0, sul_leste / 4.0,
            (self.env.comprimento - 1 - self.env.posicao_y) / float(self.env.comprimento),
            min(15.0, dist_fogo) / 15.0
        ])

        matriz_pesos = np.array(pesos).reshape(self.num_inputs, self.num_acoes)
        outputs = np.dot(inputs, matriz_pesos)

        return int(np.argmax(outputs))

    def calcular_fitness(self, cromossomo):
        visao_local, dist_fogo = self.env.reset()
        pontuacao_total = 0
        chegou = False
        passos_dados = 0

        limite_passos = self.env.comprimento * 4

        while passos_dados < limite_passos:
            passos_dados += 1
            acao = self._decidir_acao(cromossomo, visao_local, dist_fogo)

            # Atualiza o estado
            estado_env, recompensa, done, info = self.env.step(acao)
            visao_local, dist_fogo = estado_env

            pontuacao_total += recompensa

            if done:
                if recompensa == 100:
                    chegou = True
                break

        avanco = self.env.posicao_y * 20
        fitness = avanco + pontuacao_total - (passos_dados * 0.5)

        if chegou:
            fitness += 3000

        return fitness, chegou, passos_dados

    def treinar_uma_geracao(self, paciencia=5, limiar_sucesso=0.85):
        sucessos = 0
        melhor_individuo = None
        melhor_fitness_geracao = -999999

        for ind in self.populacao:
            fit, chegou, passos = self.calcular_fitness(ind.cromossomo)
            ind.fitness = fit
            ind.chegou_objetivo = chegou
            ind.passos_sobrevividos = passos

            if chegou:
                sucessos += 1
            if fit > melhor_fitness_geracao:
                melhor_fitness_geracao = fit
                melhor_individuo = ind

        taxa_sucesso = sucessos / self.tamanho_populacao

        if melhor_fitness_geracao > self.melhor_fitness_global:
            self.melhor_fitness_global = melhor_fitness_geracao
            self.geracoes_sem_melhora = 0
        else:
            # --- CORREÇÃO DA SÍNDROME DO GÊNIO ---
            # Se ele chegou no objetivo, ele já venceu! Não precisa estressar o algoritmo.
            if melhor_individuo.chegou_objetivo:
                self.geracoes_sem_melhora = 0
            else:
                self.geracoes_sem_melhora += 1

        dados_campeao = {
            "geracao": self.geracao_atual,
            "dificuldade": self.env.dificuldade,
            "semente_mapa": self.env.seed_atual,
            "fitness_campeao": melhor_fitness_geracao,
            "taxa_sucesso": taxa_sucesso,
            "cromossomo": melhor_individuo.cromossomo
        }
        self.historico.append(dados_campeao)

        terminou = False
        if taxa_sucesso >= limiar_sucesso:
            self.geracoes_consecutivas_vencedoras += 1
        else:
            self.geracoes_consecutivas_vencedoras = 0

        # Se ele for consistente na vitória, o treinamento para automaticamente!
        if self.geracoes_consecutivas_vencedoras >= paciencia:
            terminou = True

        if not terminou:
            if self.geracoes_sem_melhora >= 40:
                print(f"[GENÉTICO] ☄️ CATACLISMO na Geração {self.geracao_atual}! Reiniciando diversidade de pesos...")
                nova_populacao = [melhor_individuo]
                while len(nova_populacao) < self.tamanho_populacao:
                    nova_populacao.append(Individuo(self.tamanho_cromossomo))
                self.populacao = nova_populacao
                self.geracoes_sem_melhora = 0
                self.geracao_atual += 1
                return terminou, dados_campeao

            nova_populacao = [melhor_individuo]
            estagnado = self.geracoes_sem_melhora > 15

            while len(nova_populacao) < self.tamanho_populacao:
                pai1 = self._selecao_torneio()
                pai2 = self._selecao_torneio()
                filho1, filho2 = self._crossover(pai1, pai2)

                self._mutacao_pesos(filho1, estagnado)
                self._mutacao_pesos(filho2, estagnado)

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

    def _selecao_torneio(self, k=3):
        torneio = random.sample(self.populacao, k)
        return max(torneio, key=lambda ind: ind.fitness)

    def _crossover(self, pai1, pai2):
        pt = random.randint(1, self.tamanho_cromossomo - 1)
        filho1 = Individuo(self.tamanho_cromossomo)
        filho2 = Individuo(self.tamanho_cromossomo)

        filho1.cromossomo = pai1.cromossomo[:pt] + pai2.cromossomo[pt:]
        filho2.cromossomo = pai2.cromossomo[:pt] + pai1.cromossomo[pt:]
        return filho1, filho2

    def _mutacao_pesos(self, individuo, estagnado):
        sigma = 0.1 if not estagnado else 0.4
        taxa_mutacao = 0.05 if not estagnado else 0.25

        for i in range(self.tamanho_cromossomo):
            if random.random() < taxa_mutacao:
                individuo.cromossomo[i] += random.gauss(0, sigma)
                individuo.cromossomo[i] = max(-1.0, min(1.0, individuo.cromossomo[i]))