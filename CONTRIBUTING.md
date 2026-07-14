# Guia de Contribuição e Mapeamento do Projeto

Bem-vindo(a) ao repositório do projeto **Resgate Tático: Inteligência Artificial**. 
Nossa arquitetura foi construída seguindo o padrão MVC (Model-View-Controller) para separar a lógica matemática da interface gráfica, garantindo um código limpo e modular.

Use este guia rápido para saber exatamente em qual arquivo e função você deve mexer para alterar parâmetros do jogo, plugar as IAs ou modificar as telas, sem quebrar o resto do sistema.

---

## ⚙️ 1. Ajustes de Balanceamento do Jogo (Model)
Todas as regras de "física", pontuação e geração de mapas estão centralizadas e isoladas no arquivo `environment.py`.

* **Ajustar Dificuldades (Tamanho, Minas, Lama e Fôlego):**
    * **Arquivo:** `environment.py`
    * **Local:** Dicionário `self.configs` dentro da função `__init__`.
    * **O que alterar:** Você pode alterar livremente os valores decimais. Eles representam **probabilidades reais** (ex: `0.10` é rigorosamente 10% do mapa). O `tiros_y` define a distância inicial da ameaça (valores mais negativos = mais fôlego inicial), e o `comprimento` define o tamanho do mapa.
* **Lógica do Caminho Dourado (Golden Path):**
    * **Arquivo:** `environment.py`
    * **Local:** Funções `_gerar_caminho_dourado` e `_gerar_golden_path`.
    * **O que alterar:** Modifique a taxa de curvas ou a distância segura que aciona a plantação de "chocolates salvadores" automáticos.
* **Ajustar a Pontuação (Recompensas / Penalidades):**
    * **Arquivo:** `environment.py`
    * **Local:** Final da função `step(self, acao)`.
    * **O que alterar:** Ajuste as variáveis `recompensa = X` para alterar o "Fitness" que os algoritmos de IA vão receber ao pisar em cada terreno.

---

## 🧠 2. Onde Plugar os Agentes de Inteligência Artificial
As classes das IAs não devem ficar misturadas com o ambiente visual.

* **Agente A* (Busca Heurística e Juiz):**
    * **Arquivo:** `agent_astar.py`
    * *Nota:* Completamente implementado. Ele vasculha a `env.mapa_original` para encontrar a rota matemática perfeita. Também é importado internamente pelo `environment.py` para validar a possibilidade dos mapas procedurais antes de o jogo começar.
* **Algoritmo Genético e Q-Learning:**
    * **Arquivos recomendados:** Crie `agent_genetic.py` e `agent_qlearning.py` na raiz do projeto.
    * *Nota:* Ao contrário do A*, estas abordagens são "cegas". Elas devem interagir com o ambiente estritamente através da função `env.step(acao)`, consumindo a visão parcial (`visao`) e o retorno de `recompensa` para evoluir.

---

## 🖥️ 3. Modificações Visuais e Telas (View & Controller)
Se precisar criar novos botões, alterar textos, gráficos ou adicionar novas abas no aplicativo, os arquivos responsáveis estão na pasta `interface` e orquestrados pelo `main.py`.

* **Orquestrador de Telas (A Máquina de Estados):**
    * **Arquivo:** `main.py`
    * **Onde mexer:** No laço principal (`while True`), a variável `estado_atual` roteia o sistema entre: Menu -> Seleção de Agente -> Seleção de Dificuldade -> Simulação (Manual ou IA).
* **Adicionar novos botões e Telas do Menu Inicial:**
    * **Arquivo:** `interface/menu.py`
    * **Onde mexer:** Crie os botões nos dicionários dentro do `__init__` e implemente a lógica de colisão e renderização nas funções respectivas (ex: `processar_eventos_agentes` e `desenhar_agentes`).
* **Ajustar Cores, Fontes e Layout do Painel de Simulação (Lado Direito):**
    * **Arquivo:** `interface/dashboard.py`
    * **Onde mexer:** * Cores base estão no `__init__`.
        * O painel lateral e a telemetria são desenhados em `_desenhar_painel`.
        * A renderização dinâmica (que altera as dicas do rodapé de acordo com o modo Manual ou IA) é processada recebendo a flag `modo`.