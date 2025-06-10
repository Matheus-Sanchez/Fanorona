# src/main.py

import sys
import os
import pygame
import random
import time

# --- Bloco de Importação (Mantido como no seu original) ---
# Adiciona a pasta 'src' ao caminho do Python para que ele encontre os módulos.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from Tabuleiro import Tabuleiro
from Pecas import GerenciadorPecas
from Movimentacao import Movimentacao
from Captura import Captura
from MiniMax.ia import escolher_movimento_ia
from MiniMax.gerador_movimentos import generate_moves
from Q_Learning.ia import escolher_movimento_qlearning
from Q_Learning.train import train_agent

# --- Constantes ---
LARGURA, ALTURA = 1000, 600
pygame.init()
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Fanorona")

FONTE = pygame.font.Font(None, 36)
FONTE_GRANDE = pygame.font.Font(None, 50)
FONTE_MENU = pygame.font.Font(None, 40)

COR_V = (195, 31, 9)
COR_B = (1, 151, 246)
COR_BRANCO = (255, 255, 255)
COR_PRETO = (0, 0, 0)
COR_CAMINHO_CADEIA = (100, 100, 100)

def menu_inicial(tela):
    imagem_fundo = pygame.image.load(os.path.join("assets", "1.png"))
    imagem_fundo = pygame.transform.scale(imagem_fundo, (LARGURA, ALTURA))
    opcoes = {
        "1": "Humano vs Humano", "2": "Humano vs MiniMax", "3": "MiniMax vs MiniMax",
        "4": "Humano vs Q-Learning", "5": "MiniMax vs Q-Learning", "6": "Treinar IA (Q-Learning)",
        "0": "Manual"
    }
    while True:
        tela.blit(imagem_fundo, (0, 0))
        titulo = FONTE_GRANDE.render("Fanorona - Menu Principal", True, COR_BRANCO)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 50))
        y_pos = 150
        for key, text in opcoes.items():
            opcao_texto = FONTE_MENU.render(f"[{key}] {text}", True, COR_BRANCO)
            tela.blit(opcao_texto, (LARGURA // 2 - opcao_texto.get_width() // 2, y_pos))
            y_pos += 50
        texto_sair = FONTE_MENU.render("[ESC] Sair do Jogo", True, COR_BRANCO)
        tela.blit(texto_sair, (LARGURA // 2 - texto_sair.get_width() // 2, y_pos + 20))
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1: return "h_vs_h"
                if evento.key == pygame.K_2: return "h_vs_mm"
                if evento.key == pygame.K_3: return "mm_vs_mm"
                if evento.key == pygame.K_4: return "h_vs_q"
                if evento.key == pygame.K_5: return "mm_vs_q"
                if evento.key == pygame.K_6: return "train_q"
                if evento.key == pygame.K_0: exibir_imagem(tela)  # Chama a função de exibir imagem/manual ilustrado

def escolher_cor(tela):
    while True:
        tela.fill(COR_PRETO)
        texto_titulo = FONTE_GRANDE.render("Escolha sua cor", True, COR_BRANCO)
        tela.blit(texto_titulo, (LARGURA//2 - texto_titulo.get_width()//2, 150))
        texto_v = FONTE_MENU.render("[V] para Vermelho (Começa)", True, COR_V)
        tela.blit(texto_v, (LARGURA//2 - texto_v.get_width()//2, 250))
        texto_b = FONTE_MENU.render("[B] para Azul (Segundo a jogar)", True, COR_B)
        tela.blit(texto_b, (LARGURA//2 - texto_b.get_width()//2, 310))
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_v: return 'v'
                if evento.key == pygame.K_b: return 'b'
def desenhar_indicador_turno(jogador_atual, tipos_jogadores, ia_pensando, ia_frame):
    """Desenha o texto que indica de quem é a vez."""
    tipo_jogador_v = tipos_jogadores.get('v', 'HUMANO')
    tipo_jogador_b = tipos_jogadores.get('b', 'HUMANO')

    texto_v = f"Vermelho ({tipo_jogador_v})"
    texto_b = f"Azul ({tipo_jogador_b})"
    
    texto_str = f"Turno: {texto_v if jogador_atual == 'v' else texto_b}"
    cor = COR_V if jogador_atual == 'v' else COR_B

    if ia_pensando:
        texto_str += " pensando" + "." * (ia_frame % 4)
        
    texto_turno = FONTE.render(texto_str, True, cor)
    TELA.blit(texto_turno, (10, 10))
    
def exibir_tela_final(mensagem):
    texto_vencedor = FONTE_GRANDE.render(mensagem, True, COR_V)
    rect = texto_vencedor.get_rect(center=(LARGURA // 2, ALTURA // 2))
    fundo = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    fundo.fill((0, 0, 0, 180))
    TELA.blit(fundo, (0, 0))
    TELA.blit(texto_vencedor, rect)
    pygame.display.flip()
    pygame.time.wait(4000)

def animar_movimento(tela, movimentacao, pecas, origem, destino, cor_peca, delay=400):
    tabuleiro = movimentacao.gerenciador_pecas.tabuleiro_ref if hasattr(movimentacao.gerenciador_pecas, 'tabuleiro_ref') else Tabuleiro(LARGURA, ALTURA)
    offset_x, offset_y, tamanho_celula = pecas.offset_x, pecas.offset_y, pecas.tamanho_celula
    x_origem = offset_x + origem[1] * tamanho_celula + tamanho_celula // 2
    y_origem = offset_y + origem[0] * tamanho_celula + tamanho_celula // 2
    x_destino = offset_x + destino[1] * tamanho_celula + tamanho_celula // 2
    y_destino = offset_y + destino[0] * tamanho_celula + tamanho_celula // 2
    passos = 20
    peca_animada_obj = pecas.pecas[origem[0]][origem[1]]
    if peca_animada_obj: pecas.pecas[origem[0]][origem[1]] = None
    for i in range(passos + 1):
        x_atual = int(x_origem + (x_destino - x_origem) * i / passos)
        y_atual = int(y_origem + (y_destino - y_origem) * i / passos)
        tela.fill(COR_BRANCO)
        tabuleiro.desenhar(tela)
        pecas.desenhar_pecas(tela)
        pygame.draw.circle(tela, cor_peca, (x_atual, y_atual), 20)
        pygame.display.flip()
        pygame.time.delay(delay // passos)
    if peca_animada_obj: pecas.pecas[origem[0]][origem[1]] = peca_animada_obj

def exibir_imagem(tela):
    """Exibe uma imagem/manual ilustrado e volta ao menu ao pressionar ESC."""
    imagem = pygame.image.load("./assets/2.png")  
    imagem = pygame.transform.scale(imagem, (800, 500))  # Ajusta o tamanho da imagem
    rodando = True
    while rodando:
        tela.fill((0, 0, 0))
        tela.blit(imagem, (100, 50))
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return  # Volta para o menu

def jogo(modo):
    tipos_jogadores = {'v': 'HUMANO', 'b': 'HUMANO'}
    if modo in ["h_vs_mm", "h_vs_q"]:
        cor_humano = escolher_cor(TELA)
        cor_ia = 'b' if cor_humano == 'v' else 'v'
        tipos_jogadores[cor_humano] = 'HUMANO'
        tipos_jogadores[cor_ia] = 'MINIMAX' if modo == "h_vs_mm" else 'QLEARNING'
    elif modo == "mm_vs_mm": tipos_jogadores.update({'v': 'MINIMAX', 'b': 'MINIMAX'})
    elif modo == "mm_vs_q": tipos_jogadores.update({'v': 'MINIMAX', 'b': 'QLEARNING'})

    configuracao_inicial = [["v"]*9, ["v"]*9, ["b", "v", "b", "v", "-", "b", "v", "b", "v"], ["b"]*9, ["b"]*9]
    tabuleiro = Tabuleiro(LARGURA, ALTURA)
    pecas = GerenciadorPecas(5, 9, 100, (LARGURA - 900) // 2, (ALTURA - 500) // 2, configuracao_inicial)
    captura = Captura(5, 9, 100, (LARGURA - 900) // 2, (ALTURA - 500) // 2, configuracao_inicial)
    movimentacao = Movimentacao(5, 9, 100, (LARGURA - 900) // 2, (ALTURA - 500) // 2, pecas, configuracao_inicial)
    
    captura.set_gerenciador_pecas(pecas); captura.set_tabuleiro(tabuleiro); movimentacao.set_captura_ref(captura)
    if hasattr(movimentacao.gerenciador_pecas, 'tabuleiro_ref') is False: movimentacao.gerenciador_pecas.tabuleiro_ref = tabuleiro
    
    jogador_atual = "v"
    mensagem_vencedor = None
    rodando = True
    clock = pygame.time.Clock()
    
    botao_menu_rect = pygame.Rect(LARGURA - 180, 20, 160, 40)
    
    while rodando:
        TELA.fill(COR_BRANCO)
        tabuleiro.desenhar(TELA)
        pecas.desenhar_pecas(TELA)
        
        tipo_jogador_atual = tipos_jogadores[jogador_atual]
        ia_pensando = tipo_jogador_atual != 'HUMANO'

        # --- Lógica de Destaques Visuais ---
        if not captura.captura_em_cadeia_ativa and movimentacao.captura_ref and movimentacao.existe_captura_geral(jogador_atual):
            movimentacao.destacar_pecas_com_captura(TELA, jogador_atual)
        if movimentacao.peca_selecionada:
            movimentacao.desenhar_movimentos(TELA); movimentacao.desenhar_borda_selecao(TELA)
        if captura.captura_em_cadeia_ativa and captura.posicoes_visitadas:
            for pos in captura.posicoes_visitadas:
                centro_x = pecas.offset_x + pos[1] * pecas.tamanho_celula + pecas.tamanho_celula // 2
                centro_y = pecas.offset_y + pos[0] * pecas.tamanho_celula + pecas.tamanho_celula // 2
                pygame.draw.circle(TELA, COR_CAMINHO_CADEIA, (centro_x, centro_y), 10)
        if captura.escolha_captura_ativa: captura.desenhar_botoes_captura(TELA)
        
        desenhar_indicador_turno(jogador_atual, tipos_jogadores, ia_pensando, int(time.time() * 2) % 4)

        if not mensagem_vencedor:
            if not any("v" in row for row in configuracao_inicial): mensagem_vencedor = "Jogador Azul (B) Venceu!"
            elif not any("b" in row for row in configuracao_inicial): mensagem_vencedor = "Jogador Vermelho (V) Venceu!"
        
        if mensagem_vencedor:
            exibir_tela_final(mensagem_vencedor); return

        # Botão "Voltar ao Menu"
        pygame.draw.rect(TELA, (200, 80, 80), botao_menu_rect)
        texto_menu = FONTE.render("Voltar ao Menu", True, (255, 255, 255))
        TELA.blit(texto_menu, (botao_menu_rect.x + botao_menu_rect.width // 2 - texto_menu.get_width() // 2, botao_menu_rect.y + 8))

        if tipo_jogador_atual != 'HUMANO' and not captura.escolha_captura_ativa:
            pygame.display.flip() # Atualiza a tela para mostrar "pensando..."
            estado_atual = [list(l) for l in configuracao_inicial]
            melhor_jogada = escolher_movimento_ia(estado_atual, jogador_atual, depth=3) if tipo_jogador_atual == 'MINIMAX' else escolher_movimento_qlearning(estado_atual, jogador_atual)
            
            if not melhor_jogada:
                movimentos_possiveis = generate_moves(estado_atual, jogador_atual)
                if movimentos_possiveis: melhor_jogada = movimentos_possiveis[0]
                else: mensagem_vencedor = f"Jogador {'B' if jogador_atual == 'v' else 'V'} venceu!"; continue

            if melhor_jogada:
                cor_peca = COR_V if jogador_atual == 'v' else COR_B
                for i in range(len(melhor_jogada) - 1):
                    origem, destino = melhor_jogada[i], melhor_jogada[i+1]
                    animar_movimento(TELA, movimentacao, pecas, origem, destino, cor_peca)
                    movimentacao.peca_selecionada = origem
                    movimentacao.mover_peca(destino[0], destino[1], jogador_atual)


                    # --- LÓGICA DE ESCOLHA AUTOMÁTICA DA IA (DENTRO DE MAIN.PY) ---
                    if captura.escolha_captura_ativa:
                        oponente = 'b' if jogador_atual == 'v' else 'v'
                        d_linha = destino[0] - origem[0]
                        d_coluna = destino[1] - origem[1]
                        norm_dl = d_linha // abs(d_linha) if d_linha != 0 else 0
                        norm_dc = d_coluna // abs(d_coluna) if d_coluna != 0 else 0

                        # Verifica as duas opções de captura
                        pecas_aprox = captura.verificar_pecas_captura(destino[0], destino[1], norm_dl, norm_dc, oponente, configuracao_inicial)
                        pecas_afast = captura.verificar_pecas_captura(origem[0], origem[1], -norm_dl, -norm_dc, oponente, configuracao_inicial)
                        
                        # Executa a captura com mais peças
                        if len(pecas_aprox) >= len(pecas_afast):
                            captura.finalizar_movimento_com_captura(destino[0], destino[1], norm_dl, norm_dc, oponente, configuracao_inicial, TELA)
                        else:
                            captura.finalizar_movimento_com_captura(origem[0], origem[1], -norm_dl, -norm_dc, oponente, configuracao_inicial, TELA)
                
                movimentacao.limpar_selecao()
                if not captura.captura_em_cadeia_ativa: jogador_atual = "b" if jogador_atual == "v" else "v"
        else: # Lógica para jogador HUMANO
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT: rodando = False
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE: return
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    if botao_menu_rect.collidepoint(evento.pos):
                        return  # Volta ao menu principal
                    if not ia_pensando:
                        x, y = evento.pos
                        if captura.escolha_captura_ativa:
                            if captura.processar_clique_botoes(x, y):
                                if not captura.captura_em_cadeia_ativa: jogador_atual = "b" if jogador_atual == "v" else "v"
                        else:
                            movimento_realizado = movimentacao.processar_clique(x, y, jogador_atual)
                            if movimento_realizado and not captura.captura_em_cadeia_ativa:
                                jogador_atual = "b" if jogador_atual == "v" else "v"

        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    sys.exit()

def main():
    while True:
        modo_escolhido = menu_inicial(TELA)
        if modo_escolhido == "train_q":
            print("Iniciando treinamento da IA. Isso pode levar muito tempo.")
            try: train_agent()
            except Exception as e: print(f"Ocorreu um erro: {e}")
            exibir_tela_final("Treinamento concluído!")
        elif modo_escolhido: jogo(modo_escolhido)
        else: break

if __name__ == "__main__":
    main()