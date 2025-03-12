import pygame

from Pecas import GerenciadorPecas

# Configurações do tabuleiro
tabuleiro_linhas, tabuleiro_colunas = 5, 9
tamanho_celula = 100
tabuleiro_offset_x = 50
tabuleiro_offset_y = 50

# Inicializa o Pygame
pygame.init()
tela = pygame.display.set_mode((tabuleiro_colunas * tamanho_celula + 100, tabuleiro_linhas * tamanho_celula + 100))
pygame.display.set_caption("Movimentação Fanorona")

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (200, 0, 0)

class Movimentacao:
    DIRECOES_8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    DIRECOES_4 = [(-1, 0), (0, -1), (0, 1), (1, 0)]

    def __init__(self, tabuleiro_linhas, tabuleiro_colunas, tamanho_celula, tabuleiro_offset_x, tabuleiro_offset_y, gerenciador_pecas):
        self.tabuleiro_linhas = tabuleiro_linhas
        self.tabuleiro_colunas = tabuleiro_colunas
        self.tamanho_celula = tamanho_celula
        self.tabuleiro_offset_x = tabuleiro_offset_x
        self.tabuleiro_offset_y = tabuleiro_offset_y
        self.gerenciador_pecas = gerenciador_pecas
        self.pecas = [(2, 4)]  # Exemplo de peça no meio do tabuleiro
    
    def processar_clique(self, x, y):
        # Converte a posição do clique para índice da matriz
        coluna = (x - self.tabuleiro_offset_x) // self.tamanho_celula
        linha = (y - self.tabuleiro_offset_y) // self.tamanho_celula

        # Verifica se o clique foi dentro dos limites do tabuleiro
        if 0 <= linha < self.tabuleiro_linhas and 0 <= coluna < self.tabuleiro_colunas:
            if not self.gerenciador_pecas.posicao_vazia(linha, coluna):
                print(f"Peça selecionada na posição ({linha}, {coluna})")
                self.peca_selecionada = (linha, coluna)  # Armazena a peça selecionada


    def desenhar_pecas(self, tela):
        for linha, coluna in self.pecas:
            x = self.tabuleiro_offset_x + coluna * self.tamanho_celula
            y = self.tabuleiro_offset_y + linha * self.tamanho_celula
            #pygame.draw.circle(tela, VERMELHO, (x, y), 15)

    def mover_peca(self, indice, direcao):
        linha, coluna = self.pecas[indice]
        nova_linha = linha + direcao[0]
        nova_coluna = coluna + direcao[1]
        
        if 0 <= nova_linha < self.tabuleiro_linhas and 0 <= nova_coluna < self.tabuleiro_colunas:
            if self.gerenciador_pecas.posicao_vazia(nova_linha, nova_coluna):
                self.gerenciador_pecas.mover_peca(linha, coluna, nova_linha, nova_coluna)
                self.pecas[indice] = (nova_linha, nova_coluna)

    def processar_eventos(self, event):
        linha, coluna = self.pecas[0]
        if linha % 2 == coluna % 2:
            direcoes = self.DIRECOES_8
        else:
            direcoes = self.DIRECOES_4

        if event.key == pygame.K_UP:
            self.mover_peca(0, direcoes[0])
        elif event.key == pygame.K_DOWN:
            self.mover_peca(0, direcoes[3])
        elif event.key == pygame.K_LEFT:
            self.mover_peca(0, direcoes[1])
        elif event.key == pygame.K_RIGHT:
            self.mover_peca(0, direcoes[2])
        elif linha % 2 == coluna % 2:
            if event.key == pygame.K_w:
                self.mover_peca(0, direcoes[0])
            elif event.key == pygame.K_e:
                self.mover_peca(0, direcoes[2])
            elif event.key == pygame.K_a:
                self.mover_peca(0, direcoes[4])
            elif event.key == pygame.K_d:
                self.mover_peca(0, direcoes[6])

# movimentacao = Movimentacao(tabuleiro_linhas, tabuleiro_colunas, tamanho_celula, tabuleiro_offset_x, tabuleiro_offset_y, GerenciadorPecas)

