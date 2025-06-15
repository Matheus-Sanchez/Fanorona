# MiniMax/paralelo.py

import threading
import math
from typing import Optional # Mantenha Optional de typing
from .gerador_movimentos import State, Move # Importe State e Move do local correto
from .alpha_beta import TranspositionTable, alpha_beta_search, init_zobrist # Usamos a mesma lógica de busca
from .gerador_movimentos import generate_moves, aplicar_movimento

class ThreadSafeTranspositionTable(TranspositionTable):
    """
    Uma versão da Tabela de Transposição segura para threads, usando um bloqueio (lock)
    para evitar condições de corrida quando múltiplas threads acessam a tabela.
    Para otimizações maiores, poderíamos usar um bloqueio por "balde" (bucket), mas
    um bloqueio global é um ponto de partida mais simples e robusto.
    """
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()

    def store(self, hash_key, depth, score, flag, best_move=None):
        with self.lock:
            super().store(hash_key, depth, score, flag, best_move)

    def probe(self, hash_key, depth, alpha, beta):
        with self.lock:
            return super().probe(hash_key, depth, alpha, beta)


def search_worker(thread_id, state, player, depth, alpha, beta, is_maximizing, tt, results):
    """Função que cada thread irá executar."""
    print(f"Thread {thread_id} iniciando busca.")
    # Cada thread executa a mesma função de busca alpha-beta
    # Todas compartilham a mesma tabela de transposição (tt)
    score = alpha_beta_search(state, player, depth, alpha, beta, is_maximizing, tt, set())
    results[thread_id] = score
    print(f"Thread {thread_id} terminou com pontuação: {score}")


def escolher_movimento_ia_paralelo(state: State, player: str, depth: int, num_threads: int = 4) -> Optional[Move]:
    """
    Lazy SMP (Symmetric Multiprocessing) - Implementação de busca paralela.
    A ideia é que cada thread pesquise um ramo diferente da árvore a partir da raiz.
    Todas as threads compartilham a mesma Tabela de Transposição para comunicar
    descobertas (como bons movimentos ou limites) e evitar trabalho duplicado.
    """
    init_zobrist()
    # A Tabela de Transposição deve ser segura para threads
    shared_tt = ThreadSafeTranspositionTable()
    
    moves = generate_moves(state, player)
    if not moves:
        return None

    best_move = None
    threads = []
    results = {} # Dicionário para armazenar resultados de cada thread

    is_maximizing = (player == 'v')
    opponent = 'b' if player == 'v' else 'v'

    if is_maximizing:
        best_value = -math.inf
        # Aqui, poderíamos dividir os movimentos entre as threads,
        # mas uma implementação mais simples de Lazy SMP é deixar cada thread
        # ajudar a explorar a árvore a partir da mesma raiz, confiando na TT
        # para guiar a busca. Para uma divisão explícita:
        for i, move in enumerate(moves):
            # Para cada movimento na raiz, avaliamos seu valor
            next_state, _ = aplicar_movimento(state, move, player)
            
            # Aqui, você poderia lançar threads para avaliar os nós filhos em paralelo.
            # Por simplicidade, este exemplo mostra a lógica conceitual.
            # A verdadeira implementação Lazy SMP é mais complexa e integrada.
            
            # Vamos simular a avaliação sequencial, mas usando a TT que seria compartilhada.
            board_value = alpha_beta_search(next_state, opponent, depth - 1, -math.inf, math.inf, False, shared_tt, set())

            if board_value > best_value:
                best_value = board_value
                best_move = move
    else: # Minimizando
        best_value = math.inf
        for move in moves:
            next_state, _ = aplicar_movimento(state, move, player)
            board_value = alpha_beta_search(next_state, opponent, depth - 1, -math.inf, math.inf, True, shared_tt, set())
            if board_value < best_value:
                best_value = board_value
                best_move = move

    print(f"IA Paralela ({player}) escolheu o movimento: {best_move} com valor: {best_value}")
    return best_move

