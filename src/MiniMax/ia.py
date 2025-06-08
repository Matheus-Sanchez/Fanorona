from .gerador_movimentos import generate_moves, aplicar_movimento
from .config import IA_PLAYER, HUMANO_PLAYER, DEFAULT_DEPTH # Assuming DEFAULT_DEPTH is here
from .alpha_beta import alphabeta as alphabeta_evaluator # Renaming to avoid conflict if any
import math
from typing import Optional, List, Tuple # Added Tuple

State = List[List[str]] # Define State type alias
Move = Tuple[Tuple[int, int], Tuple[int, int]] # Define Move type alias

def escolher_movimento_ia(state: State, player: str, profundidade: int, alphabeta_func, # alphabeta_func is the evaluator
                          chain_capture_context: Optional[dict] = None) -> Optional[Move]:
    """
    Retorna o melhor movimento para a IA.
    If chain_capture_context is provided, it means we are continuing a chain.
    chain_capture_context = {'active_piece_pos': (r,c), 'visited_path': [(r0,c0), ..., (r,c)]}
    """
    
    current_best_move = None
    
    if player == IA_PLAYER:
        current_best_value = -math.inf
    else: # HUMANO_PLAYER
        current_best_value = math.inf

    if chain_capture_context:
        active_piece_ctx = chain_capture_context['active_piece_pos']
        visited_ctx = chain_capture_context['visited_path']

        # Defensive check for context validity
        if not (isinstance(active_piece_ctx, tuple) and len(active_piece_ctx) == 2 and
                0 <= active_piece_ctx[0] < len(state) and \
                0 <= active_piece_ctx[1] < len(state[0]) and \
                state[active_piece_ctx[0]][active_piece_ctx[1]] == player):
            print(f"FATAL WARNING: IA.escolher_movimento_ia called with invalid chain_capture_context.")
            print(f"Context: active_piece={active_piece_ctx}, player={player}. Board piece at pos: {state[active_piece_ctx[0]][active_piece_ctx[1]] if (isinstance(active_piece_ctx, tuple) and len(active_piece_ctx) == 2 and 0 <= active_piece_ctx[0] < len(state) and 0 <= active_piece_ctx[1] < len(state[0])) else 'OUT OF BOUNDS'}")
            print("IA will proceed as if it's a new turn, but this indicates a bug in the calling code (e.g., main.py).")
            # Fallback: Treat as a new turn by clearing context, which will use all pieces.
            # This is a workaround for the calling code's potential error.
            moves_to_evaluate = generate_moves(state, player) # Generate moves for all pieces
            chain_capture_context = None # Clear context for the rest of this function call
        else:
            # Context seems valid, proceed with chain logic
            possible_next_chain_moves = generate_moves(state, player, 
                                                       capturas_apenas=True, 
                                                       active_piece_pos=active_piece_ctx, 
                                                       visited_in_chain=visited_ctx)
            if not possible_next_chain_moves:
                return None # Chain ends
            moves_to_evaluate = possible_next_chain_moves
    else:
        # Standard turn: generate all initial moves (captures are prioritized by generate_moves)
        moves_to_evaluate = generate_moves(state, player)

    if not moves_to_evaluate:
        return None

    for move in moves_to_evaluate:
        state_after_first_part = aplicar_movimento(state, move, player)
        active_piece_after_first_part = move[1]
        
        current_path_for_chain_simulation = []
        if chain_capture_context: # Check if context is still valid (wasn't cleared by warning)
            # Ensure the move being processed is indeed from the active_piece of the context
            # This check is vital if the above fallback wasn't taken.
            if move[0] != chain_capture_context['active_piece_pos']:
                # This should only happen if generate_moves failed to respect active_piece_pos
                print(f"CRITICAL ERROR in IA: Move {move} does not originate from active_piece {chain_capture_context['active_piece_pos']} during a chain.")
                print(f"Moves evaluated were: {moves_to_evaluate}")
                # This indicates a deeper bug, possibly in generate_moves or context handling.
                # To prevent crashing, we might skip this move, but the AI will be flawed.
                continue 
            current_path_for_chain_simulation = chain_capture_context['visited_path'] + [move[1]]
        else:
            current_path_for_chain_simulation = [move[0], move[1]]

        temp_final_states = _get_all_final_states_after_chain_for_ia(state_after_first_part, player, 
                                                                  active_piece_after_first_part, 
                                                                  current_path_for_chain_simulation)
        
        opponent = HUMANO_PLAYER if player == IA_PLAYER else IA_PLAYER
        
        for final_state_of_turn in temp_final_states:
            # Now evaluate this final_state_of_turn from the opponent's perspective
            value = alphabeta_func(final_state_of_turn, opponent, profundidade - 1, -math.inf, math.inf, 
                                   (player == HUMANO_PLAYER)) # True if IA (current player) is maximizing, so opponent is minimizing (False)
                                                              # False if IA is maximizing, so opponent is minimizing (False for opponent's call)
                                                              # maximizing for alphabeta_func call is for the *next* player (opponent)
                                                              # if current player is IA (maximizer), opponent is minimizer (maximizing=False for opponent)
                                                              # if current player is Human (minimizer), opponent is IA (maximizer=True for opponent)
            
            is_maximizing_call_for_opponent = (opponent == IA_PLAYER) # This is for the call to alphabeta_func

            # The value returned by alphabeta_func is from the perspective of 'opponent'.
            # We need to compare it based on the current 'player'.
            if player == IA_PLAYER: # Maximizing
                if value > current_best_value:
                    current_best_value = value
                    current_best_move = move
            else: # Minimizing (HUMANO_PLAYER)
                if value < current_best_value:
                    current_best_value = value
                    current_best_move = move
                    
    return current_best_move

# Helper function for ia.py, similar to the one in alpha_beta.py
def _get_all_final_states_after_chain_for_ia(current_s: State, player_for_chain: str, piece_at: Tuple[int, int], 
                                             visited_path: List[Tuple[int, int]]) -> List[State]:
    if current_s is None:
        # This is unexpected and indicates an issue upstream
        # For now, return an empty list to prevent further errors, but this needs investigation
        print(f"Error: _get_all_final_states_after_chain_for_ia received current_s as None. piece_at: {piece_at}, visited_path: {visited_path}")
        return [] # Or raise an exception

    chain_moves = generate_moves(current_s, player_for_chain,
                                 capturas_apenas=True,
                                 active_piece_pos=piece_at,
                                 visited_in_chain=visited_path)
    if not chain_moves:
        return [current_s]

    all_resulting_states: List[State] = []
    for chain_m in chain_moves:
        state_after_chain_m = aplicar_movimento(current_s, chain_m, player_for_chain)
        new_piece_pos = chain_m[1]
        new_visited_path = visited_path + [new_piece_pos]
        all_resulting_states.extend(
            _get_all_final_states_after_chain_for_ia(state_after_chain_m, player_for_chain, new_piece_pos, new_visited_path)
        )
    return all_resulting_states if all_resulting_states else [current_s]
