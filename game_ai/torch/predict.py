from pathlib import Path
from .model import ChessCNN
import chess
import numpy as np
import torch
import random
from pydantic import BaseModel, ConfigDict
from logger import get_logger
log = get_logger(__name__)

class ChessUtils(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    board: chess.Board

    def convert2numpy(self) -> np.ndarray:
        board_array = np.zeros((8, 8, 12), dtype=np.float32)
        piece_idx = {
            "p": 0,
            "P": 6,
            "n": 1,
            "N": 7,
            "b": 2,
            "B": 8,
            "r": 3,
            "R": 9,
            "q": 4,
            "Q": 10,
            "k": 5,
            "K": 11,
        }
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                rank, file = divmod(square, 8)
                board_array[7 - rank, file, piece_idx[piece.symbol()]] = 1.0
        return board_array

    def move(self, model: torch.nn.Module, gpu: bool):
        best_move = None
        best_value = -1.0  # Initialize with a low value
        board = self.board
        
        # Sample a subset of legal moves for efficiency
        # Minimize the number of moves to 100 evaluate
        for move in board.legal_moves:
            board.push(move)
            board_array = ChessUtils(board=board).convert2numpy()
            board_array = np.transpose(board_array, (2, 0, 1))
            board_array = torch.tensor(board_array).float().unsqueeze(0)
            if gpu and torch.cuda.is_available():
                board_array = board_array.to("cuda")
            value = model(board_array).item()
            board.pop()
            if value > best_value:
                best_value = value
                best_move = move
        return best_move


class ChessGame:
    def __init__(self, board: chess.Board, model: torch.nn.Module, gpu: bool = False):
        """Initializes the ChessGame class.

        Args:
            gpu (bool, optional): Flag indicating whether to use GPU. Defaults to False.
            mcts (bool, optional): Flag indicating whether to use Monte Carlo Tree Search.
        """
        self.board = board
        self.model = model
        self.gpu = gpu
        if self.gpu and torch.cuda.is_available():
            self.model.to("cuda:0")

    def move(self):
        if not self.board.is_game_over():
            return ChessUtils(board=self.board).move(self.model, self.gpu)

def load_CNN_model(model_path: Path | None = None) -> torch.nn.Module:
    if model_path is None:
        model_path = Path(__file__).parent.joinpath("models", "chess_model.ckpt")
    return ChessCNN.load_from_checkpoint(model_path)

