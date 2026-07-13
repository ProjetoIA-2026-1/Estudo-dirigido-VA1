import pygame
import sys
from environment import CampoBatalhaEnv
from interface.dashboard import Dashboard


def main():
    # Instancia a Regra de Negócio (Model)
    env = CampoBatalhaEnv()
    env.reset()

    # Instancia a Interface Gráfica (View)
    dashboard = Dashboard()

    # Variáveis de Controle
    pontuacao = 0
    status = "Correndo"
    acao_str = "Aguardando..."

    rodando = True
    while rodando:
        pygame.time.Clock().tick(30)

        tomou_acao = False
        acao = -1

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            if evento.type == pygame.KEYDOWN:
                # Se o jogo acabou, só permite apertar R para reiniciar
                if status != "Correndo" and evento.key != pygame.K_r:
                    continue

                    # Mapeamento do Controle Humano
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
                elif evento.key == pygame.K_r:
                    env.reset()
                    pontuacao = 0
                    status = "Correndo"
                    acao_str = "Nova Simulação"

        # Atualiza o motor lógico se uma ação foi tomada
        if tomou_acao and status == "Correndo":
            _, recompensa, done, _ = env.step(acao)
            pontuacao += recompensa

            if done:
                status = "VITÓRIA!" if recompensa == 100 else "GAME OVER"

        # Manda a interface renderizar o estado atual
        dashboard.renderizar_frame(env, pontuacao, acao_str, status)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()