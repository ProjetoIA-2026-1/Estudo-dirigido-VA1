import random
import json
import os


class Individuo:
    def __init__(self, tamanho_cromossomo):
        self.cromossomo = [random.randint(0, 3) for _ in range(tamanho_cromossomo)]
        self.fitness = -9999
        self.chegou_objetivo = False


class AlgoritmoGenetico:
    # Aumentamos a mutação para 8% para evitar que a IA fique estagnada (Plateau)
    def __init__(self, env, tamanho_populacao=150, taxa_mutacao=0.08):
        self.env = env
        self.tamanho_populacao = tamanho_populacao
        self.taxa_mutacao = taxa_mutacao
        self.tamanho_cromossomo = env.comprimento * 2

        self.populacao = []
        self.historico = []
        self.geracoes_consecutivas_vencedoras = 0
        self.geracao_atual = 1

    def inicializar_populacao(self):
        self.populacao = [Individuo(self.tamanho_cromossomo) for _ in range(self.tamanho_populacao)]
        self.historico = []
        self.geracoes_consecutivas_vencedoras = 0
        self.geracao_atual = 1

    def calcular_fitness(self, cromossomo):
        self.env.reset()
        pontuacao_total = 0
        chegou = False

        for acao in cromossomo:
            _, recompensa, done, _ = self.env.step(acao)
            pontuacao_total += recompensa
            if done:
                if recompensa == 100: chegou = True
                break

        avanco = self.env.posicao_y * 10
        fitness = avanco + pontuacao_total

        if chegou: fitness += 1000

        return fitness, chegou

    def treinar_uma_geracao(self, paciencia=5, limiar_sucesso=0.90):
        sucessos = 0
        melhor_individuo = None
        melhor_fitness = -999999

        for ind in self.populacao:
            fit, chegou = self.calcular_fitness(ind.cromossomo)
            ind.fitness = fit
            ind.chegou_objetivo = chegou

            if chegou: sucessos += 1
            if fit > melhor_fitness:
                melhor_fitness = fit
                melhor_individuo = ind

        taxa_sucesso = sucessos / self.tamanho_populacao

        dados_campeao = {
            "geracao": self.geracao_atual,
            "dificuldade": self.env.dificuldade,
            "semente_mapa": self.env.seed_atual,
            "fitness_campeao": melhor_fitness,
            "taxa_sucesso": taxa_sucesso,
            "cromossomo": melhor_individuo.cromossomo
        }
        self.historico.append(dados_campeao)

        terminou = False
        if taxa_sucesso >= limiar_sucesso:
            self.geracoes_consecutivas_vencedoras += 1
        else:
            self.geracoes_consecutivas_vencedoras = 0

        if self.geracoes_consecutivas_vencedoras >= paciencia:
            terminou = True

        if not terminou:
            nova_populacao = [melhor_individuo]

            while len(nova_populacao) < self.tamanho_populacao:
                pai1 = self._selecao_torneio()
                pai2 = self._selecao_torneio()
                filho1, filho2 = self._crossover(pai1, pai2)
                self._mutacao(filho1)
                self._mutacao(filho2)
                nova_populacao.extend([filho1, filho2])

            self.populacao = nova_populacao[:self.tamanho_populacao]
            self.geracao_atual += 1
        else:
            # CORREÇÃO DO JSON: Força a gravação exatamente na mesma pasta deste script
            caminho_arquivo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "historico_ag.json")
            with open(caminho_arquivo, "w") as f:
                json.dump(self.historico, f, indent=4)

        return terminou, dados_campeao

    def _selecao_torneio(self, k=3):
        torneio = random.sample(self.populacao, k)
        return max(torneio, key=lambda ind: ind.fitness)

    def _crossover(self, pai1, pai2):
        ponto = random.randint(1, self.tamanho_cromossomo - 1)
        filho1 = Individuo(self.tamanho_cromossomo)
        filho2 = Individuo(self.tamanho_cromossomo)
        filho1.cromossomo = pai1.cromossomo[:ponto] + pai2.cromossomo[ponto:]
        filho2.cromossomo = pai2.cromossomo[:ponto] + pai1.cromossomo[ponto:]
        return filho1, filho2

    def _mutacao(self, individuo):
        for i in range(self.tamanho_cromossomo):
            if random.random() < self.taxa_mutacao:
                individuo.cromossomo[i] = random.randint(0, 3)