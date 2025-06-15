import os
import time
import threading
import random
from copy import deepcopy
from .environment import FanoronaEnv
from .agent import QLearningAgent
# ALTERAÇÃO 1: Importar a IA paralela do MiniMax
from MiniMax.ia import escolher_movimento_ia_paralelo

# Configurações
MODELO_DIR = os.path.join(os.path.dirname(__file__), "modelos")
os.makedirs(MODELO_DIR, exist_ok=True)

# Hiperparâmetros
# ALTERAÇÃO 2: Aumentar drasticamente o número de episódios
NUM_EPISODIOS = 10000
# ALTERAÇÃO 3: Diminuir a taxa de aprendizado para um ajuste fino (já era 0.001 no seu arquivo)
ALFA = 0.001
GAMMA = 0.999
EPSILON = 1.0
MIN_EPSILON = 0.001
# ALTERAÇÃO 4: Tornar o decaimento mais lento para uma exploração mais longa
DECAY_RATE = 0.9995
# Salva a cada 500 episódios
CHECKPOINT_INTERVAL = 500
STATS_UPDATE_INTERVAL = 100 # Mantido, pois não há alteração explícita no uso
WINDOW = 100

def async_save(agent, file_path):
    """Salva a política em segundo plano."""
    threading.Thread(target=agent.save_policy, args=(file_path,), daemon=True).start()

def train_agent():
    env = FanoronaEnv()
    agent = QLearningAgent(
                           gamma=GAMMA,
                           alpha=ALFA,
                           epsilon=EPSILON,
                           min_e=MIN_EPSILON, # Parâmetro já existente no seu train.py
                           decay=DECAY_RATE)  # Parâmetro já existente no seu train.py

    caminho_modelo = os.path.join(MODELO_DIR, "qlearning_policy.pkl")
    if os.path.exists(caminho_modelo):
        agent.load_policy(caminho_modelo)

    total_reward = 0
    total_wins = 0
    avg_rewards = []
    win_rates = []

    start_time = time.time()
    
    # ALTERAÇÃO 5: Usar todo o processador. os.cpu_count() no seu caso retornará 16.
    # Esta linha já existia e estava correta.
    NUM_THREADS = os.cpu_count()
    print(f"--- INICIANDO TREINAMENTO INTENSIVO ---")
    print(f"Oponente MiniMax usará {NUM_THREADS} threads.")
    print(f"O treinamento rodará por {NUM_EPISODIOS} episódios.")
    print(f"Pressione Ctrl+C no terminal para parar e salvar o progresso.")

    for episode in range(1, NUM_EPISODIOS + 1):
        print(f"Iniciando episódio {episode}/{NUM_EPISODIOS}...") # <--- ADICIONE ESTA LINHA
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
            else: # Minimax como oponente
                # ALTERAÇÃO 6: Usar a IA paralela com maior profundidade
                action = escolher_movimento_ia_paralelo(state_list, current_player, depth=4, num_threads=NUM_THREADS, verbose=False)

            if action is None: # Se a IA não escolheu (ou não pôde escolher)
                done = True
                winner = opponent_player if current_player == q_agent_player else q_agent_player
                break

            next_state, reward, done, info = env.step(action)
            
            # O agente só aprende com as consequências de SUAS próprias ações.
            if current_player == q_agent_player:
                # CORREÇÃO: Chama o método 'learn' com os argumentos corretos (conforme seu novo código)
                # Nota: O método 'learn' precisa existir na sua classe QLearningAgent
                # e lidar com 'done' em vez de 'next_legal_actions'.
                # O código anterior chamava agent.update(state_list, action, reward, next_state, next_legal_actions)
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
            print(f"[EP {episode}/{NUM_EPISODIOS}] Média recompensa: {avg:.2f} | Vitórias: {win_rate*100:.1f}% | Epsilon: {agent.e:.4f} | Tempo: {tempo_decorrido:.1f}s")
            avg_rewards.append(avg)
            win_rates.append(win_rate)
            total_reward = 0
            total_wins = 0
            start_time = time.time()

        # O decaimento do epsilon agora acontece dentro do loop principal, o que é mais comum
        # Movido de dentro do bloco `if episode % WINDOW == 0:`
        if agent.e > MIN_EPSILON:
            agent.e *= DECAY_RATE

        if episode % CHECKPOINT_INTERVAL == 0:
            nome_arquivo = os.path.join(MODELO_DIR, f"checkpoint_ep{episode}.pkl")
            async_save(agent, nome_arquivo)
            print(f"--- Checkpoint salvo em {nome_arquivo} ---")

    print("Treinamento concluído!")
    agent.save_policy(caminho_modelo)


if __name__ == "__main__":
    train_agent()