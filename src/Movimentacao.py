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
            return False
        em_captura_cadeia = self.captura_ref and self.captura_ref.captura_em_cadeia_ativa

        if 0 <= linha < self.tabuleiro_linhas and 0 <= coluna < self.tabuleiro_colunas:
            # Se estivermos em uma captura em cadeia, só permite mover a peça já envolvida na sequência.
            if em_captura_cadeia and self.peca_selecionada:
                linha_sel, coluna_sel = self.peca_selecionada
                if linha != linha_sel or coluna != coluna_sel:
                    if self.gerenciador_pecas.posicao_vazia(linha, coluna) and (linha, coluna) in self.movimentos_possiveis:
                        return self.mover_peca(linha, coluna, jogador_atual)
                    return False

            # Clique em uma peça
            if not self.gerenciador_pecas.posicao_vazia(linha, coluna):
                peca_tipo = self.gerenciador_pecas.obter_tipo_peca(linha, coluna)
                if peca_tipo != jogador_atual:
                    print(f"Não é a vez do jogador {peca_tipo}")
                    return False

                # Verifica se existe captura disponível para o jogador
                if self.captura_ref and self.existe_captura_geral(jogador_atual):
                    # Se a peça clicada não possui movimento de captura, não permite a seleção
                    if not self.possiveis_capturas(linha, coluna):
                        print("Você deve selecionar uma peça com captura disponível!")
                        return False

                print(f"Peça selecionada na posição ({linha}, {coluna})")
                self.peca_selecionada = (linha, coluna)
                self.movimentos_possiveis = self.possiveis_movimentos()  # Método definido abaixo
                return False

            # Clique em uma casa vazia
            else:
                if self.peca_selecionada and (linha, coluna) in self.movimentos_possiveis:
                    return self.mover_peca(linha, coluna, jogador_atual)

        return False

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

    def existe_captura_geral(self, jogador_atual):
        # Percorre todas as posições do tabuleiro
        for i in range(self.tabuleiro_linhas):
            for j in range(self.tabuleiro_colunas):
                if self.configuracao_inicial[i][j] == jogador_atual:
                    # Para cada peça, verifica se há captura disponível
                    if self.possiveis_capturas(i, j):
                        return True
        return False

    def possiveis_capturas(self, linha, coluna):
        peca_tipo = self.configuracao_inicial[linha][coluna]
        # Define o oponente
        oponente = "b" if peca_tipo == "v" else "v"

        # Escolhe as direções de movimento conforme a posição
        if linha % 2 == coluna % 2:
            direcoes = self.DIRECOES_8
        else:
            direcoes = self.DIRECOES_4

        capturas = []
        for dir_linha, dir_coluna in direcoes:
            nova_linha = linha + dir_linha
            nova_coluna = coluna + dir_coluna

            if 0 <= nova_linha < self.tabuleiro_linhas and 0 <= nova_coluna < self.tabuleiro_colunas:
                if self.gerenciador_pecas.posicao_vazia(nova_linha, nova_coluna):
                    # Verifica captura por aproximação e por afastamento
                    cap_aproximacao = self.captura_ref.verificar_pecas_captura(nova_linha, nova_coluna,
                                                                                 dir_linha, dir_coluna,
                                                                                 oponente, self.configuracao_inicial)
                    cap_afastamento = self.captura_ref.verificar_pecas_captura(linha, coluna,
                                                                               -dir_linha, -dir_coluna,
                                                                               oponente, self.configuracao_inicial)
                    if cap_aproximacao or cap_afastamento:
                        capturas.append((nova_linha, nova_coluna))
        return capturas

    def possiveis_movimentos(self):
        """
        Retorna os movimentos possíveis para a peça selecionada.
        Se houver movimentos de captura disponíveis, retorna apenas esses movimentos;
        caso contrário, retorna os movimentos livres.
        """
        linha, coluna = self.peca_selecionada

        if linha % 2 == coluna % 2:
            direcoes = self.DIRECOES_8
        else:
            direcoes = self.DIRECOES_4

        movimentos = []
        movimentos_captura = []
        peca_tipo = self.configuracao_inicial[linha][coluna]
        oponente = "b" if peca_tipo == "v" else "v"

        for dir_linha, dir_coluna in direcoes:
            nova_linha = linha + dir_linha
            nova_coluna = coluna + dir_coluna

            if 0 <= nova_linha < self.tabuleiro_linhas and 0 <= nova_coluna < self.tabuleiro_colunas:
                if self.gerenciador_pecas.posicao_vazia(nova_linha, nova_coluna):
                    movimentos.append((nova_linha, nova_coluna))
                    # Verifica se o movimento resulta em captura
                    cap_aproximacao = self.captura_ref.verificar_pecas_captura(nova_linha, nova_coluna,
                                                                                 dir_linha, dir_coluna,
                                                                                 oponente, self.configuracao_inicial)
                    cap_afastamento = self.captura_ref.verificar_pecas_captura(linha, coluna,
                                                                               -dir_linha, -dir_coluna,
                                                                               oponente, self.configuracao_inicial)
                    if cap_aproximacao or cap_afastamento:
                        movimentos_captura.append((nova_linha, nova_coluna))
        return movimentos_captura if movimentos_captura else movimentos

    def desenhar_movimentos(self, tela):
        # Desenha os círculos para os movimentos válidos
        for movimento in self.movimentos_possiveis:
            linha, coluna = movimento
            pos_x = self.tabuleiro_offset_x + (coluna * self.tamanho_celula) + self.tamanho_celula // 2
            pos_y = self.tabuleiro_offset_y + (linha * self.tamanho_celula) + self.tamanho_celula // 2

            pygame.draw.circle(tela, (255, 0, 0), (pos_x, pos_y), 15)

    def desenhar_borda_selecao(self, tela):
        if self.peca_selecionada is not None:
            linha, coluna = self.peca_selecionada
            x = self.tabuleiro_offset_x + coluna * self.tamanho_celula
            y = self.tabuleiro_offset_y + linha * self.tamanho_celula

            # Se a peça for a selecionada, desenha uma borda branca
            pygame.draw.circle(tela, (255, 255, 255), (x + self.tamanho_celula // 2, y + self.tamanho_celula // 2), 30, 3)

    def processar_eventos(self, evento):
        # Este método pode ser implementado para lidar com entradas de teclado
        pass
