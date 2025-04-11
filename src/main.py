import pygame
from Tabuleiro import Tabuleiro
from Pecas import GerenciadorPecas
from Movimentacao import Movimentacao
from Captura import Captura

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
    texto_jogar = fonte.render("1 - Jogar", True, (255, 255, 255))
    texto_imagem = fonte.render("2 - Ver Imagem", True, (255, 255, 255))
    texto_sair = fonte.render("3 - Sair", True, (255, 255, 255))

    rodando = True
    while rodando:
        tela.fill((0, 0, 0))
        tela.blit(texto_titulo, (150, 100))
        tela.blit(texto_jogar, (200, 250))
        tela.blit(texto_imagem, (200, 350))
        tela.blit(texto_sair, (200, 450))
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    return "jogar"
                elif evento.key == pygame.K_2:
                    return "imagem"
                elif evento.key == pygame.K_3:
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
                              (219, 55, 99) if jogador_atual == 'v' else (89, 19, 209))
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
            exibir_imagem(tela)  # Exibir imagem e depois voltar ao menu
        elif escolha == "jogar":
            break  # Sai do loop para iniciar o jogo
        else:
            return  # Sai do programa
    
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
            # if captura.captura_em_cadeia_ativa:
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
        
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif not mensagem_vencedor:  # Bloqueia interação após o fim do jogo
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    x, y = evento.pos
                    if captura.escolha_captura_ativa:
                        if captura.processar_clique_botoes(x, y):
                            # Se não estiver em uma captura em cadeia, troca o turno
                            if not captura.captura_em_cadeia_ativa:
                                jogador_atual = "b" if jogador_atual == "v" else "v"
                    else:
                        # Processar clique no tabuleiro
                        movimento_realizado = movimentacao.processar_clique(x, y, jogador_atual)
                        
                        # Trocar turno apenas se um movimento foi concluído e não há capturas em cadeia ativas
                        if movimento_realizado and not captura.captura_em_cadeia_ativa:
                            jogador_atual = "b" if jogador_atual == "v" else "v"
                elif evento.type == pygame.KEYDOWN:
                    movimentacao.processar_eventos(evento)
                
    pygame.quit()

if __name__ == "__main__":
    main()