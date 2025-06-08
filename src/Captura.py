import pygame

class Captura:
    def __init__(self, linhas, colunas, tamanho_celula, offset_x, offset_y, configuracao_inicial):
        self.linhas = linhas
        self.colunas = colunas
        self.tamanho_celula = tamanho_celula
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.configuracao_inicial = configuracao_inicial
        self.escolha_captura_ativa = False
        self.pecas = None  # Referência para o gerenciador de peças
        self.captura_em_cadeia_ativa = False  # Indica se uma cadeia de capturas está em andamento
        self.posicao_ultima_peca = None  # Armazena a posição da última peça movida em uma cadeia
        self.tabuleiro = None  # Referência para o tabuleiro (adicionado)
        
        # Novas variáveis para controlar as restrições de movimento
        self.posicoes_visitadas = []  # Lista de posições visitadas durante uma captura em cadeia
        self.ultima_direcao = None  # Armazena a última direção de movimento (linha_dir, coluna_dir)
    
    def set_gerenciador_pecas(self, gerenciador_pecas):
        """Define a referência para o gerenciador de peças"""
        self.pecas = gerenciador_pecas
    
    def set_tabuleiro(self, tabuleiro):
        """Define a referência para o objeto Tabuleiro."""
        self.tabuleiro = tabuleiro

    def capturar_pecas(self, linha_atual, coluna_atual, nova_linha, nova_coluna, configuracao_inicial, tela):
        direcao_linha = nova_linha - linha_atual
        direcao_coluna = nova_coluna - coluna_atual
        
        # Normalizar a direção para registrá-la corretamente (somente o sentido, não a magnitude)
        if direcao_linha != 0:
            direcao_linha = direcao_linha // abs(direcao_linha)
        if direcao_coluna != 0:
            direcao_coluna = direcao_coluna // abs(direcao_coluna)
            
        # Salvar a direção do movimento atual
        direcao_atual = (direcao_linha, direcao_coluna)
        
        peca = configuracao_inicial[nova_linha][nova_coluna]
        oponente = "b" if peca == "v" else "v"
        
        # Verificar se existem peças para capturar em ambas direções
        pecas_aproximacao = self.verificar_pecas_captura(nova_linha, nova_coluna, direcao_linha, direcao_coluna, oponente, configuracao_inicial)
        pecas_afastamento = self.verificar_pecas_captura(linha_atual, coluna_atual, -direcao_linha, -direcao_coluna, oponente, configuracao_inicial)
        
        # Se é o primeiro movimento em uma sequência, inicializa a lista de posições visitadas
        if not self.captura_em_cadeia_ativa:
            self.posicoes_visitadas = [(linha_atual, coluna_atual)]
            self.ultima_direcao = None
        
        # Adiciona a nova posição à lista de posições visitadas
        self.posicoes_visitadas.append((nova_linha, nova_coluna))
        
        # Salvar a posição da última peça movida para possíveis capturas em cadeia
        self.posicao_ultima_peca = (nova_linha, nova_coluna)
        
        # Atualizar a última direção de movimento
        self.ultima_direcao = direcao_atual
        
        # Se não há peças para capturar, retornar
        if not pecas_aproximacao and not pecas_afastamento:
            # Limpar seleção mesmo sem capturas
            if hasattr(self, 'movimentacao_ref'):
                self.movimentacao_ref.limpar_selecao()
            self.captura_em_cadeia_ativa = False
            self.posicoes_visitadas = []  # Limpar posições visitadas ao terminar
            self.ultima_direcao = None  # Limpar última direção
            return False  # Informa que não houve captura
        
        # Se só há um tipo de captura possível, executar automaticamente
        if pecas_aproximacao and not pecas_afastamento:
            captura_realizada = self.executar_captura(nova_linha, nova_coluna, direcao_linha, direcao_coluna, oponente, configuracao_inicial, tela)
            # Verificar se existem mais capturas possíveis após esta
            self.verificar_capturas_em_cadeia(nova_linha, nova_coluna, peca, configuracao_inicial, tela)
            return captura_realizada
        elif not pecas_aproximacao and pecas_afastamento:
            captura_realizada = self.executar_captura(linha_atual, coluna_atual, -direcao_linha, -direcao_coluna, oponente, configuracao_inicial, tela)
            # Verificar se existem mais capturas possíveis após esta
            self.verificar_capturas_em_cadeia(nova_linha, nova_coluna, peca, configuracao_inicial, tela)
            return captura_realizada
        
        # Se há dois tipos de captura possíveis, mostrar opções para o jogador
        self.mostrar_opcoes_captura(nova_linha, nova_coluna, linha_atual, coluna_atual, 
                                direcao_linha, direcao_coluna, oponente, configuracao_inicial, tela)
        return True  # Informa que houve captura (ou pelo menos a possibilidade)

    def verificar_capturas_em_cadeia(self, linha, coluna, peca_tipo, configuracao_inicial, tela):
        """Verifica se há mais capturas possíveis após uma captura"""
        oponente = "b" if peca_tipo == "v" else "v"
        capturas_possiveis = self.verificar_todas_direcoes_captura(linha, coluna, peca_tipo, oponente, configuracao_inicial)
        
        if capturas_possiveis:
            self.captura_em_cadeia_ativa = True
            # Selecionar automaticamente a peça para próximas capturas
            if hasattr(self, 'movimentacao_ref'):
                self.movimentacao_ref.peca_selecionada = (linha, coluna)
                self.movimentacao_ref.movimentos_possiveis = []
                # Adicionar apenas os movimentos que levam a capturas e não violam as restrições
                for dir_linha, dir_coluna in capturas_possiveis:
                    nova_linha = linha + dir_linha
                    nova_coluna = coluna + dir_coluna
                    
                    # Verificar se o novo movimento não viola as restrições
                    if self.movimento_valido_em_cadeia(nova_linha, nova_coluna, dir_linha, dir_coluna):
                        if 0 <= nova_linha < self.linhas and 0 <= nova_coluna < self.colunas and configuracao_inicial[nova_linha][nova_coluna] == "-":
                            self.movimentacao_ref.movimentos_possiveis.append((nova_linha, nova_coluna))
                
                # Se não houver movimentos possíveis após aplicar as restrições, terminar a cadeia
                if not self.movimentacao_ref.movimentos_possiveis:
                    self.captura_em_cadeia_ativa = False
                    self.movimentacao_ref.limpar_selecao()
                    self.posicoes_visitadas = []  # Limpar posições visitadas
                    self.ultima_direcao = None    # Limpar última direção
        else:
            self.captura_em_cadeia_ativa = False
            # Limpar seleção quando não há mais capturas possíveis
            if hasattr(self, 'movimentacao_ref'):
                self.movimentacao_ref.limpar_selecao()
            self.posicoes_visitadas = []  # Limpar posições visitadas
            self.ultima_direcao = None    # Limpar última direção
        
        return self.captura_em_cadeia_ativa
    
    def movimento_valido_em_cadeia(self, nova_linha, nova_coluna, dir_linha, dir_coluna):
        """
        Verifica se um movimento é válido durante uma cadeia de capturas:
        1. Não pode visitar uma posição já visitada nesta cadeia
        2. Não pode mover na mesma direção do movimento anterior
        """
        # Verificar se a posição já foi visitada
        if (nova_linha, nova_coluna) in self.posicoes_visitadas:
            return False
        
        # Verificar se está tentando mover na mesma direção do movimento anterior
        if self.ultima_direcao:
            # Normalizar a direção para comparação
            if dir_linha != 0:
                dir_linha = dir_linha // abs(dir_linha)
            if dir_coluna != 0:
                dir_coluna = dir_coluna // abs(dir_coluna)
                
            if (dir_linha, dir_coluna) == self.ultima_direcao:
                return False
        
        return True

    def verificar_todas_direcoes_captura(self, linha, coluna, peca_tipo, oponente, configuracao_inicial):
        """Verifica em todas as direções possíveis se há capturas disponíveis"""
        # Define as direções possíveis baseadas na paridade da posição
        if linha % 2 == coluna % 2:  # Posições que permitem movimento diagonal
            direcoes = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        else:  # Posições que permitem apenas movimento ortogonal
            direcoes = [(-1, 0), (0, -1), (0, 1), (1, 0)]
        
        capturas_possiveis = []
        
        for dir_linha, dir_coluna in direcoes:
            nova_linha = linha + dir_linha
            nova_coluna = coluna + dir_coluna
            
            # Verificar se o movimento é válido (dentro do tabuleiro e para uma casa vazia)
            if 0 <= nova_linha < self.linhas and 0 <= nova_coluna < self.colunas and configuracao_inicial[nova_linha][nova_coluna] == "-":
                # Verificar se o movimento cumpre as restrições da cadeia
                if self.movimento_valido_em_cadeia(nova_linha, nova_coluna, dir_linha, dir_coluna):
                    # Verificar se há capturas por aproximação
                    pecas_aproximacao = self.verificar_pecas_captura(nova_linha, nova_coluna, dir_linha, dir_coluna, oponente, configuracao_inicial)
                    # Verificar se há capturas por afastamento
                    pecas_afastamento = self.verificar_pecas_captura(linha, coluna, -dir_linha, -dir_coluna, oponente, configuracao_inicial)
                    
                    if pecas_aproximacao or pecas_afastamento:
                        capturas_possiveis.append((dir_linha, dir_coluna))
        
        return capturas_possiveis

    def mostrar_opcoes_captura(self, nova_linha, nova_coluna, linha_atual, coluna_atual, 
                            direcao_linha, direcao_coluna, oponente, configuracao_inicial, tela):
        """Mostra botões para o jogador escolher o tipo de captura"""
        # Salvar informações do movimento atual
        self.movimento_atual = {
            'nova_linha': nova_linha,
            'nova_coluna': nova_coluna,
            'linha_atual': linha_atual,
            'coluna_atual': coluna_atual
        }
        
        # A largura total da tela é tela_largura = 1000 (da main.py)
        # Posicionando os botões de forma mais centralizados
        self.opcoes_captura = {
            'aproximacao': {
                'pos': (300, 550),
                'size': (180, 30),
                'text': 'Aproximação',
                'action': lambda: self.finalizar_movimento_com_captura(
                    nova_linha, nova_coluna, direcao_linha, direcao_coluna, oponente, configuracao_inicial, tela)
            },
            'afastamento': {
                'pos': (520, 550),
                'size': (180, 30),
                'text': 'Afastamento',
                'action': lambda: self.finalizar_movimento_com_captura(
                    linha_atual, coluna_atual, -direcao_linha, -direcao_coluna, oponente, configuracao_inicial, tela)
            }
        }
        
        # Esta variável será usada no loop principal para verificar se botões de captura estão ativos
        self.escolha_captura_ativa = True

    def finalizar_movimento_com_captura(self, linha_base, coluna_base, direcao_linha, direcao_coluna, oponente, configuracao_inicial, tela):
        """Executa a captura e limpa os estados visuais"""
        # Executar a captura
        self.executar_captura(linha_base, coluna_base, direcao_linha, direcao_coluna, oponente, configuracao_inicial, tela)
        
        # Verificar se existem mais capturas possíveis após esta
        peca_tipo = configuracao_inicial[self.posicao_ultima_peca[0]][self.posicao_ultima_peca[1]]
        self.verificar_capturas_em_cadeia(self.posicao_ultima_peca[0], self.posicao_ultima_peca[1], peca_tipo, configuracao_inicial, tela)
        
        # Resetar estados
        self.escolha_captura_ativa = False

        # Redesenhar o tabuleiro completamente para garantir que tudo esteja atualizado visualmente
        if self.pecas:
            self.pecas.desenhar_pecas(tela)

    def executar_captura(self, linha_base, coluna_base, direcao_linha, direcao_coluna, oponente, configuracao_inicial, tela):
        """Executa a captura na direção especificada"""
        linha_temp = linha_base + direcao_linha
        coluna_temp = coluna_base + direcao_coluna
        captura_realizada = False
        
        while 0 <= linha_temp < self.linhas and 0 <= coluna_temp < self.colunas:
            if configuracao_inicial[linha_temp][coluna_temp] == oponente:
                configuracao_inicial[linha_temp][coluna_temp] = "-"
                if self.pecas:
                    self.pecas.pecas[linha_temp][coluna_temp] = None
                captura_realizada = True
            else:
                break
            linha_temp += direcao_linha
            coluna_temp += direcao_coluna
        
        # Resetar estado de escolha
        self.escolha_captura_ativa = False
        
        # Redesenhar completamente
        if self.pecas:
            self.pecas.desenhar_pecas(tela)
        return captura_realizada
    
    def verificar_pecas_captura(self, linha_base, coluna_base, direcao_linha, direcao_coluna, oponente, configuracao_inicial):
        """Verifica se há peças para capturar na direção especificada"""
        pecas_para_capturar = []
        linha_temp = linha_base + direcao_linha
        coluna_temp = coluna_base + direcao_coluna
        
        while 0 <= linha_temp < self.linhas and 0 <= coluna_temp < self.colunas:
            if configuracao_inicial[linha_temp][coluna_temp] == oponente:
                pecas_para_capturar.append((linha_temp, coluna_temp))
            else:
                break
            linha_temp += direcao_linha
            coluna_temp += direcao_coluna
        
        return pecas_para_capturar

    def desenhar_botoes_captura(self, tela):
        """Desenha os botões de escolha de captura"""
        if self.escolha_captura_ativa:
            font = pygame.font.SysFont(None, 24)
            
            for botao_info in self.opcoes_captura.values():
                # Desenhar retângulo do botão
                pygame.draw.rect(tela, (200, 200, 200), (botao_info['pos'][0], botao_info['pos'][1], 
                                                        botao_info['size'][0], botao_info['size'][1]))
                
                # Desenhar texto do botão
                texto = font.render(botao_info['text'], True, (0, 0, 0))
                texto_rect = texto.get_rect(center=(botao_info['pos'][0] + botao_info['size'][0]//2, 
                                                botao_info['pos'][1] + botao_info['size'][1]//2))
                tela.blit(texto, texto_rect)

    def processar_clique_botoes(self, pos_x, pos_y):
        """Processa cliques nos botões de captura"""
        if self.escolha_captura_ativa:
            for botao_info in self.opcoes_captura.values():
                x, y = botao_info['pos']
                largura, altura = botao_info['size']
                
                if x <= pos_x <= x + largura and y <= pos_y <= y + altura:
                    botao_info['action']()  # Executar a ação associada ao botão
                    self.escolha_captura_ativa = False  # Desativar os botões após a escolha
                    return True
        
        return False

    def existe_captura_geral(self, jogador, posicao=None):
        """
        Verifica se há capturas disponíveis para o jogador.
        :param jogador: 'v' para vermelho ou 'b' para azul.
        :param posicao: (linha, coluna) opcional para verificar capturas de uma peça específica.
        :return: True se houver capturas disponíveis, False caso contrário.
        """
        direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        if posicao:
            linhas, colunas = [posicao[0]], [posicao[1]]
        else:
            linhas, colunas = range(self.linhas), range(self.colunas)

        for linha in linhas:
            for coluna in colunas:
                if self.configuracao_inicial[linha][coluna] == jogador: # Changed self.configuracao to self.configuracao_inicial
                    for d_linha, d_coluna in direcoes:
                        l_alvo, c_alvo = linha + d_linha, coluna + d_coluna
                        l_captura, c_captura = linha + 2 * d_linha, coluna + 2 * d_coluna
                        if (
                            0 <= l_alvo < self.linhas and 0 <= c_alvo < self.colunas and
                            0 <= l_captura < self.linhas and 0 <= c_captura < self.colunas and
                            self.configuracao_inicial[l_alvo][c_alvo] not in (jogador, "-") and # Changed self.configuracao to self.configuracao_inicial
                            self.configuracao_inicial[l_captura][c_captura] == "-" # Changed self.configuracao to self.configuracao_inicial
                        ):
                            return True
        return False