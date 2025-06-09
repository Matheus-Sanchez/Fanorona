from typing import List, Tuple, Optional

State = List[List[str]]
# Move as a sequence of positions for chains; for single move keep two positions
Move = List[Tuple[int, int]]  # [(lin_atual, col_atual), (lin_nova, col_nova), ...]

DIRECOES_8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
DIRECOES_4 = [(-1, 0), (0, -1), (0, 1), (1, 0)]


def generate_moves(state: State, player: str, board_config: Optional[dict] = None,
                   last_move_end_pos: Optional[Tuple[int, int]] = None,
                   visited_during_chain: Optional[List[Tuple[int, int]]] = None,
                   last_direction: Optional[Tuple[int, int]] = None,
                   capturas_apenas: bool = False,
                   active_piece_pos: Optional[Tuple[int, int]] = None) -> List[Move]:  # Add active_piece_pos
    """
    Gera todos os movimentos legais para `player`.
    Capturas obrigatórias: se houver qualquer captura, só retorna cadeias de captura.
    """
    opponent = 'X' if player == 'O' else 'O'  # Make sure your player representation matches ('v', 'b')
    # ... rest of your function
    # You will also need to decide how to use active_piece_pos within this function's logic.
    # For example, if it's meant to restrict move generation to only that piece:
    # if active_piece_pos:
    #     i, j = active_piece_pos
    #     # ... logic to generate moves only for the piece at (i,j) ...
    # else:
    #     # ... your existing logic to iterate through all pieces ...

    all_caps: List[Move] = []
    for i, row in enumerate(state):
        for j, cell in enumerate(row):
            if cell == player:
                caps = possiveis_capturas(state, i, j, opponent, visited=[])
                all_caps.extend(caps)
    if all_caps:
        return all_caps

    moves: List[Move] = []
    for i, row in enumerate(state):
        for j, cell in enumerate(row):
            if cell == player:
                for dr, dc in DIRECOES_8:
                    ni, nj = i + dr, j + dc
                    if 0 <= ni < len(state) and 0 <= nj < len(row) and state[ni][nj] == '-':
                        moves.append([(i, j), (ni, nj)])
    if capturas_apenas:
        capture_moves_only = []
        # Implementar lógica para filtrar apenas os movimentos de captura
        pass  # Placeholder: Implementar lógica de filtragem aqui

    return moves


def possiveis_capturas(state: State, r: int, c: int, opponent: str,
                       visited: List[Tuple[int, int]]) -> List[Move]:
    """
    Retorna todas as cadeias de captura iniciando em (r,c).
    Mantém a mesma peça e não reutiliza posições em `visited`.
    """
    sequences: List[Move] = []
    for dr, dc in DIRECOES_8:
        ni, nj = r + dr, c + dc
        if _valid_capture(state, r, c, dr, dc, opponent, mode='approach', visited=visited):
            new_state, captured = _apply_capture(state, r, c, dr, dc, opponent, mode='approach')
            sub = possiveis_capturas(new_state, ni, nj, opponent, visited + captured)
            if sub:
                for seq in sub:
                    sequences.append([(r, c)] + seq)
            else:
                sequences.append([(r, c), (ni, nj)])
        ri, rj = r - dr, c - dc
        if _valid_capture(state, r, c, dr, dc, opponent, mode='withdrawal', visited=visited):
            new_state, captured = _apply_capture(state, r, c, dr, dc, opponent, mode='withdrawal')
            sub = possiveis_capturas(new_state, ri, rj, opponent, visited + captured)
            if sub:
                for seq in sub:
                    sequences.append([(r, c)] + seq)
            else:
                sequences.append([(r, c), (ri, rj)])
    return sequences


def _valid_capture(state: State, r: int, c: int, dr: int, dc: int,
                   opponent: str, mode: str, visited: List[Tuple[int, int]]) -> bool:
    if mode == 'approach':
        i, j = r + dr, c + dc
    else:
        i, j = r - dr, c - dc
    if not (0 <= i < len(state) and 0 <= j < len(state[0])):
        return False
    return state[i][j] == opponent and (i, j) not in visited


def _apply_capture(state: State, r: int, c: int, dr: int, dc: int,
                   opponent: str, mode: str) -> Tuple[State, List[Tuple[int, int]]]:
    new = [row.copy() for row in state]
    if mode == 'approach':
        dest = (r + dr, c + dc)
        cap = dest
    else:
        dest = (r - dr, c - dc)
        cap = (r + dr, c + dc)
    new[r][c] = '-'
    new[dest[0]][dest[1]] = state[r][c]
    captured: List[Tuple[int, int]] = []
    if new[cap[0]][cap[1]] == opponent:
        new[cap[0]][cap[1]] = '-'
        captured.append(cap)
    return new, captured


def aplicar_movimento(state: State, move: Move, player: str) -> Tuple[State, List[Tuple[int, int]]]:
    """
    Aplica um movimento (ou cadeia) para `player` e retorna novo tabuleiro e lista de capturas.
    Remove peças capturadas por aproximação e afastamento corretamente.
    """
    new_state = [row.copy() for row in state]
    opponent = 'X' if player == 'O' else 'O'
    all_captured: List[Tuple[int, int]] = []
    for idx in range(len(move) - 1):
        src = move[idx]
        dst = move[idx + 1]
        piece = new_state[src[0]][src[1]]
        new_state[src[0]][src[1]] = '-'
        new_state[dst[0]][dst[1]] = piece
        dx, dy = dst[0] - src[0], dst[1] - src[1]
        # Captura aproximação: todas as peças entre src e dst na direção (dx,dy)
        steps = max(abs(dx), abs(dy))
        dir_x = dx//steps if steps else 0
        dir_y = dy//steps if steps else 0
        for step in range(1, steps+1):
            cap = (src[0] + dir_x*step, src[1] + dir_y*step)
            if 0 <= cap[0] < len(state) and 0 <= cap[1] < len(state[0]):
                if new_state[cap[0]][cap[1]] == opponent:
                    new_state[cap[0]][cap[1]] = '-'
                    all_captured.append(cap)
        # Captura afastamento: peça atrás src
        back = (src[0] - dir_x, src[1] - dir_y)
        if 0 <= back[0] < len(state) and 0 <= back[1] < len(state[0]):
            if new_state[back[0]][back[1]] == opponent:
                new_state[back[0]][back[1]] = '-'
                all_captured.append(back)
    return new_state, all_captured
