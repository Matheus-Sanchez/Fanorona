import argparse
import json
import sys
from .config import DEFAULT_DEPTH
from .gerador_movimentos import generate_moves
from .minimax import minimax_search
from .alpha_beta import alpha_beta_search
from .heuristica import evaluate_state


def escolher_movimento_ia(state, player, profundidade=3, usar_alpha_beta=True):
    moves = generate_moves(state, player)
    best_move = None
    best_value = float("-inf")

    for move in moves:
        value = (alpha_beta_search if usar_alpha_beta else minimax_search)(state, player, move, profundidade)
        if value > best_value:
            best_value = value
            best_move = move

    return best_move, best_value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Modo IA do Fanorona para testar via JSON")
    parser.add_argument("--arquivo", type=argparse.FileType("r"), default=sys.stdin, help="Arquivo JSON com estado atual")
    parser.add_argument("--depth", type=int, default=3, help="Profundidade da busca")
    parser.add_argument("--minimax", action="store_true", help="Usa minimax em vez de alpha-beta")
    args = parser.parse_args()

    dados = json.load(args.arquivo)
    state = dados["state"]
    player = dados["player"]

    melhor_jogada, valor = escolher_movimento_ia(state, player, profundidade=args.depth, usar_alpha_beta=not args.minimax)
    print(json.dumps({"melhor_jogada": melhor_jogada, "avaliacao": valor}, indent=2))
