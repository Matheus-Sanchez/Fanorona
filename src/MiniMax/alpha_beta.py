from typing import Tuple
from .gerador_movimentos import generate_moves
from .heuristica         import evaluate_state
from copy import deepcopy

State = list[list[str]]
Move = Tuple[Tuple[int, int], Tuple[int, int]]

def aplicar_movimento(state: State, move: Move, player: str) -> State:
    new_state = deepcopy(state)
    (i1, j1), (i2, j2) = move
    new_state[i2][j2] = player
    new_state[i1][j1] = "-"
    dl = i2 - i1
    dc = j2 - j1
    if dl != 0:
        dl //= abs(dl)
    if dc != 0:
        dc //= abs(dc)
    i, j = i1 + dl, j1 + dc
    opponent = "b" if player == "v" else "v"
    while 0 <= i < len(state) and 0 <= j < len(state[0]) and new_state[i][j] == opponent:
        new_state[i][j] = "-"
        i += dl
        j += dc
    return new_state


def alpha_beta_search(state: State, player: str, move: Move, depth: int) -> float:
    next_state = aplicar_movimento(state, move, player)
    opponent = "b" if player == "v" else "v"
    return alphabeta(next_state, opponent, depth - 1, float("-inf"), float("inf"), maximizing=False)


def alphabeta(state: State, player: str, depth: int,
              alpha: float, beta: float, maximizing: bool) -> float:
    if depth == 0:
        return evaluate_state(state, player)

    moves = generate_moves(state, player)
    if not moves:
        return evaluate_state(state, player)

    opponent = "b" if player == "v" else "v"

    if maximizing:
        value = float("-inf")
        for move in moves:
            next_state = aplicar_movimento(state, move, player)
            value = max(value, alphabeta(next_state, opponent, depth - 1, alpha, beta, False))
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # beta cut-off
        return value
    else:
        value = float("inf")
        for move in moves:
            next_state = aplicar_movimento(state, move, player)
            value = min(value, alphabeta(next_state, opponent, depth - 1, alpha, beta, True))
            beta = min(beta, value)
            if beta <= alpha:
                break  # alpha cut-off
        return value
