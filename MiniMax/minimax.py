from typing import Tuple
from .gerador_movimentos import generate_moves
from .heuristica import evaluate_state
from copy import deepcopy

State = list[list[str]]
Move = Tuple[Tuple[int, int], Tuple[int, int]]

def aplicar_movimento(state: State, move: Move, player: str) -> State:
    """
    Aplica um movimento simples (sem cadeia de captura) a uma cópia do estado.
    Remove a peça da origem, coloca na posição nova.
    """
    new_state = deepcopy(state)
    (i1, j1), (i2, j2) = move
    new_state[i2][j2] = player
    new_state[i1][j1] = "-"
    # Captura simples: remove peças entre origem e destino (se houver)
    dl = i2 - i1
    dc = j2 - j1
    if dl != 0:
        dl //= abs(dl)
    if dc != 0:
        dc //= abs(dc)
    i, j = i1 + dl, j1 + dc
    opponent = "b" if player == "v" else "v"
    while 0 <= i < len(state) and 0 <= j < len(state[0]) and state[i][j] == opponent:
        new_state[i][j] = "-"
        i += dl
        j += dc
    return new_state


def minimax_search(state: State, player: str, move: Move, depth: int) -> float:
    """
    Wrapper para iniciar Minimax a partir de um movimento inicial específico.
    """
    next_state = aplicar_movimento(state, move, player)
    opponent = "b" if player == "v" else "v"
    return minimax(next_state, opponent, depth - 1, maximizing=False)


def minimax(state: State, player: str, depth: int, maximizing: bool) -> float:
    if depth == 0:
        return evaluate_state(state, player)

    moves = generate_moves(state, player)
    if not moves:
        return evaluate_state(state, player)  # sem jogadas = estado ruim

    opponent = "b" if player == "v" else "v"

    if maximizing:
        best = float("-inf")
        for move in moves:
            next_state = aplicar_movimento(state, move, player)
            val = minimax(next_state, opponent, depth - 1, False)
            best = max(best, val)
        return best
    else:
        best = float("inf")
        for move in moves:
            next_state = aplicar_movimento(state, move, player)
            val = minimax(next_state, opponent, depth - 1, True)
            best = min(best, val)
        return best
