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
        peca = configuracao_inicial[nova_linha][nova_coluna]
        oponente = "b" if peca == "v" else "v"
        
        # Verificar se existem peças para capturar em ambas direções
        pecas_aproximacao = self.verificar_pecas_captura(nova_linha, nova_coluna, direcao_linha, direcao_coluna, oponente, configuracao_inicial)
        pecas_afastamento = self.verificar_pecas_captura(linha_atual, coluna_atual, -direcao_linha, -direcao_coluna, oponente, configuracao_inicial)
        
        # Se não há peças para capturar, retornar
        if not pecas_aproximacao and not pecas_afastamento:
            # Limpar seleção mesmo sem capturas
            if hasattr(self, 'movimentacao_ref'):
                self.movimentacao_ref.limpar_selecao()
            return
        
        # Se só há um tipo de captura possível, executar automaticamente
        if pecas_aproximacao and not pecas_afastamento:
            self.executar_captura(nova_linha, nova_coluna, direcao_linha, direcao_coluna, oponente, configuracao_inicial, tela)
            if hasattr(self, 'movimentacao_ref'):
                self.movimentacao_ref.limpar_selecao()
            return
        elif not pecas_aproximacao and pecas_afastamento:
            self.executar_captura(linha_atual, coluna_atual, -direcao_linha, -direcao_coluna, oponente, configuracao_inicial, tela)
            if hasattr(self, 'movimentacao_ref'):
                self.movimentacao_ref.limpar_selecao()
            return
        
        # Se há dois tipos de captura possíveis, mostrar opções para o jogador
        self.mostrar_opcoes_captura(nova_linha, nova_coluna, linha_atual, coluna_atual, 
                                direcao_linha, direcao_coluna, oponente, configuracao_inicial, tela)

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
        
        # Limpar seleção e possíveis movimentos na classe Movimentacao
        if hasattr(self, 'movimentacao_ref'):
            self.movimentacao_ref.limpar_selecao()
        
        # Resetar estados
        self.escolha_captura_ativa = False

        # Redesenhar o tabuleiro completamente para garantir que tudo esteja atualizado visualmente
        self.desenhar_pecas(tela)


    def executar_captura(self, linha_base, coluna_base, direcao_linha, direcao_coluna, oponente, configuracao_inicial, tela):
        """Executa a captura na direção especificada"""
        linha_temp = linha_base + direcao_linha
        coluna_temp = coluna_base + direcao_coluna
        captura_realizada = False
        
        while 0 <= linha_temp < self.linhas and 0 <= coluna_temp < self.colunas:
            if configuracao_inicial[linha_temp][coluna_temp] == oponente:
                configuracao_inicial[linha_temp][coluna_temp] = "-"
                self.pecas[linha_temp][coluna_temp] = None
                captura_realizada = True
            else:
                break
            linha_temp += direcao_linha
            coluna_temp += direcao_coluna
        
        # Resetar estado de escolha
        self.escolha_captura_ativa = False
        
        # Redesenhar completamente
        self.desenhar_pecas(tela)
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
        if hasattr(self, 'escolha_captura_ativa') and self.escolha_captura_ativa:
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
        if hasattr(self, 'escolha_captura_ativa') and self.escolha_captura_ativa:
            for botao_info in self.opcoes_captura.values():
                x, y = botao_info['pos']
                largura, altura = botao_info['size']
                
                if x <= pos_x <= x + largura and y <= pos_y <= y + altura:
                    botao_info['action']()  # Executar a ação associada ao botão
                    self.escolha_captura_ativa = False  # Desativar os botões após a escolha
                    return True
        
        
        return False
    