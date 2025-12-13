
import chess
from core.board import Board
from game_ai.torch.predict import ChessGame, load_CNN_model
from .utils import find_random_move, find_best_move
from core.types import Position
from logger import get_logger, log_function_call, log_performance
log = get_logger(__name__)

def random_bot_move(board: Board):
    bot_move = find_random_move(board)
    if bot_move is None:
        return None
    start, end = bot_move 
    promo = chess.QUEEN  # Bot default promotion to Queen if needed
    return (start, end, promo)


def minimax_bot_move(board: Board):
        if board.game_over:
            return
        if board.chess_board.move_stack == [] and board.chess_board.turn == chess.WHITE:
             return random_bot_move(board)
        

        board.switch_to_bot_mode(True)  # Ensure AI boards are bot board
        # Find best move using Minimax with Alpha-Beta Pruning
        bot_move = find_best_move(board)
        board.switch_to_bot_mode(False)  # Switch back to main board

        if bot_move is None:
            return
        start, end = bot_move 
        promo = chess.QUEEN  # Bot default promotion to Queen if needed
        return (start, end, promo)


model = load_CNN_model()

@log_function_call()
def torch_bot_move(board: Board):
    global model

    if board.game_over:
        return
    
    board.switch_to_bot_mode(True)
    # Use the predictor to get the best move from the neural network
    
    chess_move = ChessGame(board=board.chess_board.copy(), model=model).move()
    board.switch_to_bot_mode(False)

    if chess_move is None:
        return
    log.debug(f"Torch bot raw move: {chess_move.uci}")
    
    start = Position.from_algebraic(chess.square_name(chess_move.from_square))
    end = Position.from_algebraic(chess.square_name(chess_move.to_square))
    promo = chess_move.promotion if chess_move.promotion is not None else None
    log.debug(f"Torch bot selected move: {start.to_algebraic()} to {end.to_algebraic()} with promo {promo}")
    return (start, end, promo)
