# MiniMax/alpha_beta.py

import random
from typing import List, Tuple, Dict

# Importando os tipos e funções refatoradas
from .gerador_movimentos import State, Move, generate_moves, aplicar_movimento
from .heuristica import evaluate_state

# --- Zobrist Hashing para Tabelas de Transposição ---
# Dicionários para armazenar os números aleatórios para cada estado possível
zobrist_table = {}
# Inicializado uma vez no início do jogo
def init_zobrist():
    """Inicializa a tabela Zobrist com números aleatórios de 64 bits."""
    # Para cada peça ('v', 'b') em cada casa
    for r in range(5):
        for c in range(9):
            zobrist_table[('v', r, c)] = random.getrandbits(64)
            zobrist_table[('b', r, c)] = random.getrandbits(64)
    # Um valor para indicar de quem é a vez de jogar
    zobrist_table['player_turn'] = random.getrandbits(64)

def compute_hash(state: State, player: str) -> int:
    """Calcula o hash Zobrist completo para um dado estado."""
    h = 0
    if player == 'b':
        h ^= zobrist_table['player_turn']
    for r in range(5):
        for c in range(9):
            if state[r][c] != '-':
                h ^= zobrist_table[(state[r][c], r, c)]
    return h

# --- Tabela de Transposição ---
class TranspositionTable:
    def __init__(self):
        self.table: Dict[int, Dict] = {}

    def store(self, hash_key: int, depth: int, score: float, flag: str, best_move: Move = None):
        """Armazena uma entrada na tabela."""
        # Estratégia de substituição: sempre substitui se a nova busca for mais profunda
        if hash_key not in self.table or self.table[hash_key]['depth'] <= depth:
            self.table[hash_key] = {'depth': depth, 'score': score, 'flag': flag, 'best_move': best_move}

    def probe(self, hash_key: int, depth: int, alpha: float, beta: float) -> Tuple[bool, float, Move]:
        """Consulta a tabela. Retorna (encontrado, pontuação, melhor_movimento)."""
        if hash_key in self.table:
            entry = self.table[hash_key]
            if entry['depth'] >= depth:
                if entry['flag'] == 'EXACT':
                    return True, entry['score'], entry.get('best_move')
                if entry['flag'] == 'LOWERBOUND' and entry['score'] >= beta:
                    return True, entry['score'], entry.get('best_move')
                if entry['flag'] == 'UPPERBOUND' and entry['score'] <= alpha:
                    return True, entry['score'], entry.get('best_move')
        return False, 0.0, None

# --- Algoritmo Alpha-Beta Refatorado ---
def alpha_beta_search(
    state: State,
    player: str,
    depth: int,
    alpha: float,
    beta: float,
    maximizing_player: bool,
    tt: TranspositionTable,
    history: set
) -> float:
    """Implementação do algoritmo Alpha-Beta com Tabelas de Transposição e prevenção de ciclos."""
    
    # 1. Cálculo do Hash e Verificação de Ciclos/Tabela de Transposição
    original_alpha = alpha
    state_hash = compute_hash(state, player)

    # Prevenção de ciclo: se já vimos este estado neste caminho de busca, é um empate.
    if state_hash in history:
        return 0.0

    # Consulta à Tabela de Transposição
    found, score, best_move_from_tt = tt.probe(state_hash, depth, alpha, beta)
    if found:
        return score

    # 2. Condição de Parada (base da recursão)
    if depth == 0:
        return evaluate_state(state, player)

    # 3. Geração e Ordenação de Movimentos
    moves = generate_moves(state, player)
    if not moves: # Fim de jogo
        return evaluate_state(state, player)

    # Ordenação de Movimentos:
    # 1. Tente o melhor movimento da Tabela de Transposição primeiro.
    # 2. Heurística simples: priorize capturas que removem mais peças.
    def move_sort_key(m):
        if best_move_from_tt and m == best_move_from_tt:
            return float('-inf') # Prioridade máxima
        _, captured = aplicar_movimento(state, m, player)
        return -len(captured) # Negativo para ordenar do maior para o menor

    moves.sort(key=move_sort_key)
    
    # 4. Lógica da Busca Recursiva
    history.add(state_hash)
    best_move_found = None
    
    opponent = 'b' if player == 'v' else 'v'

    if maximizing_player: # Jogador 'v' (vermelho)
        max_eval = float('-inf')
        for move in moves:
            next_state, _ = aplicar_movimento(state, move, player)
            evaluation = alpha_beta_search(next_state, opponent, depth - 1, alpha, beta, False, tt, history)
            if evaluation > max_eval:
                max_eval = evaluation
                best_move_found = move
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break # Poda Beta
        history.remove(state_hash)

        # 5. Armazenamento na Tabela de Transposição
        flag = 'EXACT'
        if max_eval <= original_alpha:
            flag = 'UPPERBOUND'
        elif max_eval >= beta:
            flag = 'LOWERBOUND'
        tt.store(state_hash, depth, max_eval, flag, best_move_found)
        
        return max_eval

    else: # Jogador 'b' (azul)
        min_eval = float('inf')
        for move in moves:
            next_state, _ = aplicar_movimento(state, move, player)
            evaluation = alpha_beta_search(next_state, opponent, depth - 1, alpha, beta, True, tt, history)
            if evaluation < min_eval:
                min_eval = evaluation
                best_move_found = move
            beta = min(beta, evaluation)
            if beta <= alpha:
                break # Poda Alfa
        history.remove(state_hash)
        
        # 5. Armazenamento na Tabela de Transposição
        flag = 'EXACT'
        if min_eval <= original_alpha:
            flag = 'UPPERBOUND'
        elif min_eval >= beta:
            flag = 'LOWERBOUND'
        tt.store(state_hash, depth, min_eval, flag, best_move_found)
        
        return min_eval

