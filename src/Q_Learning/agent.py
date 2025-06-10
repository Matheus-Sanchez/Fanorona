import random
import pickle
import os
import threading
import torch

class QLearningAgent:
    def __init__(self, action_dim=0, gamma=0.9, alpha=0.1, epsilon=1.0, min_e=0.01, decay=0.995):
        # dispositivo: GPU se disponível
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.gamma = gamma
        self.alpha = alpha
        self.e = epsilon
        self.min_e = min_e
        self.decay = decay
        self.action_dim = action_dim  # Armazena action_dim

        # tabela Q como tensor [n_states, n_actions]
        # Inicialmente sem estados e com self.action_dim colunas
        # Se action_dim for 0, o tensor será (0,0)
        self.q_table = torch.zeros((0, self.action_dim), device=self.device)
        # mapeamento de estado → índice na Q-table (linhas)
        self.state_to_idx = {}
        # mapeamento de ação → índice na Q-table (colunas)
        self.action_to_idx = {}
        self.idx_to_action = {}

    def _get_state_key(self, state_list):
        """Converte uma lista de listas em uma string imutável."""
        return str(state_list)

    def _get_action_key(self, action_list):
        """Converte uma lista de tuplas (ação) em uma string imutável."""
        return str(action_list)

    def _ensure_state(self, state_key):
        """Garante que o estado exista na Q-table, expandindo linhas se for novo."""
        if state_key not in self.state_to_idx:
            idx = len(self.state_to_idx)
            self.state_to_idx[state_key] = idx
            # adiciona nova linha com colunas atuais
            new_row = torch.zeros((1, self.q_table.size(1)), device=self.device)
            self.q_table = torch.cat([self.q_table, new_row], dim=0)

    def _ensure_action(self, action):
        """Garante que a ação exista na Q-table, expandindo colunas se for nova."""
        action_key = self._get_action_key(action)
        if action_key not in self.action_to_idx:
            idx = len(self.action_to_idx)
            self.action_to_idx[action_key] = idx
            self.idx_to_action[idx] = action # Armazena a ação original
            # adiciona nova coluna em todas as linhas
            pad = torch.zeros((self.q_table.size(0), 1), device=self.device)
            self.q_table = torch.cat([self.q_table, pad], dim=1)

    def choose_action(self, state, legal_actions, is_training=True):
        # exploração aleatória
        if is_training and random.random() < self.e:
            return random.choice(legal_actions)
        state_key = self._get_state_key(state)
        self._ensure_state(state_key)
        # garante que todas as ações legais estejam mapeadas
        for a in legal_actions:
            self._ensure_action(a) # Passa a ação original
        s_idx = self.state_to_idx[state_key]
        # converte ações para índices de coluna usando suas chaves string
        cols = [self.action_to_idx[self._get_action_key(a)] for a in legal_actions]
        q_vals = self.q_table[s_idx, cols]
        # escolhe a ação de maior valor
        _, idx = torch.max(q_vals, dim=0)
        return legal_actions[idx]

    def learn(self, state, action, reward, next_state, done):
        sk = self._get_state_key(state)
        skp = self._get_state_key(next_state)
        self._ensure_state(sk)
        self._ensure_state(skp)
        # garante ação mapeada
        self._ensure_action(action) # Passa a ação original
        s_idx = self.state_to_idx[sk]
        sp_idx = self.state_to_idx[skp]
        a_idx = self.action_to_idx[self._get_action_key(action)] # Usa a chave string da ação
        q_sa = self.q_table[s_idx, a_idx]
        # valor futuro máximo no próximo estado
        q_sp_max = torch.max(self.q_table[sp_idx]) if not done else torch.tensor(0.0, device=self.device)
        target = reward + self.gamma * q_sp_max
        # Q-learning update
        self.q_table[s_idx, a_idx] = q_sa + self.alpha * (target - q_sa)
        if done and self.e > self.min_e:
            self.e *= self.decay

    def save_policy(self, file_path=None):
        """Grava Q-table e mapeamentos em arquivo."""
        path = file_path or os.path.join('Q-Learning', 'modelos', 'qlearning_policy.pkl')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {
            'q_table': self.q_table.cpu(),
            'state_to_idx': self.state_to_idx,
            'action_to_idx': self.action_to_idx
        }
        with open(path, 'wb') as f:
            pickle.dump(data, f)

    def load_policy(self, file_path=None):
        """Carrega Q-table e mapeamentos de arquivo, se existir."""
        path = file_path or os.path.join('Q-Learning', 'modelos', 'qlearning_policy.pkl')
        if os.path.exists(path):
            data = pickle.load(open(path, 'rb'))
            self.q_table = data['q_table'].to(self.device)
            self.state_to_idx = data.get('state_to_idx', {})
            self.action_to_idx = data.get('action_to_idx', {})
            # recria idx_to_action
            self.idx_to_action = {idx: act for act, idx in self.action_to_idx.items()}
            self.action_dim = self.q_table.size(1) # Atualiza action_dim com base na tabela carregada
            print(f"Política carregada de {path}")
        else:
            print(f"Arquivo de política não encontrado em {path}. Iniciando com nova política.")
