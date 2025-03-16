import pygame

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (219, 55, 99)
AZUL = (89, 19, 209)

class Peca:
    def __init__(self, x, y, cor):
        self.x = x
        self.y = y
        self.cor = cor

    def desenhar(self, tela):
        pygame.draw.circle(tela, self.cor, (self.x, self.y), 20)

    def movimentar(self, novo_x, novo_y):
        self.x = novo_x
        self.y = novo_y

class GerenciadorPecas:
    def __init__(self, linhas, colunas, tamanho_celula, offset_x, offset_y, configuracao_inicial):
        self.linhas = linhas
        self.colunas = colunas
        self.tamanho_celula = tamanho_celula
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.configuracao_inicial = configuracao_inicial
        self.pecas = self.inicializar_pecas()

    def inicializar_pecas(self):
        print("Peças 3: \n")
        for configuracao in self.configuracao_inicial:
            print(f"{configuracao} \n")
        
        pecas = []
        for i in range(self.linhas):
            linha = []
            for j in range(self.colunas):
                x = self.offset_x + j * self.tamanho_celula + self.tamanho_celula // 2
                y = self.offset_y + i * self.tamanho_celula + self.tamanho_celula // 2

                if self.configuracao_inicial[i][j] == "v":
                    linha.append(Peca(x, y, VERMELHO))  # Peças do jogador A
                elif self.configuracao_inicial[i][j] == "b":
                    linha.append(Peca(x, y, AZUL))  # Peças do jogador B
                elif self.configuracao_inicial[i][j] == "-":
                    linha.append(None)  # Espaço vazio
            pecas.append(linha)
        return pecas

    def desenhar_pecas(self, tela):
        for linha in self.pecas:
            for peca in linha:
                if peca is not None:
                    peca.desenhar(tela)  # Corrigido: chamar o método desenhar da instância peca
                    
    def posicao_vazia(self, linha, coluna):
        return self.pecas[linha][coluna] is None
    
    def mover_peca(self, linha_atual, coluna_atual, nova_linha, nova_coluna, configuracao_inicial, tela):
        if self.posicao_vazia(nova_linha, nova_coluna):
            # Atualiza a configuração
            peca = configuracao_inicial[linha_atual][coluna_atual]
            configuracao_inicial[linha_atual][coluna_atual] = "-"
            configuracao_inicial[nova_linha][nova_coluna] = peca

            # Move a peça visualmente
            self.pecas[nova_linha][nova_coluna] = self.pecas[linha_atual][coluna_atual]
            self.pecas[linha_atual][coluna_atual] = None
            self.pecas[nova_linha][nova_coluna].movimentar(
                self.offset_x + nova_coluna * self.tamanho_celula + self.tamanho_celula // 2,
                self.offset_y + nova_linha * self.tamanho_celula + self.tamanho_celula // 2
            )

        # Redesenha o tabuleiro
        self.desenhar_pecas(tela)

    def capturar_pecas(self, linha_atual, coluna_atual, nova_linha, nova_coluna, configuracao_inicial, tela):
        direcao_linha = nova_linha - linha_atual
        direcao_coluna = nova_coluna - coluna_atual
        peca = configuracao_inicial[nova_linha][nova_coluna]  # Pegando a peça já na nova posição
        oponente = "b" if peca == "v" else "v"

        # Captura por Aproximação
        linha_temp = nova_linha + direcao_linha
        coluna_temp = nova_coluna + direcao_coluna
        while 0 <= linha_temp < self.linhas and 0 <= coluna_temp < self.colunas:
            if configuracao_inicial[linha_temp][coluna_temp] == oponente:
                configuracao_inicial[linha_temp][coluna_temp] = "-"
                # Atualizar a representação visual das peças
                self.pecas[linha_temp][coluna_temp] = None
            else:
                break
            linha_temp += direcao_linha
            coluna_temp += direcao_coluna

        # Captura por Afastamento
        linha_temp = linha_atual - direcao_linha
        coluna_temp = coluna_atual - direcao_coluna
        while 0 <= linha_temp < self.linhas and 0 <= coluna_temp < self.colunas:
            if configuracao_inicial[linha_temp][coluna_temp] == oponente:
                configuracao_inicial[linha_temp][coluna_temp] = "-"
                # Atualizar a representação visual das peças
                self.pecas[linha_temp][coluna_temp] = None
            else:
                break
            linha_temp -= direcao_linha
            coluna_temp -= direcao_coluna

        # Redesenhar o tabuleiro
        self.desenhar_pecas(tela)  


