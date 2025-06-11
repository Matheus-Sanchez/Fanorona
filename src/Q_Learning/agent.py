# ======================================================================
# Responsabilidade: Contém a classe do Agente Q-Learning, adaptada
# para usar dicionários em vez de arrays NumPy.
# ======================================================================

import random
import pickle
import os
import threading

# A constante MODELO_DIR agora será usada como o padrão
MODELO_DIR = os.path.join(os.path.dirname(__file__), "modelos")
os.makedirs(MODELO_DIR, exist_ok=True)

class QLearningAgent:
    """
    Esta é a classe `Qlearning` do seu professor, mas adaptada para o Fanorona.
    - Usa dicionários para a Q-Table e Política, permitindo um número
      quase infinito de estados/ações.
    - O loop de treinamento é episódico (jogo a jogo).
    """
    def __init__(self, gamma=0.90, alpha=0.1, epsilon=0.4, min_e=0.01, decay=0.99995): 
        self.q_table = {}
        self.policy = {}   
        
        self.desconto = gamma    
        self.alpha = alpha
        self.e = epsilon
        self.min_e = min_e  # Adiciona o atributo min_e
        self.decay_rate = decay # Adiciona o atributo para a taxa de decaimento

    def _get_state_key(self, state_list):
        """Converte o estado em uma chave de dicionário imutável."""
        return tuple(map(tuple, state_list))

    def _get_action_key(self, action):
        """Converte a ação (lista de tuplos) em uma chave imutável."""
        return tuple(map(tuple, action))

    def get_q_value(self, state_key, action_key):
        """Obtém um valor da Q-Table, retornando 0 se não existir."""
        return self.q_table.get(state_key, {}).get(action_key, 0.0)

    # [PROFESSOR] Equivalente a `sorteia_proxima_acao`
    def choose_action(self, state_list, legal_actions, is_training=True):
        """
        Escolhe uma ação usando a estratégia epsilon-greedy.
        - Com probabilidade 'e', escolhe uma ação aleatória (exploração).
        - Com probabilidade (1-e), escolhe a melhor ação conhecida (explotação).
        """
        if not legal_actions:
            return None

        state_key = self._get_state_key(state_list)

        # Exploração
        if is_training and random.uniform(0, 1) < self.e:
            return random.choice(legal_actions)
        
        # Explotação
        # [PROFESSOR] acao_politica = self.PI[estado]
        # Se já temos uma política para este estado, use-a.
        if state_key in self.policy:
            # Certifica-se de que a ação da política ainda é legal
            best_action_from_policy = list(map(tuple, self.policy[state_key]))
            if best_action_from_policy in legal_actions:
                return best_action_from_policy

        # Se não há política ou a política aponta para uma jogada ilegal,
        # encontra a melhor ação a partir da Q-Table.
        q_values = {self._get_action_key(a): self.get_q_value(state_key, self._get_action_key(a)) for a in legal_actions}
        
        if not q_values:
             return random.choice(legal_actions) # Fallback

        max_q = max(q_values.values())
        best_actions = [a for a, q in q_values.items() if q == max_q]
        
        # Desempacota a ação de volta para o formato de lista
        chosen_action_tuple = random.choice(best_actions)
        return list(map(list, chosen_action_tuple))

    # [PROFESSOR] Equivalente a `novo_q` e a linha de atualização do Q-value
    # RENOMEAR MÉTODO e AJUSTAR PARÂMETROS E LÓGICA INTERNA
    def learn(self, state, action, reward, next_state, done): # Modificado de update(..., next_legal_actions)
        """Atualiza a Q-Table e a Política para um passo (s, a, r, s')."""
        state_key = self._get_state_key(state)
        action_key = self._get_action_key(action)
        next_state_key = self._get_state_key(next_state)

        # Pega o Q-valor antigo
        old_value = self.get_q_value(state_key, action_key)

        # Calcula o melhor Q-valor para o próximo estado
        next_max_q = 0.0
        if not done: # Se o episódio não terminou
            # Se o próximo estado já tem valores Q conhecidos, pega o máximo
            if next_state_key in self.q_table and self.q_table[next_state_key]:
                next_max_q = max(self.q_table[next_state_key].values())
            # Caso contrário, next_max_q permanece 0 (Q-valores para ações não exploradas são 0)
        
        # Calcula o novo valor Q
        new_value = old_value + self.alpha * (reward + self.desconto * next_max_q - old_value)

        # Atualiza a Q-Table
        if state_key not in self.q_table:
            self.q_table[state_key] = {}
        self.q_table[state_key][action_key] = new_value

        # Atualiza a política para o estado atual
        # Garante que o estado existe na q_table e tem ações antes de tentar obter o max
        if state_key in self.q_table and self.q_table[state_key]:
            current_best_action = max(self.q_table[state_key], key=self.q_table[state_key].get)
            self.policy[state_key] = current_best_action

    def save_policy(self, file_path=None):
        """Salva a Q-Table e a política em um arquivo."""
        # Se nenhum caminho for fornecido, usa o caminho padrão dentro da pasta de modelos
        if file_path is None:
            file_path = os.path.join(MODELO_DIR, "qlearning_policy.pkl")

        with open(file_path, 'wb') as f:
            pickle.dump({'q_table': self.q_table, 'policy': self.policy}, f)
        print(f"Política salva em {file_path}")
    
    def async_save(self, file_path=None):
        thread = threading.Thread(target=self.save_policy, args=(file_path,))
        thread.daemon = True
        thread.start()

    # --- CORREÇÃO AQUI ---
    def load_policy(self, file_path=None):
        """Carrega a Q-Table e a política de um arquivo."""
        # Se nenhum caminho for fornecido, usa o caminho padrão dentro da pasta de modelos
        if file_path is None:
            file_path = os.path.join(MODELO_DIR, "qlearning_policy.pkl")
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
                self.q_table = data['q_table']
                self.policy = data['policy']
            print(f"Política carregada de {file_path}")
        except FileNotFoundError:
            print(f"Arquivo de política não encontrado em {file_path}. Começando com uma política vazia.")