# Guia de Contribuição e Mapeamento do Projeto

Bem-vindo(a) ao repositório do projeto **Resgate Tático: Inteligência Artificial**. 
Nossa arquitetura foi construída seguindo o padrão MVC (Model-View-Controller) para separar a lógica matemática da interface gráfica. 

Use este guia rápido para saber exatamente em qual arquivo e função você deve mexer para alterar parâmetros do jogo, plugar as IAs ou modificar as telas, sem quebrar o resto do sistema.

---

## ⚙️ 1. Ajustes de Balanceamento do Jogo (Model)
Todas as regras de "física", pontuação e geração de mapas estão centralizadas e isoladas no arquivo `environment.py`.

* **Ajustar percentual de Minas, Lama e Chocolates:**
    * **Arquivo:** `environment.py`
    * **Local:** Função `_gerar_mapa(self)` (por volta da linha 32).
    * **O que alterar:** Modifique os valores nas condições `if chance < X:`. Lembre-se que as probabilidades são acumulativas.
* **Alterar a distância inicial da Enxurrada de Tiros (Fôlego Inicial):**
    * **Arquivo:** `environment.py`
    * **Local:** Função `reset(self)` (por volta da linha 52).
    * **O que alterar:** Altere o valor de `self.linha_tiros_y = -8`. (Um número mais negativo dá mais fôlego no início da corrida).
* **Ajustar a Pontuação (Recompensas / Penalidades):**
    * **Arquivo:** `environment.py`
    * **Local:** Final da função `step(self, acao)` (por volta da linha 95).
    * **O que alterar:** Ajuste as variáveis `recompensa = X` para alterar o "Fitness" que os algoritmos de IA vão receber ao pisar em cada terreno.

---

## 🧠 2. Onde Plugar os Agentes de Inteligência Artificial
As classes das IAs não devem ficar misturadas com o ambiente visual.

* **Agente A* (Busca Heurística):**
    * **Arquivo:** `agent_astar.py`
    * *Nota:* O esqueleto da classe já está criado. Ele deve receber a instância de `CampoBatalhaEnv` para conseguir vasculhar a matriz global (`env.mapa_original`).
* **Algoritmo Genético e Q-Learning:**
    * **Arquivos recomendados:** Crie `agent_genetic.py` e `agent_qlearning.py` na raiz do projeto.
    * *Nota:* Eles devem interagir com o ambiente apenas através da função `env.step(acao)`, consumindo a visão parcial (`visao`) e o retorno de `recompensa`.

---

## 🖥️ 3. Modificações Visuais e Telas (View & Controller)
Se precisar criar novos botões, alterar textos, gráficos ou adicionar novas abas no aplicativo, os arquivos responsáveis estão na pasta `interface` e orquestrados pelo `main.py`.

* **Orquestrador de Telas (A Máquina de Estados):**
    * **Arquivo:** `main.py`
    * **Onde mexer:** No laço principal (`while True`), procure pelo roteamento através da variável `estado_atual`. 
* **Criar a Tela Definitiva dos Agentes (Gráficos e Seleção):**
    * **Arquivo:** `main.py`
    * **Local:** Bloco `elif estado_atual == "ESTADO_AGENTES":` (próximo ao fim do arquivo).
    * *O que fazer:* Atualmente, esta tela é apenas um "placeholder" visual. Quando formos plugar as IAs rodando em tempo real, a lógica de chamar a interface de treino deve entrar neste bloco.
* **Ajustar Cores, Fontes e Layout do Painel de Simulação (Lado Direito):**
    * **Arquivo:** `interface/dashboard.py`
    * **Local:** Função `_desenhar_painel` e o `__init__` (para paleta de cores).
* **Adicionar novos botões no Menu Inicial:**
    * **Arquivo:** `interface/menu.py`
    * **Local:** Adicione o botão no dicionário `self.botoes` dentro do `__init__`, e crie a regra de clique na função `processar_eventos`.