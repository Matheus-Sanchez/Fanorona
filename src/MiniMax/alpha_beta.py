from typing import Tuple, List, Optional # Added List, Optional
from .gerador_movimentos import generate_moves # generate_moves now has more params
from .gerador_movimentos import aplicar_movimento # Assuming this is the simple one from gerador_movimentos.py
from .heuristica import evaluate_state
from copy import deepcopy

State = list[list[str]]
Move = Tuple[Tuple[int, int], Tuple[int, int]]

# aplicar_movimento from this file is a utility, ensure it's the simple one if gerador_movimentos.aplicar_movimento is different
# For this example, I'll assume the aplicar_movimento defined in this file is used.
# If gerador_movimentos.aplicar_movimento is the canonical one, import and use that.
# Let's remove the local one to avoid confusion and use the one from gerador_movimentos.
# from .gerador_movimentos import aplicar_movimento as aplicar_movimento_simples

# ... (remove local aplicar_movimento if it's a duplicate of gerador_movimentos.aplicar_movimento)

def _get_all_final_states_after_chain(current_s: State, player_for_chain: str, piece_at: Tuple[int, int], 
                                      visited_path: List[Tuple[int, int]]) -> List[State]:
    """
    Recursively finds all possible board states after a chain capture sequence is completed.
    """
    # generate_moves is imported from .gerador_movimentos
    # aplicar_movimento is also imported from .gerador_movimentos
    
    chain_moves = generate_moves(current_s, player_for_chain,
                                 capturas_apenas=True,  # Chains are always captures
                                 active_piece_pos=piece_at,
                                 visited_in_chain=visited_path)
    if not chain_moves:
        return [current_s]  # Base case: no more chain moves

    all_resulting_states: List[State] = []
    for chain_m in chain_moves:
        # aplicar_movimento from gerador_movimentos should be used
        state_after_chain_m = aplicar_movimento(current_s, chain_m, player_for_chain)
        
        new_piece_pos = chain_m[1]
        new_visited_path = visited_path + [new_piece_pos]
        
        all_resulting_states.extend(
            _get_all_final_states_after_chain(state_after_chain_m, player_for_chain, new_piece_pos, new_visited_path)
        )
    
    # If all chain_moves led to no further valid chains (e.g. all branches ended),
    # but this function was called because chain_moves was initially non-empty,
    # this means those branches have been explored.
    # If all_resulting_states is empty here, it means the initial chain_moves didn't lead to valid deeper states.
    # This shouldn't happen if generate_moves and aplicar_movimento are correct.
    # If a chain_move is made, it must result in at least one state.
    return all_resulting_states if all_resulting_states else [current_s] # Fallback if something went wrong

def alpha_beta_search(state: State, player: str, move: Move, depth: int) -> float:
    # This function seems to be an entry point that applies one move first.
    # It should also handle the start of a chain.
    next_state_after_first_move = aplicar_movimento(state, move, player) # from gerador_movimentos
    opponent = "b" if player == "v" else "v"

    active_piece_pos = move[1]
    visited_path_for_chain = [move[0], move[1]] # Path includes start and end of first move

    final_states_from_this_initial_move = _get_all_final_states_after_chain(
        next_state_after_first_move, player, active_piece_pos, visited_path_for_chain
    )

    # If the initial move leads to multiple outcomes due to chain choices,
    # we need to decide how to evaluate. Typically, minimax evaluates the best outcome for the current player.
    # For now, let's assume we evaluate all and the calling IA function will pick.
    # Or, if this is the main alphabeta, it should branch.
    # The current alphabeta structure below is better: it iterates initial_moves.

    # This alpha_beta_search might not be the one used by ia.py directly.
    # Let's assume ia.py calls the main `alphabeta` function.
    # So, this `alpha_beta_search` might be for a different purpose or can be removed if unused.
    # For now, let's make it evaluate one of the final states.
    if not final_states_from_this_initial_move: # Should not happen
        return evaluate_state(next_state_after_first_move, player) # Or opponent? Depends on whose turn it is after chain.

    # This part is tricky: which final_state to pass to alphabeta?
    # If player is maximizing, they'd choose the chain leading to best outcome.
    # This suggests the chain logic should be *inside* the main alphabeta loop.
    # Let's assume for now this function is simplified or ia.py calls the main alphabeta.
    # The main alphabeta below is more robust.
    # We will focus on the main `alphabeta` function.
    # This `alpha_beta_search` will be simplified or removed later if not the primary entry.
    # For now, just evaluate the first outcome of the chain for this specific path.
    return alphabeta(final_states_from_this_initial_move[0], opponent, depth - 1, float("-inf"), float("inf"), maximizing=False)


def alphabeta(state: State, player: str, depth: int,
              alpha: float, beta: float, maximizing: bool) -> float:
    if depth == 0:
        return evaluate_state(state, player)

    initial_moves = generate_moves(state, player) # Gets all valid first moves (captures prioritized)
    if not initial_moves:
        return evaluate_state(state, player)

    opponent = "b" if player == "v" else "v"

    if maximizing:
        max_eval = float("-inf")
        for first_move in initial_moves:
            state_after_first_move = aplicar_movimento(state, first_move, player) # from gerador_movimentos
            
            active_piece_pos = first_move[1] 
            visited_path_for_chain = [first_move[0], first_move[1]]

            final_states = _get_all_final_states_after_chain(
                state_after_first_move, player, active_piece_pos, visited_path_for_chain
            )
            
            # The player will choose the chain continuation that maximizes their outcome.
            # So, for each first_move, we find the best possible outcome after its chain.
            current_first_move_best_outcome_val = float("-inf")
            if not final_states: # Should mean state_after_first_move was the end.
                 final_states = [state_after_first_move]

            for final_s in final_states:
                eval_val = alphabeta(final_s, opponent, depth - 1, alpha, beta, False)
                current_first_move_best_outcome_val = max(current_first_move_best_outcome_val, eval_val)
            
            max_eval = max(max_eval, current_first_move_best_outcome_val)
            alpha = max(alpha, max_eval)
            if alpha >= beta:
                break 
        return max_eval
    else: # Minimizing
        min_eval = float("inf")
        for first_move in initial_moves:
            state_after_first_move = aplicar_movimento(state, first_move, player)
            active_piece_pos = first_move[1]
            visited_path_for_chain = [first_move[0], first_move[1]]

            final_states = _get_all_final_states_after_chain(
                state_after_first_move, player, active_piece_pos, visited_path_for_chain
            )

            current_first_move_worst_outcome_val = float("inf")
            if not final_states:
                final_states = [state_after_first_move]

            for final_s in final_states:
                eval_val = alphabeta(final_s, opponent, depth - 1, alpha, beta, True)
                current_first_move_worst_outcome_val = min(current_first_move_worst_outcome_val, eval_val)
            
            min_eval = min(min_eval, current_first_move_worst_outcome_val)
            beta = min(beta, min_eval)
            if beta <= alpha:
                break
        return min_eval
