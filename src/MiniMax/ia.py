# MiniMax/ia.py

from typing import Optional, List, Tuple
import math
from .gerador_movimentos import State, Move, generate_moves, aplicar_movimento
from .alpha_beta import alpha_beta_search, TranspositionTable, init_zobrist, compute_hash

def escolher_movimento_ia(state: State, player: str, depth: int) -> Optional[Move]:
    """
    Função de alto nível que orquestra a busca da IA para encontrar o melhor movimento.
    """
    # Inicializa os componentes necessários para a busca
    init_zobrist()
    tt = TranspositionTable()
    
    best_move = None
    
    # Gera os movimentos possíveis a partir da raiz da árvore de busca
    moves = generate_moves(state, player)
    if not moves:
        return None

    opponent = 'b' if player == 'v' else 'v'
    
    # Determina se a IA está maximizando ou minimizando
    # Assumimos que o jogador 'v' (vermelho) é sempre o maximizador
    is_maximizing = (player == 'v')

    if is_maximizing:
        best_value = -math.inf
        for move in moves:
            next_state, _ = aplicar_movimento(state, move, player)
            # A busca para o próximo nível será para o jogador minimizador
            board_value = alpha_beta_search(next_state, opponent, depth - 1, -math.inf, math.inf, False, tt, set())
            if board_value > best_value:
                best_value = board_value
                best_move = move
    else: # Jogador Minimizador ('b', azul)
        best_value = math.inf
        for move in moves:
            next_state, _ = aplicar_movimento(state, move, player)
            # A busca para o próximo nível será para o jogador maximizador
            board_value = alpha_beta_search(next_state, opponent, depth - 1, -math.inf, math.inf, True, tt, set())
            if board_value < best_value:
                best_value = board_value
                best_move = move
                
    print(f"IA ({player}) escolheu o movimento: {best_move} com valor: {best_value}")
    return best_move
