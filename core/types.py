"""Type definitions for chess game."""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
from time import time
import chess

if TYPE_CHECKING:
    from .pieces import Piece

DICT_PIECE_TYPES = {
            chess.PAWN: "Pawn",
            chess.ROOK: "Rook",
            chess.KNIGHT: "Knight",
            chess.BISHOP: "Bishop",
            chess.QUEEN: "Queen",
            chess.KING: "King"
            }

# class PieceType(Enum):
#         chess.PAWN = "Pawn"
#         chess.ROOK = "Rook"
#         chess.KNIGHT = "Knight"
#         chess.BISHOP = "Bishop"
#         chess.QUEEN = "Queen"
#         chess.KING = "King"


class Color(Enum):
    WHITE = "W"
    BLACK = "B"


@dataclass
class Position:
    row: int
    col: int
    
    def __hash__(self):
        return hash((self.row, self.col))
    
    def __eq__(self, other):
        if isinstance(other, Position):
            return self.row == other.row and self.col == other.col
        return False
    
    def is_valid(self) -> bool:
        return 0 <= self.row < 8 and 0 <= self.col < 8
    
    def to_algebraic(self) -> str:
        """Convert to algebraic notation (e.g., 'e4')."""
        col_letter = chr(ord('a') + self.col)
        row_number = 8 - self.row
        return f"{col_letter}{row_number}"
    
    @classmethod
    def from_algebraic(cls, notation: str) -> 'Position':
        """Create Position from algebraic notation (e.g., 'e4')."""
        col = ord(notation[0]) - ord('a')
        row = 8 - int(notation[1])
        return cls(row, col)
    


@dataclass
class Move:
    start: Position
    end: Position
    piece: 'Piece'
    captured: Optional['Piece'] = None
    is_castling: bool = False
    is_en_passant: bool = False
    promotion_type: Optional[chess.PieceType] = None
    castling_rook_start: Optional[Position] = None
    castling_rook_end: Optional[Position] = None
    # For undo support
    piece_had_moved: bool = False
    rook_had_moved: bool = False
    previous_en_passant: Optional[Position] = None
    # For recording time taken per move
    timestamp: float = time()
    
    def to_algebraic(self) -> str:
        """Convert move to algebraic notation."""
        if self.is_castling:
            return "O-O" if self.end.col == 6 else "O-O-O"
        
        piece_symbol = ""
        if self.piece.piece_type != chess.PAWN:
            symbols = {
                chess.KING: "K",
                chess.QUEEN: "Q",
                chess.ROOK: "R",
                chess.BISHOP: "B",
                chess.KNIGHT: "N",
            }
            piece_symbol = symbols.get(self.piece.piece_type, "")
        
        capture = "x" if self.captured or self.is_en_passant else ""
        
        # For pawn captures, include starting file
        start_file = ""
        if self.piece.piece_type == chess.PAWN and capture:
            start_file = chr(ord('a') + self.start.col)
        
        dest = self.end.to_algebraic()
        
        promotion = ""
        if self.promotion_type:
            promo_symbols = {
                chess.QUEEN: "Q",
                chess.ROOK: "R",
                chess.BISHOP: "B",
                chess.KNIGHT: "N",
            }
            promotion = "=" + promo_symbols.get(self.promotion_type, "Q")
        
        return f"{piece_symbol}{start_file}{capture}{dest}{promotion}"
    
    def to_uci(self) -> str:
        """Convert move to UCI notation (e.g., e2e4, e7e8q), including castling."""
        # Handle castling
        if self.is_castling:
            # White: O-O (kingside) = e1g1, O-O-O (queenside) = e1c1
            # Black: O-O (kingside) = e8g8, O-O-O (queenside) = e8c8
            if self.start.row == 7:  # White
                if self.end.col == 6:
                    return "e1g1"
                else:
                    return "e1c1"
            elif self.start.row == 0:  # Black
                if self.end.col == 6:
                    return "e8g8"
                else:
                    return "e8c8"
        # Normal move
        start_sq = chr(ord('a') + self.start.col) + str(8 - self.start.row)
        end_sq = chr(ord('a') + self.end.col) + str(8 - self.end.row)
        promo = ''
        if self.promotion_type:
            promo_map = {
                chess.QUEEN: 'q',
                chess.ROOK: 'r',
                chess.BISHOP: 'b',
                chess.KNIGHT: 'n',
            }
            promo = promo_map.get(self.promotion_type, 'q')
        return f"{start_sq}{end_sq}{promo}"
