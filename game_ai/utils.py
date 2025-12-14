from core.types import Color, Position
from core.board import Board
from typing import Optional
import random
import chess
###
### Note: Check later piece variable in quiescence_search function is needed
###

# Constants for Minimax
QUIESCENCE_MAX_DEPTH = 2
# Constants for Minimax
MAX_SEARCH_DEPTH = 2
# Piece values for the evaluation function (in centipawns/pawn units)
PIECE_VALUES = {
    chess.PAWN: 10,
    chess.KNIGHT: 30,
    chess.BISHOP: 35,
    chess.ROOK: 60,
    chess.QUEEN: 90,
    chess.KING: 9999, 
}



def evaluate_board(board: Board) -> float:
    """
    Scores the board based on pieces value and total of possible moves of sides.
    Positive score favors White, negative favors Black.
    """
    if board.game_over:
        if board.is_stalemate:
            return 0.0 
        if board.winner == Color.WHITE: # Checkmate value
            return float('inf')  
        elif board.winner == Color.BLACK:
            return float('-inf')
        return 0.0
     
    score = 0
    for r in range(8):
        for c in range(8):
            piece = board.grid[r][c]
            if piece:
                value = PIECE_VALUES.get(piece.piece_type, 0)
                if piece.color == Color.WHITE:
                    score += value
                else:
                    score -= value
                    
    white_moves = len(_get_all_legal_moves(board, Color.WHITE))
    black_moves = len(_get_all_legal_moves(board, Color.BLACK))
    score += (white_moves - black_moves) * 1
    return score


def quiescence_search(board: Board, alpha: float, beta: float, current_depth: int) -> float:
    """
    Performs a shallow search to prevent unstable positions.
    """
    # Base case
    if board.game_over or current_depth >= QUIESCENCE_MAX_DEPTH:
        return evaluate_board(board)
    
    stand_pat = evaluate_board(board)

    if board.current_turn == Color.WHITE: # Minimizing player (Black)
        alpha = max(alpha, stand_pat)
        if alpha >= beta:
            return beta
        # Generate ALL legal moves
        moves = order_moves(board, _get_all_legal_moves(board, Color.WHITE))
        # Only consider CAPTURES and CHECKS for the quiescence search 
        for start, end in moves:
            # piece = board.get_piece(start)
            target = board.get_piece(end)
            # Check for captures or en passant target
            if target or end == board.en_passant_target: 
                board.move_piece(start, end)
                # Recursive call + switches maximum/minimizing 
                score = quiescence_search(board, alpha, beta, current_depth + 1)
                board.undo_move()
                alpha = max(alpha, score)
                if alpha >= beta:
                    return beta
        return alpha
    
    else: # Minimizing player (Black)
        beta = min(beta, stand_pat)
        if alpha >= beta:
            return alpha   
        moves = order_moves(board, _get_all_legal_moves(board, Color.BLACK))
        for start, end in moves:
            # piece = board.get_piece(start)
            target = board.get_piece(end)
            # Check for captures or en passant target
            if target or end == board.en_passant_target: 
                board.move_piece(start, end)

                score = quiescence_search(board, alpha, beta, current_depth + 1)
                board.undo_move() 
                beta = min(beta, score)
                if alpha >= beta:
                    return alpha
        return beta
    
def minimax_alpha_beta(board: Board, depth: int, alpha: float, beta: float, 
                       is_maximizing_player: bool) -> float:
    """
    The recursive minimax algorithm with alpha-beta pruning.
    :return: The best score found for the current position.
    """
    current_color = board.current_turn

    # Base Case 
    if depth == 0 or board.game_over:
        if board.game_over:
            return evaluate_board(board)
        return quiescence_search(board, alpha, beta, 0)
    
    moves = order_moves(board, _get_all_legal_moves(board, current_color))
    if not moves:
        board._check_game_end() # check update game_over status
        return evaluate_board(board) 
    
    if is_maximizing_player:  # Maximum for White
        max_eval = float('-inf')
        for start, end in moves:
            board.move_piece(start, end)    
            # Recursive call + switches maximum/minimizing 
            evaluation = minimax_alpha_beta(board, depth - 1, alpha, beta, False)     
            
            board.undo_move()  
            max_eval = max(max_eval, evaluation)
            alpha = max(alpha, max_eval)

            if alpha >= beta:  # Alpha-Beta Pruning
                break
        return max_eval
    
    else: # Minimizing for Black
        min_eval = float('inf')
        for start, end in moves:
            board.move_piece(start, end)
            evaluation = minimax_alpha_beta(board, depth - 1, alpha, beta, True)

            board.undo_move()
            min_eval = min(min_eval, evaluation)
            beta = min(beta, min_eval)

            if alpha >= beta:
                break
        return min_eval
    

def find_best_move(board: Board) -> Optional[tuple[Position, Position]]:
    """
    Finds the best move for the current player using Minimax with Alpha-Beta Pruning.
    
    :param board: The current Board state.
    :return: A tuple (start_pos, end_pos) representing the best move.
    """
    current_color = board.current_turn
    is_maximizing = current_color == Color.WHITE
    best_score = float('-inf') if is_maximizing else float('inf')
    best_move = None
    # get
    all_legal_moves = _get_all_legal_moves(board, current_color)
    if not all_legal_moves:
        return None 
    # start 
    for start, end in all_legal_moves:
        board.move_piece(start, end)
        score = minimax_alpha_beta(
            board=board,
            depth=MAX_SEARCH_DEPTH - 1, # Decrement depth for the first recursive call
            alpha=float('-inf'),
            beta=float('inf'),
            is_maximizing_player=not is_maximizing # Switch turn for the recursive call
        )
        board.undo_move()
        if is_maximizing:
            if score > best_score:
                best_score = score
                best_move = (start, end)
        else:
            if score < best_score:
                best_score = score
                best_move = (start, end)   
    # print(f"AI chose move {best_move} with score {best_score}")
    return best_move


def _get_all_legal_moves(board: Board, color: Color) -> list[tuple[Position, Position]]:
    """Generates all legal (start_pos, end_pos) move pairs for a given color."""
    moves = []
    for r in range(8):
        for c in range(8):
            piece = board.grid[r][c]
            if piece and piece.color == color:
                start_pos = Position(r, c)
                # piece.get_valid_moves handles checking for leaving king in check
                for end_pos in piece.get_valid_moves(board): 
                    moves.append((start_pos, end_pos))
    return moves

################################################################################################################

def find_random_move(board: 'Board') -> Optional[tuple[Position, Position]]:
    current_color = board.current_turn
    
    all_legal_moves = _get_all_legal_moves(board, current_color)
    
    if not all_legal_moves:
        return None 
    
    random_move = random.choice(all_legal_moves)
    return random_move

##################################################################################################################

def order_moves(board: Board, moves: list[tuple[Position, Position]]) -> list[tuple[Position, Position]]:
    """Helper function for orders moves to improve alpha-beta pruning efficiency."""
    def move_score(move):
        start, end = move
        target = board.get_piece(end)
        if target:  # Captures
            return PIECE_VALUES.get(target.piece_type, 0)
        return 0  # Non-captures have lower priority

    return sorted(moves, key=move_score, reverse=True)