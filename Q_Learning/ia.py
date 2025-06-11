# src/Q-Learning/ia.py

from .agent import QLearningAgent
# CORREÇÃO: A importação correta é generate_moves, não aplicar_movimento.
from MiniMax.gerador_movimentos import generate_moves
import os

# Instancia global do agente para não precisar carregar o arquivo toda vez
q_agent = QLearningAgent()

# Define o caminho padrão para o modelo
caminho_modelo_padrao = os.path.join("Q-Learning", "modelos", "qlearning_policy.pkl")
q_agent.load_policy(caminho_modelo_padrao) # Carrega a política uma vez quando o módulo é importado

def escolher_movimento_qlearning(state, player):
    """
    Função chamada pelo `main.py` para obter a jogada da IA.
    Usa a política aprendida sem exploração.
    """
    # CORREÇÃO: Usa a função correta para obter a lista de movimentos.
    legal_actions = generate_moves(state, player)
    
    if not legal_actions:
        return None
        
    # Chama choose_action com is_training=False para garantir que ele use a melhor jogada
    return q_agent.choose_action(state, legal_actions, is_training=False)
