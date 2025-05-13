import pygame

class Tabuleiro:
    def __init__(self, largura, altura, linhas=5, colunas=9, tamanho_celula=100, cor_celula=(255, 255, 255)):
        self.linhas = linhas
        self.colunas = colunas
        self.tamanho_celula = tamanho_celula
        self.largura = colunas * tamanho_celula
        self.altura = linhas * tamanho_celula
        self.tela_largura = largura
        self.tela_altura = altura
        self.offset_x = (largura - self.largura) // 2
        self.offset_y = (altura - self.altura) // 2
        self.cor_fundo = (94, 71, 49)  # Marrom liver
        self.cor_linha = (17, 4, 3)  # Preto licorice
        self.cor_celula = cor_celula

    def desenhar(self, tela):
        tela.fill(self.cor_fundo)
        for i in range(self.linhas):
            for j in range(self.colunas):
                x = self.offset_x + j * self.tamanho_celula + self.tamanho_celula / 2
                y = self.offset_y + i * self.tamanho_celula + self.tamanho_celula / 2
                

                # Conectar pontos adjacentes
                if j < self.colunas - 1:
                    pygame.draw.line(tela, self.cor_linha, (x, y), (x + self.tamanho_celula, y), 2)
                if i < self.linhas - 1:
                    pygame.draw.line(tela, self.cor_linha, (x, y), (x, y + self.tamanho_celula), 2)
                
                # Conexões diagonais
                if i % 2 == j % 2: 
                    if i < self.linhas - 1 and j < self.colunas - 1:
                        pygame.draw.line(tela, self.cor_linha, (x, y), (x + self.tamanho_celula, y + self.tamanho_celula), 2)
                    if i < self.linhas - 1 and j > 0:
                        pygame.draw.line(tela, self.cor_linha, (x, y), (x - self.tamanho_celula, y + self.tamanho_celula), 2)
                    
                # Desenhar os pontos
                pygame.draw.circle(tela, self.cor_linha, (x, y), 8)
                