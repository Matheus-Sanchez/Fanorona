"""
Gera movimentos legais para Fanorona a partir de um estado e lista opcional de peças.
Implementa as regras de movimento e captura obrigatória (aproximação, afastamento, cadeias).
"""
from typing import List, Tuple, Optional

State = List[List[str]]
Move = Tuple[Tuple[int, int], Tuple[int, int]]  # ((lin_atual, col_atual), (lin_nova, col_nova))

DIRECOES_8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
DIRECOES_4 = [(-1, 0), (0, -1), (0, 1), (1, 0)]


def verificar_pecas_captura(state: State, linha: int, coluna: int,
                            dir_linha: int, dir_coluna: int, oponente: str) -> List[Tuple[int, int]]:
    """
    Verifica se há peças do oponente na direção especificada até encontrar um vazio.
    Retorna lista de coordenadas capturáveis.
    """
    capturaveis = []
    i, j = linha + dir_linha, coluna + dir_coluna
    while 0 <= i < len(state) and 0 <= j < len(state[0]):
        if state[i][j] == oponente:
            capturaveis.append((i, j))
        else:
            break
        i += dir_linha
        j += dir_coluna
    return capturaveis


def possiveis_capturas(state: State, linha: int, coluna: int, player: str, visited_in_chain: Optional[List[Tuple[int, int]]] = None) -> List[Move]:
    """
    Para uma peça em (linha, coluna), retorna movimentações para casas vazias que resultam em captura,
    avoiding destinations in visited_in_chain.
    """
    if state is None: # Defensive check
        # Log this or handle, as state should not be None here
        print(f"Error: possiveis_capturas received state as None. Piece: ({linha},{coluna}), Player: {player}")
        return []

    oponente = 'b' if player == 'v' else 'v'
    direcoes = DIRECOES_8 if (linha % 2 == coluna % 2) else DIRECOES_4
    moves = []
    for dl, dc in direcoes:
        ni, nj = linha + dl, coluna + dc

        if visited_in_chain and (ni, nj) in visited_in_chain:
            continue  # Não pode mover para um quadrado já visitado nesta cadeia

        # Verifica se a casa de destino está vazia
        if 0 <= ni < len(state) and 0 <= nj < len(state[0]) and state[ni][nj] == "-":
            # Aproximação
            if verificar_pecas_captura(state, ni, nj, dl, dc, oponente):
                moves.append(((linha, coluna), (ni, nj)))
            # Afastamento (garante que é um movimento distinto se ambas as condições forem atendidas para o mesmo (ni,nj))
            elif verificar_pecas_captura(state, linha, coluna, -dl, -dc, oponente):
                 # Verifica se este movimento via afastamento já foi adicionado pela aproximação
                is_duplicate = False
                for existing_move in moves:
                    if existing_move[0] == (linha,coluna) and existing_move[1] == (ni,nj):
                        is_duplicate = True
                        break
                if not is_duplicate:
                    moves.append(((linha, coluna), (ni, nj)))
    return moves


def generate_moves(state: State, player: str,
                   movable_pieces: Optional[List[Tuple[int, int]]] = None,
                   capturas_apenas: bool = False,
                   active_piece_pos: Optional[Tuple[int, int]] = None,
                   visited_in_chain: Optional[List[Tuple[int, int]]] = None) -> List[Move]:
    """
    Gera lista completa de movimentos para `player` no `state`.
    - Se `active_piece_pos` é fornecido, gera movimentos apenas para essa peça.
    - Se `visited_in_chain` é fornecido, os movimentos gerados não irão aterrissar nesses quadrados.
    - Prioriza capturas, a menos que `capturas_apenas` seja Falso e nenhuma captura seja encontrada.
    """
    if active_piece_pos:
        peças = [active_piece_pos]
        # Se uma peça ativa está definida (captura em cadeia), estamos sempre procurando capturas primeiro.
        # A flag capturas_apenas é mais para a geração inicial de movimentos.
    elif movable_pieces is not None:
        peças = movable_pieces
    else:
        peças = [(i, j) for i, row in enumerate(state) for j, c in enumerate(row) if c == player]

    capture_moves: List[Move] = []
    for r, c in peças:
        capture_moves.extend(possiveis_capturas(state, r, c, player, visited_in_chain))

    if capturas_apenas: # Estritamente apenas capturas
        return capture_moves
    
    if capture_moves: # Se alguma captura é encontrada para as peças consideradas, elas são obrigatórias
        return capture_moves

    # Se não houver capturas, gera movimentos regulares (respeitando active_piece e visited_in_chain se definidos)
    regular_moves: List[Move] = []
    if not active_piece_pos: # Movimentos regulares geralmente não são para uma peça já em uma cadeia, a menos que seja uma continuação sem captura (não é regra do Fanorona)
        for r, c in peças: # Reitera se não active_piece_pos, ou usa o original 'peças'
            regular_moves.extend(possiveis_movimentos(state, r, c, player, visited_in_chain))
    # Se active_piece_pos está definido, mas nenhuma captura foi encontrada, significa que a cadeia terminou.
    # Portanto, uma lista vazia deve ser retornada pelo manipulador da cadeia.
    # Esta função, se active_piece_pos está definida e nenhuma captura, deve retornar vazia.
    # A lógica para voltar a movimentos regulares é para um turno geral, não no meio da cadeia.
    
    # Lógica corrigida:
    # 1. Se active_piece_pos está definida, estamos em uma cadeia: retorna apenas capturas para essa peça.
    if active_piece_pos:
        # Já calculamos capture_moves para esta peça.
        return capture_moves

    # 2. Se não é uma peça ativa (turno normal):
    #    Primeiro, verifica todas as peças para capturas. Se houver, esses são os únicos movimentos.
    all_pieces_captures: List[Move] = []
    if not movable_pieces and not active_piece_pos: # apenas recalcule se não estiver feito para peças específicas
        all_peças_for_captures = [(i, j) for i, row in enumerate(state) for j, c in enumerate(row) if c == player]
        for r_all, c_all in all_peças_for_captures:
            all_pieces_captures.extend(possiveis_capturas(state, r_all, c_all, player, visited_in_chain)) # visited_in_chain é provavelmente None aqui

    if all_pieces_captures:
        return all_pieces_captures

    # 3. Se não houver capturas em nenhum lugar do tabuleiro para o jogador, então gera movimentos regulares.
    #    (A lista 'peças' já está configurada para esse caso se movable_pieces for None)
    for r, c in peças:
        regular_moves.extend(possiveis_movimentos(state, r, c, player, visited_in_chain)) # visited_in_chain é provavelmente None aqui
    return regular_moves


def possiveis_movimentos(state: State, linha: int, coluna: int, player: str, visited_in_chain: Optional[List[Tuple[int, int]]] = None) -> List[Move]:
    """
    Retorna movimentos livres (não captura) para a peça em (linha, coluna),
    evitando destinos em visited_in_chain.
    Esta função não deve retornar capturas. generate_moves trata da prioridade de captura.
    """
    direcoes = DIRECOES_8 if (linha % 2 == coluna % 2) else DIRECOES_4
    livres = []
    for dl, dc in direcoes:
        ni, nj = linha + dl, coluna + dc

        if visited_in_chain and (ni, nj) in visited_in_chain:
            continue

        if 0 <= ni < len(state) and 0 <= nj < len(state[0]) and state[ni][nj] == "-":
            livres.append(((linha, coluna), (ni, nj)))
    return livres


def aplicar_movimento(state: State, move: Move, player: str) -> State:
    """
    Aplica um movimento (incluindo captura simples) e retorna o novo estado.
    """
    if state is None:
        raise ValueError("aplicar_movimento recebeu um estado None, o que não deveria acontecer.")
        
    origem, destino = move
    novo_estado = [list(l) for l in state]  # cópia profunda

    # Verifica se o destino está vazio ANTES de aplicar o movimento
    # Esta verificação é crucial e estava faltando aqui.
    # generate_moves deveria garantir isso, mas uma verificação dupla é mais segura.
    if novo_estado[destino[0]][destino[1]] != "-":
        # This indicates a bug in generate_moves if it happens,
        # as generate_moves should only produce moves to empty squares.
        raise ValueError(f"Bug: aplicar_movimento tentou mover para uma posição ocupada: {destino} a partir de {origem}. Estado: {state}")

    # mover peça
    novo_estado[origem[0]][origem[1]] = "-"
    novo_estado[destino[0]][destino[1]] = player
    return novo_estado
