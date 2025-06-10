# MiniMax/heuristica.py

from typing import List, Tuple
from .gerador_movimentos import generate_moves, is_strong_intersection

State = List[List[str]]

# Pesos para cada componente da heurística. Podem ser ajustados para otimizar o comportamento da IA.
W_MATERIAL = 100.0
W_MOBILITY = 1.0
W_CONTROL = 10.0

def piece_difference(state: State, player: str) -> int:
    """Calcula a diferença de material (contagem de peças)."""
    opponent = 'b' if player == 'v' else 'v'
    player_pieces = sum(row.count(player) for row in state)
    opponent_pieces = sum(row.count(opponent) for row in state)
    return player_pieces - opponent_pieces

def mobility(state: State, player: str) -> int:
    """
    Calcula a mobilidade, ou seja, o número total de movimentos legais disponíveis.
    Isso dá uma medida do controle e das opções do jogador.
    """
    return len(generate_moves(state, player))

def control_of_strong_intersections(state: State, player: str) -> int:
    """
    Calcula o controle de interseções fortes. Peças nesses pontos são mais poderosas.
    """
    opponent = 'b' if player == 'v' else 'v'
    control_score = 0
    for r in range(5):
        for c in range(9):
            if is_strong_intersection(r, c):
                if state[r][c] == player:
                    control_score += 1
                elif state[r][c] == opponent:
                    control_score -= 1
    return control_score

def evaluate_state(state: State, player: str) -> float:
    """
    Função de avaliação principal que combina várias métricas.
    O sinal é ajustado para que valores positivos sejam sempre bons para o jogador 'v' (vermelho).
    """
    # Verifica condições de vitória/derrota
    player_moves = generate_moves(state, player)
    opponent = 'b' if player == 'v' else 'v'
    opponent_moves = generate_moves(state, opponent)

    if not opponent_moves:
        return float('inf') # Vitória
    if not player_moves:
        return float('-inf') # Derrota

    # Combinação ponderada de componentes heurísticos
    eval_material = W_MATERIAL * piece_difference(state, player)
    eval_mobility = W_MOBILITY * (mobility(state, player) - mobility(state, opponent))
    eval_control = W_CONTROL * control_of_strong_intersections(state, player)

    total_evaluation = eval_material + eval_mobility + eval_control
    
    # A avaliação deve ser do ponto de vista do jogador MAX (vermelho 'v')
    # Se o jogador atual for 'b', invertemos a pontuação.
    return total_evaluation if player == 'v' else -total_evaluation
