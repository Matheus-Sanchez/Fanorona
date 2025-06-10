from typing import Optional, List, Tuple
import math
from .gerador_movimentos import State, Move, generate_moves, aplicar_movimento
from .alpha_beta import alpha_beta_search, TranspositionTable, init_zobrist
from concurrent.futures import ThreadPoolExecutor

# --- FUNÇÃO ORIGINAL (SINGLE-THREADED) ---
def escolher_movimento_ia(state: State, player: str, depth: int, verbose: bool = True) -> Optional[Move]:
    """
    Versão original de thread única para a busca da IA.
    """
    init_zobrist()
    tt = TranspositionTable()
    
    best_move = None
    moves = generate_moves(state, player)
    if not moves:
        return None

    opponent = 'b' if player == 'v' else 'v'
    is_maximizing = (player == 'v')
    best_value = -math.inf if is_maximizing else math.inf

    for move in moves:
        next_state, _ = aplicar_movimento(state, move, player)
        board_value = alpha_beta_search(next_state, opponent, depth - 1, -math.inf, math.inf, not is_maximizing, tt, set())
        
        if is_maximizing:
            if board_value > best_value:
                best_value = board_value
                best_move = move
        else:
            if board_value < best_value:
                best_value = board_value
                best_move = move
    
    if verbose:
        print(f"IA ({player}) escolheu o movimento: {best_move} com valor: {best_value}")
        
    return best_move

# --- NOVA FUNÇÃO PARALELA ---
def avaliar_movimento(args):
    """Função auxiliar para ser usada pelo ThreadPoolExecutor."""
    move, state, player, depth, opponent, is_maximizing = args
    tt = TranspositionTable() # Cada thread pode ter sua própria tabela ou compartilhar uma (simples aqui)
    next_state, _ = aplicar_movimento(state, move, player)
    # A busca para o próximo nível inverte o jogador maximizador
    return move, alpha_beta_search(next_state, opponent, depth - 1, -math.inf, math.inf, not is_maximizing, tt, set())

def escolher_movimento_ia_paralelo(state: State, player: str, depth: int, num_threads: int, verbose: bool = True) -> Optional[Move]:
    """
    Versão paralela que distribui a avaliação dos movimentos iniciais entre várias threads.
    """
    init_zobrist()
    
    moves = generate_moves(state, player)
    if not moves:
        return None

    opponent = 'b' if player == 'v' else 'v'
    is_maximizing = (player == 'v')
    
    # Prepara os argumentos para cada tarefa
    tasks = [(move, state, player, depth, opponent, is_maximizing) for move in moves]

    best_move = None
    best_value = -math.inf if is_maximizing else math.inf

    # Usa um ThreadPoolExecutor para rodar as avaliações em paralelo
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = list(executor.map(avaliar_movimento, tasks))

    # Encontra o melhor resultado a partir dos que retornaram das threads
    for move, value in results:
        if is_maximizing:
            if value > best_value:
                best_value = value
                best_move = move
        else:
            if value < best_value:
                best_value = value
                best_move = move
    
    if verbose:
        print(f"IA ({player}) escolheu o movimento: {best_move} com valor: {best_value}")

    return best_move