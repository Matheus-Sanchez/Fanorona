import pygame
from Tabuleiro import Tabuleiro
from Pecas import GerenciadorPecas
from Movimentacao import Movimentacao
from Captura import Captura
from MiniMax.ia import escolher_movimento_ia
from MiniMax.gerador_movimentos import aplicar_movimento  # <-- ADICIONE ESTA LINHA
from MiniMax.config import IA_PLAYER, HUMANO_PLAYER
from concurrent.futures import ThreadPoolExecutor
import threading

# paleta de cores 
# preto licorice (17, 4, 3)
# fundo (217, 217, 217)
# jogador azul (1, 151, 246)
# jogador vermelho (195, 31, 9)
# borda de seleção (79, 18, 113)
# borda selecionado (243, 232, 238)


def exibir_imagem(tela):
    imagem = pygame.image.load("./assets/2.png")  # Substitua pelo caminho da imagem
    imagem = pygame.transform.scale(imagem, (800, 500))  # Ajusta o tamanho da imagem
    rodando = True
    while rodando:
        tela.fill((0, 0, 0))
        tela.blit(imagem, (100, 50))
        
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return  # Volta para o menu

def menu_inicial(tela):
    imagem = pygame.image.load("./assets/1.png")  # Substitua pelo caminho da imagem
    imagem = pygame.transform.scale(imagem, (1000, 600))  # Ajusta o tamanho da imagem

    while True:
        tela.fill((0, 0, 0))
        tela.blit(imagem, (0, 0))

        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    return "jogar"
                elif evento.key == pygame.K_2:
                    return "ia"
                elif evento.key == pygame.K_5:
                    return "imagem"
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    
def verificar_fim_de_jogo(configuracao):
    pecas_v = sum(linha.count("v") for linha in configuracao)
    pecas_b = sum(linha.count("b") for linha in configuracao)
    if pecas_v == 0:
        return "Jogador B venceu!"
    elif pecas_b == 0:
        return "Jogador V venceu!"
    return None

# --- Substituir o indicador de turno ---
def desenhar_indicador_turno(tela, jogador_atual, fonte, ia_pensando, ia_frame):
    cor = (195, 31, 9) if jogador_atual == 'v' else (1, 151, 246)
    texto = "Turno: Jogador Vermelho -> IA pensando..." if modo_ia and jogador_atual == IA_PLAYER and ia_pensando else \
            f"Turno: Jogador {'Vermelho' if jogador_atual == 'v' else 'Azul'}"
    texto_turno = fonte.render(texto, True, cor)
    tela.blit(texto_turno, (10, 10))

    if jogador_atual == IA_PLAYER and ia_pensando:
        base_x = texto_turno.get_width() + 20
        for i in range(3):
            raio = 4
            x = 10 + base_x + i * 20
            y = 10 + texto_turno.get_height() // 2
            ativo = (ia_frame // 10) % 3 == i
            cor_ponto = cor if ativo else (180, 180, 180)
            pygame.draw.circle(tela, cor_ponto, (x, y), raio)



def animar_movimento(tela, movimentacao, origem, destino, cor, tabuleiro, pecas, delay=500):
    """
    Anima o movimento de uma peça no tabuleiro.
    """
    linha_origem, coluna_origem = origem
    linha_destino, coluna_destino = destino

    x_origem = movimentacao.tabuleiro_offset_x + coluna_origem * movimentacao.tamanho_celula + movimentacao.tamanho_celula // 2
    y_origem = movimentacao.tabuleiro_offset_y + linha_origem * movimentacao.tamanho_celula + movimentacao.tamanho_celula // 2
    x_destino = movimentacao.tabuleiro_offset_x + coluna_destino * movimentacao.tamanho_celula + movimentacao.tamanho_celula // 2
    y_destino = movimentacao.tabuleiro_offset_y + linha_destino * movimentacao.tamanho_celula + movimentacao.tamanho_celula // 2

    passos = 24
    for i in range(passos + 1):
        x_atual = x_origem + (x_destino - x_origem) * i / passos
        y_atual = y_origem + (y_destino - y_origem) * i / passos

        tela.fill((255, 255, 255))
        tabuleiro.desenhar(tela)
        pecas.desenhar_pecas(tela)

        pygame.draw.circle(tela, cor, (int(x_atual), int(y_atual)), movimentacao.tamanho_celula // 3)

        pygame.display.flip()
        pygame.time.delay(delay // passos)


def main():
    pygame.init()
    largura, altura = 1000, 600
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Fanorona")
    fonte = pygame.font.Font(None, 36)
    fonte_grande = pygame.font.Font(None, 50)
    
    global modo_ia # Adicionar para que desenhar_indicador_turno possa acessá-lo
    modo_ia = False # Inicializar modo_ia como False
    
    while True:
        escolha = menu_inicial(tela)
        if escolha == "imagem":
            exibir_imagem(tela)
        elif escolha == "sair":
            return
        elif escolha in ("jogar", "ia"):
            modo_ia = (escolha == "ia")
            break
    
    # Inicia o jogo normalmente
    configuracao_inicial = [
        ["v", "v", "v", "v", "v", "v", "v", "v", "v"],
        ["v", "v", "v", "v", "v", "v", "v", "v", "v"],
        ["v", "b", "v", "b", "-", "v", "b", "v", "b"],
        ["b", "b", "b", "b", "b", "b", "b", "b", "b"],
        ["b", "b", "b", "b", "b", "b", "b", "b", "b"]
    ]
    
    # Inicialização dos componentes do jogo
    tabuleiro = Tabuleiro(largura, altura)
    pecas = GerenciadorPecas(5, 9, 100, (largura - 900) // 2, (altura - 500) // 2, configuracao_inicial)
    captura = Captura(5, 9, 100, (largura - 900) // 2, (altura - 500) // 2, configuracao_inicial)
    movimentacao = Movimentacao(5, 9, 100, (largura - 900) // 2, (altura - 500) // 2, pecas, configuracao_inicial)
    
    # Configurar referências cruzadas
    captura.set_gerenciador_pecas(pecas)
    captura.set_tabuleiro(tabuleiro)  # Configurar referência ao tabuleiro
    movimentacao.set_captura_ref(captura)
    
    # Inicializar o jogador atual (v = vermelho começa)
    jogador_atual = "v"
    
    mensagem_vencedor = None
    rodando = True
    ia_pensando = False  # Inicializar ia_pensando
    ia_frame = 0
    clock = pygame.time.Clock() 

    # *** CORREÇÃO DO ERRO UnboundLocalError ***
    # A variável 'depth' precisa ser definida antes do loop principal do jogo.
    depth = 4 
    
    while rodando:
        tela.fill((255, 255, 255))
        tabuleiro.desenhar(tela)
        pecas.desenhar_pecas(tela)
        movimentacao.desenhar_movimentos(tela)
  
        # Se houver alguma captura disponível para o jogador atual, destaca as peças elegíveis
        if movimentacao.captura_ref and movimentacao.existe_captura_geral(jogador_atual):
            movimentacao.destacar_pecas_com_captura(tela, jogador_atual)
        
        movimentacao.desenhar_movimentos(tela)

        # Desenhar a borda de seleção se uma peça estiver selecionada
        if movimentacao.peca_selecionada:
            movimentacao.desenhar_borda_selecao(tela)
        
        # Mostrar botões de captura se necessário
        if captura.escolha_captura_ativa:
            captura.desenhar_botoes_captura(tela)
        
        # Desenhar posições já visitadas durante uma captura em cadeia
        if captura.captura_em_cadeia_ativa and captura.posicoes_visitadas:
            for posicao in captura.posicoes_visitadas:
                linha, coluna = posicao
                pos_x = captura.offset_x + (coluna * captura.tamanho_celula) + captura.tamanho_celula // 2
                pos_y = captura.offset_y + (linha * captura.tamanho_celula) + captura.tamanho_celula // 2
                # Desenhar um círculo semitransparente para indicar posições já visitadas
                pygame.draw.circle(tela, (100, 100, 100, 128), (pos_x, pos_y), 10)
        
        # Mostrar indicador de turno
        if not mensagem_vencedor:
            desenhar_indicador_turno(tela, jogador_atual, fonte, ia_pensando, ia_frame)
            
            # # Mostrar indicador de captura em cadeia se ativo
            # if captura.captura_em_cadeia:
            #     desenhar_indicador_captura_cadeia(tela, 
            #                                    captura.captura_em_cadeia_ativa, 
            #                                    fonte, 
            #                                    captura.posicoes_visitadas, 
            #                                    captura.ultima_direcao)
        
        # Verificar fim de jogo
        if not mensagem_vencedor:
            resultado = verificar_fim_de_jogo(configuracao_inicial)
            if resultado:
                mensagem_vencedor = resultado
                print(f"Fim de jogo: {mensagem_vencedor}")  # Debug

        # Mostrar mensagem de vencedor
        if mensagem_vencedor:
            texto_vencedor = fonte_grande.render(mensagem_vencedor, True, (255, 0, 0))
            tela.blit(texto_vencedor, (largura // 2 - texto_vencedor.get_width() // 2, 20))
            pygame.display.flip()
            pygame.time.delay(3000)  # Esperar 3 segundos antes de encerrar
            rodando = False  # Encerrar o jogo após exibir a mensagem
            continue  # Sair do loop atual para evitar mais lógica

        if modo_ia and not mensagem_vencedor and jogador_atual == IA_PLAYER and not ia_pensando:
            if not captura.escolha_captura_ativa and not captura.captura_em_cadeia_ativa:
                ia_pensando = True  # IA começa a pensar
                ia_frame_count = 0

                # Mostrar "IA pensando..." com animação antes de calcular a jogada
                for _ in range(30):  # Exibir animação por um curto período
                    tela.fill((255, 255, 255))
                    tabuleiro.desenhar(tela)
                    pecas.desenhar_pecas(tela)
                    movimentacao.desenhar_movimentos(tela)
                    if movimentacao.captura_ref and movimentacao.existe_captura_geral(jogador_atual):
                        movimentacao.destacar_pecas_com_captura(tela, jogador_atual)
                    if movimentacao.peca_selecionada:
                        movimentacao.desenhar_borda_selecao(tela)
                    if captura.escolha_captura_ativa:
                        captura.desenhar_botoes_captura(tela)
                    if captura.captura_em_cadeia_ativa and captura.posicoes_visitadas:
                        for posicao in captura.posicoes_visitadas:
                            linha, coluna = posicao
                            pos_x = captura.offset_x + (coluna * captura.tamanho_celula) + captura.tamanho_celula // 2
                            pos_y = captura.offset_y + (linha * captura.tamanho_celula) + captura.tamanho_celula // 2
                            pygame.draw.circle(tela, (100, 100, 100, 128), (pos_x, pos_y), 10)
                    desenhar_indicador_turno(tela, jogador_atual, fonte, ia_pensando, ia_frame)
                    pygame.display.flip()
                    ia_frame += 1
                    pygame.time.delay(100)  # Pequeno atraso para a animação

                # Calcular a jogada da IA
                estado_ia = [list(l) for l in configuracao_inicial]
                print("IA está avaliando o estado atual...")  # Debug

                melhor_jogada = escolher_movimento_ia(estado_ia, IA_PLAYER, depth)
                ia_pensando = False  # IA terminou de pensar

                if melhor_jogada:
                    print(f"IA escolheu o movimento: {melhor_jogada}")
                    cor_peca = (195, 31, 9) if IA_PLAYER == "v" else (1, 151, 246)
                    for i in range(len(melhor_jogada) - 1):
                        origem = melhor_jogada[i]
                        destino = melhor_jogada[i+1]
                        animar_movimento(tela, movimentacao, origem, destino, cor_peca, tabuleiro, pecas)
                        movimentacao.peca_selecionada = origem
                        movimentacao.movimentos_possiveis = [destino]
                        movimentacao.mover_peca(destino[0], destino[1], IA_PLAYER)
                    movimentacao.limpar_selecao()
                    if captura.captura_em_cadeia_ativa or captura.escolha_captura_ativa:
                        captura.finalizar_cadeia_captura()
                    jogador_atual = HUMANO_PLAYER
                    print(f"Turno do jogador humano: {jogador_atual}")
                else:
                    # Verifica se realmente não há nenhum movimento possível para a IA
                    from MiniMax.gerador_movimentos import generate_moves
                    movimentos_possiveis = generate_moves(estado_ia, IA_PLAYER)
                    if movimentos_possiveis:
                        # Força a IA a jogar o primeiro movimento possível
                        print("IA não encontrou jogada ótima, mas ainda há movimentos possíveis. Forçando o primeiro movimento legal.")
                        melhor_jogada = movimentos_possiveis[0]
                        cor_peca = (195, 31, 9) if IA_PLAYER == "v" else (1, 151, 246)
                        for i in range(len(melhor_jogada) - 1):
                            origem = melhor_jogada[i]
                            destino = melhor_jogada[i+1]
                            animar_movimento(tela, movimentacao, origem, destino, cor_peca, tabuleiro, pecas)
                            movimentacao.peca_selecionada = origem
                            movimentacao.movimentos_possiveis = [destino]
                            movimentacao.mover_peca(destino[0], destino[1], IA_PLAYER)
                        movimentacao.limpar_selecao()
                        if captura.captura_em_cadeia_ativa or captura.escolha_captura_ativa:
                            captura.finalizar_cadeia_captura()
                        jogador_atual = HUMANO_PLAYER
                        print(f"Turno do jogador humano: {jogador_atual}")
                    else:
                        print("IA não encontrou jogadas possíveis.")
                        mensagem_vencedor = "Jogador Humano venceu! (IA ficou sem movimentos)"
                        print(f"Fim de jogo: {mensagem_vencedor}")
                        pygame.display.flip()
                        pygame.time.delay(3000)
                        rodando = False
                        continue

            # Trocar turno para o jogador humano
            jogador_atual = HUMANO_PLAYER
            print(f"Turno do jogador humano: {jogador_atual}")  # Debug

        pygame.display.flip()
        ia_frame += 1  # Incrementar para animação dos pontos

        # Verificar eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                print("Jogo encerrado pelo usuário.")  # Debug
                rodando = False
            elif not mensagem_vencedor:  # Bloqueia interação após o fim do jogo
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    x, y = evento.pos
                    if captura.escolha_captura_ativa:
                        if captura.processar_clique_botoes(x, y):
                            if not captura.captura_em_cadeia_ativa:
                                jogador_atual = "b" if jogador_atual == "v" else "v"
                                print(f"Turno trocado para: {jogador_atual}")  # Debug
                    else:
                        movimento_realizado = movimentacao.processar_clique(x, y, jogador_atual)
                        if movimento_realizado and not captura.captura_em_cadeia_ativa and not captura.escolha_captura_ativa:
                            jogador_atual = "b" if jogador_atual == "v" else "v"
                            print(f"Turno trocado para: {jogador_atual}")  # Debug
                        elif evento.type == pygame.KEYDOWN:
                            movimentacao.processar_eventos(evento)

    print("Jogo encerrado.")  # Debug
    pygame.quit()

if __name__ == "__main__":
    main()