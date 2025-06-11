# ======================================================================
# Responsabilidade: Define o ambiente do jogo Fanorona de uma forma que
# o agente de Q-Learning possa entender (estados, ações, recompensas).
# ======================================================================

from copy import deepcopy
from MiniMax.gerador_movimentos import generate_moves, aplicar_movimento

class FanoronaEnv:
    """
    Ambiente de Aprendizado por Reforço adaptado para o jogo Fanorona.
    Permite interações com agentes de Q-Learning.
    """
    Q_AGENT = "q_agent"
    MINIMAX_AGENT = "minimax_agent"

    def __init__(self, max_turns=200):
        self.initial_state = [
            ["v", "v", "v", "v", "v", "v", "v", "v", "v"],
            ["v", "v", "v", "v", "v", "v", "v", "v", "v"],
            ["v", "b", "v", "b", "-", "v", "b", "v", "b"],
            ["b", "b", "b", "b", "b", "b", "b", "b", "b"],
            ["b", "b", "b", "b", "b", "b", "b", "b", "b"]
        ]
        self.max_turns = max_turns
        self.reset()

    def reset(self, starting_player="v"):
        """Reinicia o ambiente."""
        self.state = deepcopy(self.initial_state)
        self.current_player = starting_player
        self.done = False
        self.turn_count = 0
        return deepcopy(self.state)

    def get_state_tuple(self, state=None):
        """Retorna uma versão imutável do estado (para usar como chave em Q-Table)."""
        target = state if state else self.state
        return tuple(map(tuple, target))

    def get_legal_actions(self, state, player):
        """Retorna os movimentos legais do jogador no estado."""
        return generate_moves(state, player)

    def count_pieces(self, state, player):
        return sum(row.count(player) for row in state)

    def step(self, action):
        """
        Executa a ação fornecida pelo jogador atual.
        Retorna: (próximo estado, recompensa, se terminou, info)
        """
        if self.done:
            raise Exception("Jogo já finalizado. Reinicie o ambiente.")

        state_before = deepcopy(self.state)
        player = self.current_player
        opponent = "b" if player == "v" else "v"

        # Aplica o movimento
        next_state, captured = aplicar_movimento(state_before, action, player)

        self.state = next_state
        self.turn_count += 1

        # --- Verificação de fim de jogo ---
        winner = None
        if self.count_pieces(next_state, opponent) == 0:
            self.done = True
            winner = player
        elif self.count_pieces(next_state, player) == 0:
            self.done = True
            winner = opponent
        elif self.turn_count >= self.max_turns:
            self.done = True
            winner = None  # Empate

        # --- Recompensa ---
        reward = 0
        if self.done:
            if winner == player:
                reward = +100
            elif winner == opponent:
                reward = -100
            else:
                reward = 0  # empate
        else:
            reward += len(captured) * 5  # Recompensa por capturar
            reward -= 0.2  # Penalidade leve por cada turno

        # Troca o jogador
        self.current_player = opponent

        info = {"winner": winner}
        return deepcopy(self.state), reward, self.done, info