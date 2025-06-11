import pickle
import os
import random

def inspecionar_modelo_qlearning():
    """
    Carrega e inspeciona a Q-Table e a política de Q-Learning salvas.
    """
    # Caminho para o modelo treinado
    caminho_modelo = os.path.join(os.path.dirname(__file__), 'modelos/treinamento1', 'qlearning_policy.pkl')

    if not os.path.exists(caminho_modelo):
        print(f"Arquivo de modelo não encontrado em: {caminho_modelo}")
        print("Execute o treinamento (train.py) primeiro para gerar o modelo.")
        return

    print(f"Carregando modelo de: {caminho_modelo}")
    
    try:
        with open(caminho_modelo, 'rb') as f:
            data = pickle.load(f)
    except Exception as e:
        print(f"Ocorreu um erro ao carregar o arquivo: {e}")
        return

    q_table = data.get('q_table')
    policy = data.get('policy')

    if q_table is None:
        print("A Q-Table não foi encontrada no arquivo.")
        return
    
    if policy is None:
        print("A Política não foi encontrada no arquivo.")
        return

    print("\n--- Estatísticas da Q-Table ---")
    num_estados_q_table = len(q_table)
    print(f"Número de estados únicos na Q-Table: {num_estados_q_table}")

    total_pares_estado_acao = 0
    for state_key in q_table:
        total_pares_estado_acao += len(q_table[state_key])
    
    print(f"Número total de pares (estado, ação) com valores Q aprendidos: {total_pares_estado_acao}")

    if num_estados_q_table > 0:
        print("\n--- Exemplo de Dados da Q-Table ---")
        # Pega uma chave de estado aleatória para exibir
        random_state_key = random.choice(list(q_table.keys()))
        
        print(f"\nValores Q para um estado aleatório:")
        print(f"Estado (chave): {random_state_key}") # A chave do estado é uma tupla de tuplas
        
        actions_for_state = q_table[random_state_key]
        print(f"Número de ações aprendidas para este estado: {len(actions_for_state)}")
        
        for i, (action_key, q_value) in enumerate(actions_for_state.items()):
            if i < 5: # Mostra até 5 ações para este estado
                print(f"  Ação (chave): {action_key}, Valor Q: {q_value:.4f}")
            else:
                print(f"  ... e mais {len(actions_for_state) - 5} ações.")
                break
        
        # Encontra a melhor ação para esse estado na Q-Table
        if actions_for_state:
            best_action_q_table = max(actions_for_state, key=actions_for_state.get)
            best_q_value = actions_for_state[best_action_q_table]
            print(f"\nMelhor ação para este estado (baseado na Q-Table):")
            print(f"  Ação (chave): {best_action_q_table} | Valor Q: {best_q_value:.4f}")

    print("\n--- Estatísticas da Política ---")
    num_estados_policy = len(policy)
    print(f"Número de estados únicos na Política: {num_estados_policy}")

    if num_estados_policy > 0:
        print("\n--- Exemplo de Dados da Política ---")
        # Pega uma chave de estado aleatória da política para exibir
        # Pode ser o mesmo estado ou outro, dependendo se todos os estados da Q-Table estão na política
        if random_state_key in policy:
            state_key_policy_example = random_state_key
        else:
            state_key_policy_example = random.choice(list(policy.keys()))

        print(f"\nAção da política para o estado (chave): {state_key_policy_example}")
        action_in_policy = policy[state_key_policy_example]
        print(f"  Ação (chave): {action_in_policy}")
        
        # Verifica se esta ação também está na Q-Table para este estado
        if state_key_policy_example in q_table and action_in_policy in q_table[state_key_policy_example]:
            q_value_of_policy_action = q_table[state_key_policy_example][action_in_policy]
            print(f"  Valor Q desta ação na Q-Table: {q_value_of_policy_action:.4f}")
        else:
            print(f"  (Esta ação da política não foi encontrada na Q-Table para este estado, o que pode ser inesperado)")


if __name__ == "__main__":
    inspecionar_modelo_qlearning()