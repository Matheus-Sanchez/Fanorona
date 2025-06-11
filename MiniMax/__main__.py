import argparse
import json
import sys
from .gerador_movimentos import generate_moves, aplicar_movimento
from .minimax import minimax_search
from .alpha_beta import alpha_beta_search
from .heuristica import evaluate_state
from concurrent.futures import ThreadPoolExecutor
from MiniMax.ia import escolher_movimento_ia


state_cache = {}


def alphabeta(state, player, depth, alpha, beta, maximizing, estados_visitados=None):
    """
    Implementação do algoritmo Alpha-Beta com suporte para capturas em cadeia.
    :param state: Estado atual do tabuleiro.
    :param player: Jogador atual ("v" ou "b").
    :param depth: Profundidade máxima da busca.
    :param alpha: Valor alpha para poda.
    :param beta: Valor beta para poda.
    :param maximizing: Indica se é o jogador maximizador.
    :param estados_visitados: Conjunto de estados visitados para evitar ciclos.
    :return: Valor da avaliação do estado.
    """
    if depth == 0:
        return evaluate_state(state, player)

    if estados_visitados is None:
        estados_visitados = set()

    moves = generate_moves(state, player, capturas_apenas=True) or generate_moves(state, player)
    if not moves:
        return evaluate_state(state, player)

    if maximizing:
        max_eval = float("-inf")
        for move in moves:
            # aplica movimento simples (removendo capturas no caminho)
            novo_estado = aplicar_movimento(state, move, player)
            eval = alphabeta(novo_estado,
                             "b" if player == "v" else "v",
                             depth - 1,
                             alpha, beta,
                             False,
                             estados_visitados)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval

    else:
        min_eval = float("inf")
        for move in moves:
            novo_estado = aplicar_movimento(state, move, player)
            eval = alphabeta(novo_estado,
                             "b" if player == "v" else "v",
                             depth - 1,
                             alpha, beta,
                             True,
                             estados_visitados)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


def parallel_minimax(moves, state, player, depth, maximizing):
    with ThreadPoolExecutor() as executor:
        results = executor.map(
            lambda move: alphabeta(
                aplicar_movimento(state, move, player),
                "b" if player == "v" else "v",
                depth - 1,
                float("-inf"),
                float("inf"),
                not maximizing
            ),
            moves
        )
    return max(results) if maximizing else min(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Modo IA do Fanorona para testar via JSON")
    parser.add_argument("--arquivo", type=argparse.FileType("r"), default=sys.stdin, help="Arquivo JSON com estado atual")
    parser.add_argument("--depth", type=int, default=3, help="Profundidade da busca")
    parser.add_argument("--minimax", action="store_true", help="Usa minimax em vez de alpha-beta")
    args = parser.parse_args()

    dados = json.load(args.arquivo)
    state = dados["state"]
    player = dados["player"]

    melhor_jogada, valor = escolher_movimento_ia(state, player, profundidade=args.depth, alphabeta=alphabeta, usar_alpha_beta=not args.minimax)
    print(json.dumps({"melhor_jogada": melhor_jogada, "avaliacao": valor}, indent=2))
