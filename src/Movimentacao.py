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

    def __init__(self, tabuleiro_linhas, tabuleiro_colunas, tamanho_celula, tabuleiro_offset_x, tabuleiro_offset_y, gerenciador_pecas, configuracao_inicial):
        self.tabuleiro_linhas = tabuleiro_linhas
        self.tabuleiro_colunas = tabuleiro_colunas
        self.tamanho_celula = tamanho_celula
        self.tabuleiro_offset_x = tabuleiro_offset_x
        self.tabuleiro_offset_y = tabuleiro_offset_y
        self.gerenciador_pecas = gerenciador_pecas
        self.pecas = [(2, 4)]  # Exemplo de peça no meio do tabuleiro
        self.peca_selecionada = None
        self.movimentos_possiveis = []  # Armazena os movimentos ativos
        self.configuracao_inicial = configuracao_inicial
    
    # Verifica se o clique foi dentro dos limites do tabuleiro
    def processar_clique(self, x, y):
        coluna = (x - self.tabuleiro_offset_x) // self.tamanho_celula
        linha = (y - self.tabuleiro_offset_y) // self.tamanho_celula

        if 0 <= linha < self.tabuleiro_linhas and 0 <= coluna < self.tabuleiro_colunas:
            if not self.gerenciador_pecas.posicao_vazia(linha, coluna):
                print(f"Peça selecionada na posição ({linha}, {coluna})")
                self.peca_selecionada = (linha, coluna)
                self.desenhar_borda_selecao(tela)
                self.movimentos_possiveis = self.possiveis_movimentos()
            else:
                # Se clicar em uma casa vazia e já tiver peça selecionada, tenta mover
                if self.peca_selecionada and (linha, coluna) in self.movimentos_possiveis:
                    print(f"Movendo para ({linha}, {coluna})")
                    self.mover_peca(linha, coluna)
                    self.peca_selecionada = None
                    self.movimentos_possiveis = []  # Limpa os círculos após o movimento

    def possiveis_movimentos(self):
        linha, coluna = self.peca_selecionada

        if linha % 2 == coluna % 2:
            direcoes = self.DIRECOES_8
        else:
            direcoes = self.DIRECOES_4
        
        movimentos = []
        for direcao in direcoes:
            nova_linha = linha + direcao[0]
            nova_coluna = coluna + direcao[1]

            if 0 <= nova_linha < self.tabuleiro_linhas and 0 <= nova_coluna < self.tabuleiro_colunas:
                if self.gerenciador_pecas.posicao_vazia(nova_linha, nova_coluna):
                    movimentos.append((nova_linha, nova_coluna))
        return movimentos

    def desenhar_movimentos(self):
        # Desenha os círculos para os movimentos válidos
        for movimento in self.movimentos_possiveis:
            linha, coluna = movimento
            pos_x = self.tabuleiro_offset_x + (coluna * self.tamanho_celula) + self.tamanho_celula // 2
            pos_y = self.tabuleiro_offset_y + (linha * self.tamanho_celula) + self.tamanho_celula // 2

            pygame.draw.circle(tela, (255, 0, 0), (pos_x, pos_y), 15)

    def mover_peca(self, nova_linha, nova_coluna):
        # Move a peça e atualiza o tabuleiro
        linha_atual, coluna_atual = self.peca_selecionada
        
        self.gerenciador_pecas.mover_peca(linha_atual, coluna_atual, nova_linha, nova_coluna, self.configuracao_inicial, tela)
        self.gerenciador_pecas.capturar_pecas(linha_atual, coluna_atual, nova_linha, nova_coluna, self.configuracao_inicial, tela)

        print("Movimentação: \n")
        for configuracao in self.configuracao_inicial:
            print(f"{configuracao} \n")
    

    def desenhar_borda_selecao(self, tela):
        if self.peca_selecionada != None:
            linha, coluna = self.peca_selecionada
            x = self.tabuleiro_offset_x + coluna * self.tamanho_celula
            y = self.tabuleiro_offset_y + linha * self.tamanho_celula

            # Se a peça for a selecionada, desenha uma borda branca
            if self.peca_selecionada == (linha, coluna):
                pygame.draw.circle(tela, (255, 255, 255), (x + self.tamanho_celula // 2, y + self.tamanho_celula // 2), 30, 3)






    # def processar_eventos(self, event):
    #     linha, coluna = self.pecas[0]
    #     if linha % 2 == coluna % 2:
    #         direcoes = self.DIRECOES_8
    #     else:
    #         direcoes = self.DIRECOES_4

    #     if event.key == pygame.K_UP:
    #         self.mover_peca(0, direcoes[0])
    #     elif event.key == pygame.K_DOWN:
    #         self.mover_peca(0, direcoes[3])
    #     elif event.key == pygame.K_LEFT:
    #         self.mover_peca(0, direcoes[1])
    #     elif event.key == pygame.K_RIGHT:
    #         self.mover_peca(0, direcoes[2])
    #     elif linha % 2 == coluna % 2:
    #         if event.key == pygame.K_w:
    #             self.mover_peca(0, direcoes[0])
    #         elif event.key == pygame.K_e:
    #             self.mover_peca(0, direcoes[2])
    #         elif event.key == pygame.K_a:
    #             self.mover_peca(0, direcoes[4])
    #         elif event.key == pygame.K_d:
    #             self.mover_peca(0, direcoes[6])

# movimentacao = Movimentacao(tabuleiro_linhas, tabuleiro_colunas, tamanho_celula, tabuleiro_offset_x, tabuleiro_offset_y, GerenciadorPecas)

