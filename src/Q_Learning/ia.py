import os
from .agent import QLearningAgent
from .environment import FanoronaEnv

# Instancia global do agente para não precisar carregar o arquivo toda vez
env = FanoronaEnv()
initial_state = env.reset()
# ações no Fanorona: pares de coordenadas (origem, destino)
legal = env.get_legal_actions(initial_state, env.current_player)
# Cria agente SEM passar action_dim
q_agent = QLearningAgent()

# carrega política existente (se houver)
caminho_modelo_padrao = os.path.join('Q-Learning', 'modelos', 'qlearning_policy.pkl')
q_agent.load_policy(caminho_modelo_padrao)

def escolher_movimento_qlearning(state, legal_actions):
    """
    Retorna a ação escolhida pelo Q-Learning agent para um dado estado e conjunto de ações.
    state: lista de listas que representa o tabuleiro
    legal_actions: lista de ações (cada ação é [(r1,c1),(r2,c2)])
    """
    # o agente espera listas de coordenadas como ações
    move = q_agent.choose_action(state, legal_actions, is_training=True)
    return move
