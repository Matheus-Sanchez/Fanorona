import pygame

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
        self.peca_selecionada = None
        self.movimentos_possiveis = []  # Armazena os movimentos ativos
        self.configuracao_inicial = configuracao_inicial
        self.captura_ref = None  # Referência para o objeto Captura
    
    def set_captura_ref(self, captura):
        """Define a referência para o objeto Captura"""
        self.captura_ref = captura
        captura.movimentacao_ref = self  # Define a referência mútua
    
    def processar_clique(self, x, y, jogador_atual):
        coluna = (x - self.tabuleiro_offset_x) // self.tamanho_celula
        linha = (y - self.tabuleiro_offset_y) // self.tamanho_celula

        # Se houver uma escolha de captura ativa, ignoramos cliques no tabuleiro
        if self.captura_ref and self.captura_ref.escolha_captura_ativa:
            return False  # Nenhuma ação realizada no tabuleiro

        # Verificar se estamos em uma captura em cadeia
        em_captura_cadeia = self.captura_ref and self.captura_ref.captura_em_cadeia_ativa

        if 0 <= linha < self.tabuleiro_linhas and 0 <= coluna < self.tabuleiro_colunas:
            # Se estivermos em uma captura em cadeia, só podemos selecionar a peça que acabou de capturar
            if em_captura_cadeia and self.peca_selecionada:
                linha_sel, coluna_sel = self.peca_selecionada
                if linha != linha_sel or coluna != coluna_sel:
                    # Se clicar em uma casa vazia que é um movimento possível, permitir o movimento
                    if self.gerenciador_pecas.posicao_vazia(linha, coluna) and (linha, coluna) in self.movimentos_possiveis:
                        return self.mover_peca(linha, coluna, jogador_atual)
                    return False  # Não permite selecionar outra peça durante captura em cadeia
            
            # Clique em uma peça
            if not self.gerenciador_pecas.posicao_vazia(linha, coluna):
                # Verificar se a peça clicada pertence ao jogador atual
                peca_tipo = self.gerenciador_pecas.obter_tipo_peca(linha, coluna)
                if peca_tipo != jogador_atual:
                    print(f"Não é a vez do jogador {peca_tipo}")
                    return False  # Não é a vez deste jogador
                
                print(f"Peça selecionada na posição ({linha}, {coluna})")
                self.peca_selecionada = (linha, coluna)
                self.movimentos_possiveis = self.possiveis_movimentos()
                return False  # Apenas selecionou uma peça, não trocou o turno
            
            # Clique em uma casa vazia
            else:
                # Se clicar em uma casa vazia e já tiver peça selecionada, tenta mover
                if self.peca_selecionada and (linha, coluna) in self.movimentos_possiveis:
                    return self.mover_peca(linha, coluna, jogador_atual)
        
        return False  # Nenhuma ação que mude o turno foi realizada

    def mover_peca(self, nova_linha, nova_coluna, jogador_atual):
        """Método para mover a peça selecionada para uma nova posição"""
        linha_atual, coluna_atual = self.peca_selecionada
        
        # Move a peça
        self.gerenciador_pecas.mover_peca(linha_atual, coluna_atual, nova_linha, nova_coluna, 
                                        self.configuracao_inicial, pygame.display.get_surface())
        
        # Verifica e processa capturas (retorna True se houve captura)
        captura_realizada = False
        if self.captura_ref:
            captura_realizada = self.captura_ref.capturar_pecas(linha_atual, coluna_atual, nova_linha, nova_coluna, 
                                                            self.configuracao_inicial, pygame.display.get_surface())
        
        # Só limpa a seleção se não houver escolha de captura ativa e não estiver em uma captura em cadeia
        if not (self.captura_ref and (self.captura_ref.escolha_captura_ativa or self.captura_ref.captura_em_cadeia_ativa)):
            self.limpar_selecao()
        
        print("Estado atual: ")
        for configuracao in self.configuracao_inicial:
            print(f"{configuracao} \n")
        
        # Retorna True para indicar que o movimento foi concluído e pode trocar de turno
        # (mas a troca só acontecerá se não houver capturas em cadeia)
        return True

    def limpar_selecao(self):
        """Método auxiliar para limpar seleção e possíveis movimentos"""
        self.peca_selecionada = None
        self.movimentos_possiveis = []

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

    def desenhar_movimentos(self, tela):
        # Desenha os círculos para os movimentos válidos
        for movimento in self.movimentos_possiveis:
            linha, coluna = movimento
            pos_x = self.tabuleiro_offset_x + (coluna * self.tamanho_celula) + self.tamanho_celula // 2
            pos_y = self.tabuleiro_offset_y + (linha * self.tamanho_celula) + self.tamanho_celula // 2

            pygame.draw.circle(tela, (255, 0, 0), (pos_x, pos_y), 15)

    def desenhar_borda_selecao(self, tela):
        if self.peca_selecionada != None:
            linha, coluna = self.peca_selecionada
            x = self.tabuleiro_offset_x + coluna * self.tamanho_celula
            y = self.tabuleiro_offset_y + linha * self.tamanho_celula

            # Se a peça for a selecionada, desenha uma borda branca
            if self.peca_selecionada == (linha, coluna):
                pygame.draw.circle(tela, (255, 255, 255), (x + self.tamanho_celula // 2, y + self.tamanho_celula // 2), 30, 3)

    def processar_eventos(self, evento):
        # Este método pode ser implementado para lidar com entradas de teclado
        pass