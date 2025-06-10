import os
import time
import threading
import random
from copy import deepcopy
from .environment import FanoronaEnv
from .agent import QLearningAgent
from MiniMax.ia import escolher_movimento_ia

# Configurações
MODELO_DIR = os.path.join(os.path.dirname(__file__), "modelos")
os.makedirs(MODELO_DIR, exist_ok=True)

# Hiperparâmetros
NUM_EPISODIOS = 200
ALFA = 0.01
GAMMA = 0.99
EPSILON = 1.0
MIN_EPSILON = 0.01
DECAY_RATE = 0.9995
CHECKPOINT_INTERVAL = 100
STATS_UPDATE_INTERVAL = 100
WINDOW = 500

def async_save(agent, file_path):
    """Salva a política em segundo plano."""
    threading.Thread(target=agent.save_policy, args=(file_path,), daemon=True).start()

def train_agent():
    env = FanoronaEnv()
    # pega estado inicial para contar ações legais
    initial_state = env.reset()
    state_dim = len(initial_state) * len(initial_state[0])
    # número real de ações no estado inicial
    action_dim = len(env.get_legal_actions(initial_state, env.current_player))
    agent = QLearningAgent(
                           gamma=GAMMA,
                           alpha=ALFA,
                           epsilon=EPSILON,
                           min_e=MIN_EPSILON,
                           decay=DECAY_RATE)

    caminho_modelo = os.path.join(MODELO_DIR, "qlearning_policy.pkl")
    if os.path.exists(caminho_modelo):
        agent.load_policy(caminho_modelo)

    total_reward = 0
    total_wins = 0
    avg_rewards = []
    win_rates = []

    start_time = time.time()

    for episode in range(1, NUM_EPISODIOS + 1):
        q_agent_player = random.choice(['v', 'b'])
        opponent_player = 'b' if q_agent_player == 'v' else 'v'

        state = env.reset() # O ambiente agora controla quem joga
        done = False
        reward_acumulado = 0
        winner = None

        while not done:
            current_player = env.current_player
            state_list = deepcopy(state)

            legal_actions = env.get_legal_actions(state_list, current_player)

            if not legal_actions:
                done = True
                winner = opponent_player if current_player == q_agent_player else q_agent_player
                break

            action = None
            if current_player == q_agent_player:
                action = agent.choose_action(state_list, legal_actions, is_training=True)
            else: # Minimax
                action = escolher_movimento_ia(state_list, current_player, depth=6) # Profundidade 2 para acelerar

            if action is None: # Se a IA não escolheu (ou não pôde escolher)
                done = True
                winner = opponent_player if current_player == q_agent_player else q_agent_player
                break

            next_state, reward, done, info = env.step(action)
            
            # O agente só aprende com as consequências de SUAS próprias ações.
            if current_player == q_agent_player:
                next_legal_actions = env.get_legal_actions(next_state, opponent_player)
                # CORREÇÃO: Chama o método 'update' com os argumentos corretos
                agent.learn(state_list, action, reward, next_state, done)
                reward_acumulado += reward

            state = next_state
            if info.get("winner"):
                winner = info["winner"]

        if winner == q_agent_player:
            total_wins += 1
        total_reward += reward_acumulado

        if episode % WINDOW == 0:
            avg = total_reward / WINDOW if WINDOW > 0 else 0
            win_rate = total_wins / WINDOW if WINDOW > 0 else 0
            tempo_decorrido = time.time() - start_time
            print(f"[EP {episode}/{NUM_EPISODIOS}] Média recompensa: {avg:.2f} | Vitórias: {win_rate*100:.1f}% | Epsilon: {agent.e:.3f} | Tempo: {tempo_decorrido:.1f}s")
            avg_rewards.append(avg)
            win_rates.append(win_rate)
            total_reward = 0
            total_wins = 0
            start_time = time.time()

            if agent.e > MIN_EPSILON:
                agent.e *= DECAY_RATE

        if episode % CHECKPOINT_INTERVAL == 0:
            nome_arquivo = os.path.join(MODELO_DIR, f"checkpoint_ep{episode}.pkl")
            async_save(agent, nome_arquivo)

    print("Treinamento concluído!")
    agent.save_policy(caminho_modelo)


if __name__ == "__main__":
    train_agent()