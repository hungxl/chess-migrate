"""Type definitions for chess game."""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .pieces import Piece


class PieceType(Enum):
    PAWN = "Pawn"
    ROOK = "Rook"
    KNIGHT = "Knight"
    BISHOP = "Bishop"
    QUEEN = "Queen"
    KING = "King"


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


@dataclass
class Move:
    start: Position
    end: Position
    piece: 'Piece'
    captured: Optional['Piece'] = None
    is_castling: bool = False
    is_en_passant: bool = False
    promotion_type: Optional[PieceType] = None
    castling_rook_start: Optional[Position] = None
    castling_rook_end: Optional[Position] = None
    # For undo support
    piece_had_moved: bool = False
    rook_had_moved: bool = False
    previous_en_passant: Optional[Position] = None
    
    def to_algebraic(self) -> str:
        """Convert move to algebraic notation."""
        if self.is_castling:
            return "O-O" if self.end.col == 6 else "O-O-O"
        
        piece_symbol = ""
        if self.piece.piece_type != PieceType.PAWN:
            symbols = {
                PieceType.KING: "K",
                PieceType.QUEEN: "Q",
                PieceType.ROOK: "R",
                PieceType.BISHOP: "B",
                PieceType.KNIGHT: "N",
            }
            piece_symbol = symbols.get(self.piece.piece_type, "")
        
        capture = "x" if self.captured or self.is_en_passant else ""
        
        # For pawn captures, include starting file
        start_file = ""
        if self.piece.piece_type == PieceType.PAWN and capture:
            start_file = chr(ord('a') + self.start.col)
        
        dest = self.end.to_algebraic()
        
        promotion = ""
        if self.promotion_type:
            promo_symbols = {
                PieceType.QUEEN: "Q",
                PieceType.ROOK: "R",
                PieceType.BISHOP: "B",
                PieceType.KNIGHT: "N",
            }
            promotion = "=" + promo_symbols.get(self.promotion_type, "Q")
        
        return f"{piece_symbol}{start_file}{capture}{dest}{promotion}"
