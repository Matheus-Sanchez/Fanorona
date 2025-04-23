from typing import List, Tuple
from .gerador_movimentos import possiveis_capturas

State = List[List[str]]
Move = Tuple[Tuple[int, int], Tuple[int, int]]


def piece_difference(state: State, player: str) -> int:
    opp = 'b' if player == 'v' else 'v'
    return sum(r.count(player) for r in state) - sum(r.count(opp) for r in state)


def capture_potential(state: State, player: str) -> int:
    """
    Soma de todas as capturas possíveis (inclui aproximação e afastamento)
    de cada peça do jogador, indicando "armadilhas" e cadeias.
    """
    total = 0
    for i, row in enumerate(state):
        for j, c in enumerate(row):
            if c == player:
                total += len(possiveis_capturas(state, i, j, player))
    return total


def mobility(state: State, player: str) -> int:
    """
    Número de movimentos livres disponíveis (sem captura)
    Quando há captura, mobility fica menor, mas capture_potential
    já reflete o poder de captura.
    """
    # contar apenas movimentos livres: aqueles que não aparecem em possiveis_capturas
    count = 0
    for i, row in enumerate(state):
        for j, c in enumerate(row):
            if c == player:
                # livre = total moves - capturas
                livre = 0
                # direções básicas
                livre = len([m for m in possiveis_capturas(state, i, j, player)
                             if m not in possiveis_capturas(state, i, j, player)])
                count += livre
    return count


def evaluate_state(state: State, player: str) -> float:
    """
    Combina métricas:
      - material (piece_difference)
      - captura potencial (capture_potential)
      - mobilidade livre (mobility)
    Pesos ajustáveis:
      material: 1.5
      captura: 1.0
      mobilidade: 0.3
    """
    pd = piece_difference(state, player)
    cp = capture_potential(state, player)
    mob = mobility(state, player)
    return 1.5 * pd + 1.0 * cp + 0.3 * mob
