import pygame
from Tabuleiro import Tabuleiro
from Pecas import GerenciadorPecas
from Movimentacao import Movimentacao

# Configurações da tela
tela_largura = 1000
tela_altura = 600

# Inicializa o Pygame
pygame.init()
tela = pygame.display.set_mode((tela_largura, tela_altura))
pygame.display.set_caption("Fanorona")

# Definindo a configuração inicial das peças
configuracao_inicial = [
    ["v", "v", "v", "v", "v", "v", "v", "v", "v"],
    ["v", "v", "v", "v", "v", "v", "v", "v", "v"],
    ["v", "b", "v", "b", "-", "v", "b", "v", "b"],
    ["b", "b", "b", "b", "b", "b", "b", "b", "b"],
    ["b", "b", "b", "b", "b", "b", "b", "b", "b"]
]

# Cria o tabuleiro, as peças e a movimentação
tabuleiro = Tabuleiro(tela_largura, tela_altura, cor_celula=(255, 255, 255))  # Cor das células branca
pecas = GerenciadorPecas(5, 9, 100, (tela_largura - 900) // 2, (tela_altura - 500) // 2, configuracao_inicial)
movimentacao = Movimentacao(5, 9, 100, (tela_largura - 900) // 2, (tela_altura - 500) // 2, pecas, configuracao_inicial)

for configuracao in configuracao_inicial:
    print(f"{configuracao} \n")
    
# Loop principal do jogo
rodando = True
while rodando:
    tela.fill((255, 255, 255))
    
    tabuleiro.desenhar(tela)
    pecas.desenhar_pecas(tela)
    movimentacao.gerenciador_pecas.desenhar_pecas(tela)
    movimentacao.desenhar_borda_selecao(tela)
    movimentacao.desenhar_movimentos()  # Mantém os círculos na tela
    
    
    # Desenhar botões de captura, se estiverem ativos
    if hasattr(pecas, 'escolha_captura_ativa') and pecas.escolha_captura_ativa:
        pecas.desenhar_botoes_captura(tela)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False
        elif event.type == pygame.MOUSEBUTTONDOWN:  # Captura clique do mouse
            x, y = event.pos
            
            # Primeiro tenta processar cliques nos botões de captura
            if hasattr(pecas, 'escolha_captura_ativa') and pecas.escolha_captura_ativa:
                if pecas.processar_clique_botoes(x, y):
                    continue  # Se o clique foi em um botão, não processamos como movimento
            
            # Se não foi um clique em botão, processa normalmente
            movimentacao.processar_clique(x, y)
        elif event.type == pygame.KEYDOWN:
            movimentacao.processar_eventos(event)
    
    pygame.display.flip()
    
pygame.quit()