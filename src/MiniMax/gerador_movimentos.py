"""
Gera movimentos legais para Fanorona a partir de um estado e lista opcional de peças.
Implementa as regras de movimento e captura obrigatória (aproximação, afastamento, cadeias).
"""
from typing import List, Tuple, Optional

State = List[List[str]]
Move = Tuple[Tuple[int, int], Tuple[int, int]]  # ((lin_atual, col_atual), (lin_nova, col_nova))

DIRECOES_8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
DIRECOES_4 = [(-1, 0), (0, -1), (0, 1), (1, 0)]


def verificar_pecas_captura(state: State, linha: int, coluna: int,
                            dir_linha: int, dir_coluna: int, oponente: str) -> List[Tuple[int,int]]:
    """
    Verifica se há peças do oponente na direção especificada até encontrar um vazio.
    Retorna lista de coordenadas capturáveis.
    """
    capturaveis = []
    i, j = linha + dir_linha, coluna + dir_coluna
    while 0 <= i < len(state) and 0 <= j < len(state[0]):
        if state[i][j] == oponente:
            capturaveis.append((i, j))
        else:
            break
        i += dir_linha
        j += dir_coluna
    return capturaveis


def possiveis_capturas(state: State, linha: int, coluna: int, player: str) -> List[Move]:
    """
    Para uma peça em (linha,coluna), retorna movimentações para casas vazias que resultam em captura.
    """
    oponente = 'b' if player == 'v' else 'v'
    direcoes = DIRECOES_8 if (linha % 2 == coluna % 2) else DIRECOES_4
    moves = []
    for dl, dc in direcoes:
        ni, nj = linha + dl, coluna + dc
        # casa de destino vazia?
        if 0 <= ni < len(state) and 0 <= nj < len(state[0]) and state[ni][nj] == '-':
            # aproximação
            if verificar_pecas_captura(state, ni, nj, dl, dc, oponente):
                moves.append(((linha, coluna), (ni, nj)))
            # afastamento
            if verificar_pecas_captura(state, linha, coluna, -dl, -dc, oponente):
                moves.append(((linha, coluna), (ni, nj)))
    return moves


def possiveis_movimentos(state: State, linha: int, coluna: int, player: str) -> List[Move]:
    """
    Retorna movimentos livres ou de captura obrigatória para a peça em (linha,coluna).
    Se existirem capturas, apenas elas são retornadas.
    """
    # gera movimentos livres
    direcoes = DIRECOES_8 if (linha % 2 == coluna % 2) else DIRECOES_4
    livres = []
    for dl, dc in direcoes:
        ni, nj = linha + dl, coluna + dc
        if 0 <= ni < len(state) and 0 <= nj < len(state[0]) and state[ni][nj] == '-':
            livres.append(((linha, coluna), (ni, nj)))
    # filtra capturas
    caps = possiveis_capturas(state, linha, coluna, player)
    return caps if caps else livres


def generate_moves(state: State, player: str,
                   movable_pieces: Optional[List[Tuple[int,int]]] = None) -> List[Move]:
    """
    Gera lista completa de movimentos para `player` no `state`, opcionalmente limitado a `movable_pieces`.
    """
    # determina quais peças considerar
    peças = movable_pieces if movable_pieces is not None else [
        (i, j) for i, row in enumerate(state) for j, c in enumerate(row) if c == player
    ]
    moves: List[Move] = []
    for i, j in peças:
        moves.extend(possiveis_movimentos(state, i, j, player))
    return moves
