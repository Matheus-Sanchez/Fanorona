import json
import os
import matplotlib.pyplot as plt

# Caminho para a pasta onde os dados foram salvos
MODELO_DIR = "Q-Learning/modelos" # Ou o novo caminho que você definiu

def plot_training_results():
    """
    Carrega as estatísticas de treinamento de um arquivo JSON e gera os gráficos.
    """
    stats_path = os.path.join(MODELO_DIR, "training_stats.json")

    try:
        with open(stats_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Arquivo de estatísticas não encontrado em {stats_path}")
        return

    avg_rewards = data.get("avg_rewards", [])
    win_rates = data.get("win_rates", [])

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(avg_rewards)
    plt.title("Recompensa Média por Janela")
    plt.xlabel(f"Janela (x{WINDOW} episódios)") # Supondo que WINDOW seja 500
    plt.ylabel("Recompensa Média")

    plt.subplot(1, 2, 2)
    plt.plot(win_rates)
    plt.title("Taxa de Vitórias por Janela")
    plt.xlabel(f"Janela (x{WINDOW} episódios)") # Supondo que WINDOW seja 500
    plt.ylabel("Vitórias (%)")

    plt.tight_layout()
    
    # Salva o gráfico em um arquivo
    output_path = os.path.join(MODELO_DIR, "evolucao_treinamento.png")
    plt.savefig(output_path)
    print(f"Gráfico salvo em {output_path}")

    plt.show()

if __name__ == "__main__":
    # Você precisará definir a variável WINDOW ou passá-la como argumento
    # se o script for executado de forma independente.
    WINDOW = 500 
    plot_training_results()