import pygame

class Captura:
    def __init__(self, linhas, colunas, tamanho_celula, offset_x, offset_y, configuracao_inicial):
        self.linhas = linhas
        self.colunas = colunas
        self.tamanho_celula = tamanho_celula
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.configuracao_inicial = configuracao_inicial
    
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
    