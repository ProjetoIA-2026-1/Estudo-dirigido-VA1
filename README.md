# Resgate no Campo de Batalha: Agentes Inteligentes 🪖

Repositório para o estudo dirigido referente ao conteúdo da primeira VA da disciplina de Inteligência Artificial (2026.1). 

## 🎯 Sobre o Projeto
O projeto consiste na implementação de um ambiente virtual próprio (Contexto I), que simula um campo de batalha onde soldados (agentes) precisam atravessar um terreno hostil para resgatar um companheiro ferido. 

O ambiente apresenta desafios estáticos (minas terrestres e lama), bônus (chocolate para energia) e uma ameaça dinâmica (uma "enxurrada de tiros" que avança a cada turno, forçando o avanço). O terreno possui visibilidade parcial (Névoa de Guerra) para os agentes de aprendizado, exigindo exploração e tomada de decisão sob incerteza.

## 🧠 Paradigmas de IA Implementados
Neste ambiente, comparamos três paradigmas distintos de Inteligência Artificial:
1. **Algoritmo Genético:** Uma população de soldados evolui ao longo de gerações, otimizando suas sequências de movimentos (cromossomos) através de seleção e mutação para maximizar a distância percorrida.
2. **Aprendizado por Reforço (Q-Learning):** Um agente aprende regras de sobrevivência iterativamente por meio de um sistema de recompensas e penalidades, baseando-se apenas em sua visão local do terreno.
3. **Busca Heurística (A*):** O agente determinístico atua como nosso *baseline* (referência matemática ótima), possuindo visão global da matriz para calcular a rota de menor custo antes da execução, utilizando heurística de distância.

## ⚙️ Instalação e Execução

**Pré-requisitos:** Python 3.10 ou superior.

1. Clone o repositório:
\`\`\`bash
git clone https://github.com/seu-usuario/Estudo-dirigido-VA1.git
cd Estudo-dirigido-VA1
\`\`\`

2. Instale as dependências:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. Execute o ambiente de simulação:
\`\`\`bash
# Em breve: comandos para rodar o treinamento e a comparação final
python main.py
\`\`\`