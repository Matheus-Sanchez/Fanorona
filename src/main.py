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

def main():
    pygame.init()
    largura, altura = 1000, 600
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Fanorona")
    fonte = pygame.font.Font(None, 50)
    
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
    
    tabuleiro = Tabuleiro(largura, altura)
    pecas = GerenciadorPecas(5, 9, 100, (largura - 900) // 2, (altura - 500) // 2, configuracao_inicial)
    movimentacao = Movimentacao(5, 9, 100, (largura - 900) // 2, (altura - 500) // 2, pecas, configuracao_inicial)
    captura = Captura(5, 9, 100, (largura - 900) // 2, (altura - 500) // 2, configuracao_inicial)
    
    mensagem_vencedor = None
    rodando = True
    while rodando:
        tela.fill((255, 255, 255))
        tabuleiro.desenhar(tela)
        pecas.desenhar_pecas(tela)
        movimentacao.desenhar_movimentos()
        pygame.display.flip()
        
        if hasattr(pecas, 'escolha_captura_ativa') and pecas.escolha_captura_ativa:
            pecas.desenhar_botoes_captura(tela)
        
        if mensagem_vencedor:
            texto_vencedor = fonte.render(mensagem_vencedor, True, (255, 0, 0))
            tela.blit(texto_vencedor, (largura // 2 - texto_vencedor.get_width() // 2, 20))
        
        pygame.display.flip()
        
        if not mensagem_vencedor:
            resultado = verificar_fim_de_jogo(configuracao_inicial)
            if resultado:
                mensagem_vencedor = resultado
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif not mensagem_vencedor:  # Bloqueia interação após o fim do jogo
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    x, y = evento.pos
                    if hasattr(pecas, 'escolha_captura_ativa') and pecas.escolha_captura_ativa:
                        if pecas.processar_clique_botoes(x, y):
                            continue
                    movimentacao.processar_clique(x, y)
                elif evento.type == pygame.KEYDOWN:
                    movimentacao.processar_eventos(evento)
                
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
