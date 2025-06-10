# MiniMax/gerador_movimentos.py

from typing import List, Tuple, Dict
from copy import deepcopy

# Tipos para clareza
State = List[List[str]]
Position = Tuple[int, int]
Move = List[Position]  # Um movimento é um caminho: [(origem), (destino1), (destino2), ...]

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

def is_valid_pos(lin: int, col: int) -> bool:
    """Verifica se uma posição (lin, col) está dentro dos limites do tabuleiro 5x9."""
    return 0 <= lin < 5 and 0 <= col < 9

def is_strong_intersection(lin: int, col: int) -> bool:
    """Verifica se uma interseção é forte (permite movimentos diagonais)."""
    return (lin + col) % 2 == 0

def aplicar_movimento(state: State, move: Move, player: str) -> Tuple[State, List[Position]]:
    new_state = deepcopy(state)
    opponent = 'b' if player == 'v' else 'v'
    total_captured_pieces = []

    for i in range(len(move) - 1):
        start_pos, end_pos = move[i], move[i+1]
        
        if not is_valid_pos(*start_pos) or not is_valid_pos(*end_pos): continue

        piece_to_move = new_state[start_pos[0]][start_pos[1]]
        new_state[start_pos[0]][start_pos[1]] = '-'
        new_state[end_pos[0]][end_pos[1]] = piece_to_move
        
        d_lin, d_col = end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]

        # Captura por APROXIMAÇÃO
        pos = (end_pos[0] + d_lin, end_pos[1] + d_col)
        if is_valid_pos(*pos) and new_state[pos[0]][pos[1]] == opponent:
            while is_valid_pos(*pos) and new_state[pos[0]][pos[1]] == opponent:
                total_captured_pieces.append(pos)
                new_state[pos[0]][pos[1]] = '-'
                pos = (pos[0] + d_lin, pos[1] + d_col)

        # Captura por AFASTAMENTO
        pos = (start_pos[0] - d_lin, start_pos[1] - d_col)
        if is_valid_pos(*pos) and new_state[pos[0]][pos[1]] == opponent:
            while is_valid_pos(*pos) and new_state[pos[0]][pos[1]] == opponent:
                total_captured_pieces.append(pos)
                new_state[pos[0]][pos[1]] = '-'
                pos = (pos[0] - d_lin, pos[1] - d_col)
                
    return new_state, total_captured_pieces

def _get_capture_continuations(state: State, player: str, piece_pos: Position, visited_path: List[Position], last_direction: Position) -> List[Move]:
    """Função recursiva para encontrar continuações de uma cadeia de captura."""
    continuations = []
    opponent = 'b' if player == 'v' else 'v'
    
    possible_directions = DIRECTIONS if is_strong_intersection(*piece_pos) else DIRECTIONS[1::2]

    for d_lin, d_col in possible_directions:
        current_direction = (d_lin, d_col)
        if current_direction == last_direction or current_direction == (-last_direction[0], -last_direction[1]):
            continue

        # Captura por Aproximação
        target_pos = (piece_pos[0] + d_lin, piece_pos[1] + d_col)
        capture_check_pos = (target_pos[0] + d_lin, target_pos[1] + d_col)
        if is_valid_pos(*target_pos) and target_pos not in visited_path and state[target_pos[0]][target_pos[1]] == '-' and is_valid_pos(*capture_check_pos) and state[capture_check_pos[0]][capture_check_pos[1]] == opponent:
            temp_state, _ = aplicar_movimento(state, [piece_pos, target_pos], player)
            sub_chains = _get_capture_continuations(temp_state, player, target_pos, visited_path + [target_pos], current_direction)
            if not sub_chains:
                continuations.append([target_pos])
            else:
                for chain in sub_chains:
                    continuations.append([target_pos] + chain)

        # Captura por Afastamento
        target_pos = (piece_pos[0] + d_lin, piece_pos[1] + d_col)
        capture_check_pos = (piece_pos[0] - d_lin, piece_pos[1] - d_col)
        if is_valid_pos(*target_pos) and target_pos not in visited_path and state[target_pos[0]][target_pos[1]] == '-' and is_valid_pos(*capture_check_pos) and state[capture_check_pos[0]][capture_check_pos[1]] == opponent:
            temp_state, _ = aplicar_movimento(state, [piece_pos, target_pos], player)
            sub_chains = _get_capture_continuations(temp_state, player, target_pos, visited_path + [target_pos], current_direction)
            if not sub_chains:
                continuations.append([target_pos])
            else:
                for chain in sub_chains:
                    continuations.append([target_pos] + chain)

    return continuations


def generate_moves(state: State, player: str) -> List[Move]:
    """
    Gera todos os movimentos legais para um jogador.
    Implementa a regra de captura obrigatória: se capturas existem, apenas elas são retornadas.
    """
    capture_moves = []
    
    # 1. Identificar TODAS as capturas iniciais possíveis
    for r in range(5):
        for c in range(9):
            if state[r][c] == player:
                continuations = _get_capture_continuations(state, player, (r, c), [(r,c)], (0,0))
                for chain in continuations:
                    capture_moves.append([(r,c)] + chain)

    # 2. Se houver movimentos de captura, retorne-os
    if capture_moves:
        return capture_moves

    # 3. Se não houver capturas, gere movimentos normais (não capturantes)
    non_capture_moves = []
    for r in range(5):
        for c in range(9):
            if state[r][c] == player:
                possible_directions = DIRECTIONS if is_strong_intersection(r, c) else DIRECTIONS[1::2]
                for d_lin, d_col in possible_directions:
                    target_pos = (r + d_lin, c + d_col)
                    if is_valid_pos(*target_pos) and state[target_pos[0]][target_pos[1]] == '-':
                        non_capture_moves.append([(r, c), target_pos])
    
    return non_capture_moves


def aplicar_movimento(state: State, move: Move, player: str) -> Tuple[State, List[Position]]:
    """
    Aplica um movimento (que pode ser uma cadeia) a um estado do tabuleiro.
    Retorna o novo estado e uma lista de peças capturadas.
    """
    new_state = deepcopy(state)
    opponent = 'b' if player == 'v' else 'v'
    total_captured_pieces = []

    # Um movimento é uma lista de posições, ex: [(r1,c1), (r2,c2), (r3,c3)]
    # Iteramos sobre os segmentos do caminho, ex: (r1,c1)->(r2,c2), depois (r2,c2)->(r3,c3)
    for i in range(len(move) - 1):
        start_pos = move[i]
        end_pos = move[i+1]

        # Mover a peça
        piece_to_move = new_state[start_pos[0]][start_pos[1]]
        new_state[start_pos[0]][start_pos[1]] = '-'
        new_state[end_pos[0]][end_pos[1]] = piece_to_move
        
        d_lin = end_pos[0] - start_pos[0]
        d_col = end_pos[1] - start_pos[1]

        # Lógica de captura por APROXIMAÇÃO
        approach_capture_pos = (end_pos[0] + d_lin, end_pos[1] + d_col)
        if is_valid_pos(*approach_capture_pos) and new_state[approach_capture_pos[0]][approach_capture_pos[1]] == opponent:
            curr_pos = approach_capture_pos
            while is_valid_pos(*curr_pos) and new_state[curr_pos[0]][curr_pos[1]] == opponent:
                total_captured_pieces.append(curr_pos)
                new_state[curr_pos[0]][curr_pos[1]] = '-'
                curr_pos = (curr_pos[0] + d_lin, curr_pos[1] + d_col)

        # Lógica de captura por AFASTAMENTO
        withdrawal_capture_pos = (start_pos[0] - d_lin, start_pos[1] - d_col)
        if is_valid_pos(*withdrawal_capture_pos) and new_state[withdrawal_capture_pos[0]][withdrawal_capture_pos[1]] == opponent:
            curr_pos = withdrawal_capture_pos
            while is_valid_pos(*curr_pos) and new_state[curr_pos[0]][curr_pos[1]] == opponent:
                total_captured_pieces.append(curr_pos)
                new_state[curr_pos[0]][curr_pos[1]] = '-'
                curr_pos = (curr_pos[0] - d_lin, curr_pos[1] - d_col)

    return new_state, total_captured_pieces
