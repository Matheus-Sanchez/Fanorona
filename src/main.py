import pygame
from Tabuleiro import Tabuleiro
from Pecas import GerenciadorPecas
from Movimentacao import Movimentacao
from Captura import Captura
from MiniMax.__main__ import alphabeta  # Importar a função alphabeta
from MiniMax.ia import escolher_movimento_ia
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
    imagem = pygame.image.load("./assets/tutorial.jpg")  # Substitua pelo caminho da imagem
    imagem = pygame.transform.scale(imagem, (800, 500))  # Ajusta o tamanho da imagem
    rodando = True
    while rodando:
        tela.fill((0, 0, 0))
        tela.blit(imagem, (100, 50))
        
        fonte = pygame.font.Font(None, 50)
        texto_voltar = fonte.render("Pressione ESC para voltar", True, (255, 255, 255))
        tela.blit(texto_voltar, (250, 550))
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return  # Volta para o menu

def menu_inicial(tela):
    fonte = pygame.font.Font(None, 74)
    texto_titulo = fonte.render("Jogo de Tabuleiro", True, (255, 255, 255))
    texto_jogar = fonte.render("1 - Jogar (Humano vs Humano)", True, (255, 255, 255))
    texto_ia = fonte.render("2 - Jogar contra IA (MiniMax)", True, (255, 255, 255))
    texto_imagem = fonte.render("3 - Ver Imagem", True, (255, 255, 255))
    texto_sair = fonte.render("4 - Sair", True, (255, 255, 255))

    while True:
        tela.fill((0, 0, 0))
        tela.blit(texto_titulo, (100, 50))
        tela.blit(texto_jogar, (100, 150))
        tela.blit(texto_ia, (100, 250))
        tela.blit(texto_imagem, (100, 350))
        tela.blit(texto_sair, (100, 450))
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
                elif evento.key == pygame.K_3:
                    return "imagem"
                elif evento.key == pygame.K_4:
                    pygame.quit()
                    exit()
                    
def verificar_fim_de_jogo(configuracao):
    pecas_v = sum(linha.count("v") for linha in configuracao)
    pecas_b = sum(linha.count("b") for linha in configuracao)
    if pecas_v == 0:
        return "Jogador B venceu!"
    elif pecas_b == 0:
        return "Jogador V venceu!"
    return None

def desenhar_indicador_turno(tela, jogador_atual, fonte):
    """Desenha um indicador mostrando de quem é o turno atual"""
    texto_turno = fonte.render(f"Turno: Jogador {'Vermelho' if jogador_atual == 'v' else 'Azul'}", True, 
                              (195, 31, 9) if jogador_atual == 'v' else (1, 151, 246))
    tela.blit(texto_turno, (10, 10))  # Posição no canto superior esquerdo


# def desenhar_indicador_captura_cadeia(tela, captura_em_cadeia_ativa, fonte, posicoes_visitadas, ultima_direcao):
#     """Desenha um indicador quando uma captura em cadeia está ativa"""
#     if captura_em_cadeia_ativa:
        # texto_cadeia = fonte.render("Captura em cadeia ativa! Continue capturando.", True, (255, 140, 0))
        # tela.blit(texto_cadeia, (300, 10))  # Posição no topo central
        
        # Exibir restrições atuais
        # if posicoes_visitadas:
            # texto_restricao_posicoes = fonte.render("Não pode visitar pontos já visitados", True, (180, 0, 0))
            # tela.blit(texto_restricao_posicoes, (300, 40))
        
        # if ultima_direcao:
        #     dir_texto = ""
        #     if ultima_direcao == (-1, 0):
        #         dir_texto = "cima"
        #     elif ultima_direcao == (1, 0):
        #         dir_texto = "baixo"
        #     elif ultima_direcao == (0, -1):
        #         dir_texto = "esquerda"
        #     elif ultima_direcao == (0, 1):
        #         dir_texto = "direita"
        #     elif ultima_direcao == (-1, -1):
        #         dir_texto = "diagonal superior esquerda"
        #     elif ultima_direcao == (-1, 1):
        #         dir_texto = "diagonal superior direita"
        #     elif ultima_direcao == (1, -1):
        #         dir_texto = "diagonal inferior esquerda"
        #     elif ultima_direcao == (1, 1):
        #         dir_texto = "diagonal inferior direita"
                
            # texto_restricao_direcao = fonte.render(f"Não pode mover na direção: {dir_texto}", True, (180, 0, 0))
            # tela.blit(texto_restricao_direcao, (300, 70))

def animacao_carregamento(tela, fonte, mensagem="IA pensando..."):
    """Exibe uma animação de carregamento na tela."""
    cores = [(195, 31, 9), (1, 151, 246), (79, 18, 113)]
    posicoes = [(500, 300), (550, 300), (600, 300)]
    indice = 0
    rodando = True
    while rodando:
        tela.fill((217, 217, 217))  # Fundo cinza claro
        texto = fonte.render(mensagem, True, (0, 0, 0))
        tela.blit(texto, (400, 200))  # Mensagem centralizada acima dos círculos

        # Desenhar círculos piscando
        for i, pos in enumerate(posicoes):
            cor = cores[i] if i == indice else (200, 200, 200)
            pygame.draw.circle(tela, cor, pos, 15)
        
        pygame.display.flip()
        indice = (indice + 1) % len(posicoes)  # Alternar entre os círculos
        pygame.time.delay(300)  # Atraso para criar o efeito de animação

        # Verificar eventos para sair da animação
        for evento in pygame.event.get():
            if evento.type == pygame.USEREVENT:  # Evento personalizado para parar a animação
                rodando = False

def animar_movimento(tela, movimentacao, origem, destino, cor, delay=500):
    """
    Anima o movimento de uma peça no tabuleiro.
    :param tela: Tela do pygame.
    :param movimentacao: Objeto Movimentacao para obter posições.
    :param origem: Tupla (linha, coluna) de onde a peça está se movendo.
    :param destino: Tupla (linha, coluna) para onde a peça está se movendo.
    :param cor: Cor da peça para desenhar durante a animação.
    :param delay: Tempo de atraso em milissegundos para a animação.
    """
    linha_origem, coluna_origem = origem
    linha_destino, coluna_destino = destino

    # Coordenadas iniciais e finais
    x_origem = movimentacao.tabuleiro_offset_x + coluna_origem * movimentacao.tamanho_celula + movimentacao.tamanho_celula // 2
    y_origem = movimentacao.tabuleiro_offset_y + linha_origem * movimentacao.tamanho_celula + movimentacao.tamanho_celula // 2
    x_destino = movimentacao.tabuleiro_offset_x + coluna_destino * movimentacao.tamanho_celula + movimentacao.tamanho_celula // 2
    y_destino = movimentacao.tabuleiro_offset_y + linha_destino * movimentacao.tamanho_celula + movimentacao.tamanho_celula // 2

    # Número de quadros para a animação
    passos = 16
    for i in range(passos + 1):
        # Interpolação linear para calcular a posição intermediária
        x_atual = x_origem + (x_destino - x_origem) * i / passos
        y_atual = y_origem + (y_destino - y_origem) * i / passos

        # Redesenhar o tabuleiro e as peças
        tela.fill((255, 255, 255))  # Fundo branco
        movimentacao.captura_ref.tabuleiro.desenhar(tela)
        movimentacao.gerenciador_pecas.desenhar_pecas(tela)

        # Desenhar a peça em movimento
        pygame.draw.circle(tela, cor, (int(x_atual), int(y_atual)), movimentacao.tamanho_celula // 3)

        pygame.display.flip()
        pygame.time.delay(delay // passos)  # Atraso entre os quadros

def main():
    pygame.init()
    largura, altura = 1000, 600
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Fanorona")
    fonte = pygame.font.Font(None, 36)
    fonte_grande = pygame.font.Font(None, 50)
    
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
            desenhar_indicador_turno(tela, jogador_atual, fonte)
            
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
        
        # Mostrar mensagem de vencedor
        if mensagem_vencedor:
            texto_vencedor = fonte_grande.render(mensagem_vencedor, True, (255, 0, 0))
            tela.blit(texto_vencedor, (largura // 2 - texto_vencedor.get_width() // 2, 20))
        

        
        if modo_ia and mensagem_vencedor is None \
           and jogador_atual == IA_PLAYER \
           and not captura.escolha_captura_ativa \
           and not captura.captura_em_cadeia_ativa:
            while True:  # Loop to handle chain captures
                # Exibir animação de carregamento em uma thread separada
                pygame.time.set_timer(pygame.USEREVENT, 0)  # Garantir que o evento não seja disparado antes
                threading.Thread(target=animacao_carregamento, args=(tela, fonte)).start()

                # Copiar estado lógico (v, b ou -)
                estado_ia = [list(l) for l in configuracao_inicial]
                print("IA está avaliando o estado atual...")  # Atualização no terminal

                melhor_jogada = escolher_movimento_ia(estado_ia, IA_PLAYER, profundidade=4, alphabeta_func=alphabeta)

                # Parar a animação de carregamento
                pygame.event.post(pygame.event.Event(pygame.USEREVENT))  # Enviar evento para parar a animação

                if melhor_jogada:
                    (i1, j1), (i2, j2) = melhor_jogada
                    print(f"IA escolheu mover de ({i1}, {j1}) para ({i2}, {j2}).")  # Atualização no terminal

                    # Animação do movimento da IA
                    cor_peca = (195, 31, 9) if IA_PLAYER == "v" else (1, 151, 246)
                    animar_movimento(tela, movimentacao, (i1, j1), (i2, j2), cor_peca)

                    # Preparar o movimento na camada de lógica + GUI
                    movimentacao.peca_selecionada = (i1, j1)
                    movimentacao.movimentos_possiveis = [(i2, j2)]
                    movimentacao.mover_peca(i2, j2, IA_PLAYER)
                    movimentacao.limpar_selecao()  # Evita peças "presas" selecionadas

                    # Atualizar a configuração inicial para refletir o movimento
                    configuracao_inicial[i1][j1] = "-"
                    configuracao_inicial[i2][j2] = IA_PLAYER

                    # Verificar se há uma captura em cadeia disponível
                    if captura.existe_captura_geral(IA_PLAYER, (i2, j2)):
                        print("IA encontrou uma captura em cadeia. Continuando...")
                        continue  # Continuar o loop para realizar a captura em cadeia
                    else:
                        break  # Sair do loop se não houver mais capturas em cadeia
                else:
                    # Sem jogadas possíveis → declare fim ou passe o turno
                    resultado = verificar_fim_de_jogo(configuracao_inicial)
                    if resultado:
                        mensagem_vencedor = resultado
                    break  # Sair do loop se não houver jogadas possíveis

            # Trocar turno para o jogador humano
            jogador_atual = HUMANO_PLAYER
    
        pygame.display.flip()  
              
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif not mensagem_vencedor:  # Bloqueia interação após o fim do jogo
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    x, y = evento.pos
                    if captura.escolha_captura_ativa:
                        if captura.processar_clique_botoes(x, y):
                            if not captura.captura_em_cadeia_ativa:
                                jogador_atual = "b" if jogador_atual == "v" else "v"
                    else:
                        movimento_realizado = movimentacao.processar_clique(x, y, jogador_atual)
                        if movimento_realizado and not captura.captura_em_cadeia_ativa and not captura.escolha_captura_ativa:
                            jogador_atual = "b" if jogador_atual == "v" else "v"
                        elif evento.type == pygame.KEYDOWN:
                            movimentacao.processar_eventos(evento)
                
    pygame.quit()

if __name__ == "__main__":
    main()