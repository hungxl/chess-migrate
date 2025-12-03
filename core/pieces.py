"""Chess piece classes."""

from typing import Optional, TYPE_CHECKING
from .types import PieceType, Color, Position

if TYPE_CHECKING:
    from .board import Board
    import pygame


class Piece:
    def __init__(self, color: Color, piece_type: PieceType, position: Position):
        self.color = color
        self.piece_type = piece_type
        self.position = position
        self.has_moved = False
        self.image: Optional['pygame.Surface'] = None
    
    def get_image_filename(self) -> str:
        color_prefix = self.color.value
        piece_name = self.piece_type.value
        return f"{color_prefix}_{piece_name}.png"
    
    def get_potential_moves(self, board: 'Board') -> list[Position]:
        """Get all potential moves without considering check."""
        raise NotImplementedError
    
    def get_valid_moves(self, board: 'Board') -> list[Position]:
        """Get valid moves (filters out moves that leave king in check)."""
        potential_moves = self.get_potential_moves(board)
        valid_moves = []
        
        for move_pos in potential_moves:
            if not board.would_be_in_check_after_move(self.position, move_pos, self.color):
                valid_moves.append(move_pos)
        
        return valid_moves
    
    def copy(self) -> 'Piece':
        """Create a copy of this piece."""
        new_piece = self.__class__(self.color, self.piece_type, 
                                    Position(self.position.row, self.position.col))
        new_piece.has_moved = self.has_moved
        new_piece.image = self.image
        return new_piece


class Pawn(Piece):
    def __init__(self, color: Color, position: Position):
        super().__init__(color, PieceType.PAWN, position)
    
    def get_potential_moves(self, board: 'Board') -> list[Position]:
        moves = []
        direction = -1 if self.color == Color.WHITE else 1
        start_row = 6 if self.color == Color.WHITE else 1
        
        # Forward move
        one_forward = Position(self.position.row + direction, self.position.col)
        if one_forward.is_valid() and board.get_piece(one_forward) is None:
            moves.append(one_forward)
            
            # Double forward from starting position
            if self.position.row == start_row:
                two_forward = Position(self.position.row + 2 * direction, self.position.col)
                if two_forward.is_valid() and board.get_piece(two_forward) is None:
                    moves.append(two_forward)
        
        # Diagonal captures
        for col_offset in [-1, 1]:
            capture_pos = Position(self.position.row + direction, self.position.col + col_offset)
            if capture_pos.is_valid():
                target = board.get_piece(capture_pos)
                if target is not None and target.color != self.color:
                    moves.append(capture_pos)
                # En passant
                elif board.en_passant_target == capture_pos:
                    moves.append(capture_pos)
        
        return moves


class Rook(Piece):
    def __init__(self, color: Color, position: Position):
        super().__init__(color, PieceType.ROOK, position)
    
    def get_potential_moves(self, board: 'Board') -> list[Position]:
        return get_straight_moves(self, board)


class Knight(Piece):
    def __init__(self, color: Color, position: Position):
        super().__init__(color, PieceType.KNIGHT, position)
    
    def get_potential_moves(self, board: 'Board') -> list[Position]:
        moves = []
        offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for row_off, col_off in offsets:
            new_pos = Position(self.position.row + row_off, self.position.col + col_off)
            if new_pos.is_valid():
                target = board.get_piece(new_pos)
                if target is None or target.color != self.color:
                    moves.append(new_pos)
        
        return moves


class Bishop(Piece):
    def __init__(self, color: Color, position: Position):
        super().__init__(color, PieceType.BISHOP, position)
    
    def get_potential_moves(self, board: 'Board') -> list[Position]:
        return get_diagonal_moves(self, board)


class Queen(Piece):
    def __init__(self, color: Color, position: Position):
        super().__init__(color, PieceType.QUEEN, position)
    
    def get_potential_moves(self, board: 'Board') -> list[Position]:
        return get_straight_moves(self, board) + get_diagonal_moves(self, board)


class King(Piece):
    def __init__(self, color: Color, position: Position):
        super().__init__(color, PieceType.KING, position)
    
    def get_potential_moves(self, board: 'Board') -> list[Position]:
        moves = []
        
        # Normal king moves
        for row_off in [-1, 0, 1]:
            for col_off in [-1, 0, 1]:
                if row_off == 0 and col_off == 0:
                    continue
                new_pos = Position(self.position.row + row_off, self.position.col + col_off)
                if new_pos.is_valid():
                    target = board.get_piece(new_pos)
                    if target is None or target.color != self.color:
                        moves.append(new_pos)
        
        # Castling
        if not self.has_moved and not board.is_in_check(self.color):
            row = self.position.row
            
            # Kingside castling
            kingside_rook = board.get_piece(Position(row, 7))
            if (kingside_rook and isinstance(kingside_rook, Rook) and 
                not kingside_rook.has_moved and
                board.get_piece(Position(row, 5)) is None and
                board.get_piece(Position(row, 6)) is None and
                not board.is_square_attacked(Position(row, 5), self.color) and
                not board.is_square_attacked(Position(row, 6), self.color)):
                moves.append(Position(row, 6))
            
            # Queenside castling
            queenside_rook = board.get_piece(Position(row, 0))
            if (queenside_rook and isinstance(queenside_rook, Rook) and 
                not queenside_rook.has_moved and
                board.get_piece(Position(row, 1)) is None and
                board.get_piece(Position(row, 2)) is None and
                board.get_piece(Position(row, 3)) is None and
                not board.is_square_attacked(Position(row, 2), self.color) and
                not board.is_square_attacked(Position(row, 3), self.color)):
                moves.append(Position(row, 2))
        
        return moves


# ============================================================================
# MOVEMENT HELPERS
# ============================================================================

def get_straight_moves(piece: Piece, board: 'Board') -> list[Position]:
    """Get moves in straight lines (for rook and queen)."""
    moves = []
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    for row_dir, col_dir in directions:
        for distance in range(1, 8):
            new_pos = Position(
                piece.position.row + row_dir * distance,
                piece.position.col + col_dir * distance
            )
            if not new_pos.is_valid():
                break
            
            target = board.get_piece(new_pos)
            if target is None:
                moves.append(new_pos)
            elif target.color != piece.color:
                moves.append(new_pos)
                break
            else:
                break
    
    return moves


def get_diagonal_moves(piece: Piece, board: 'Board') -> list[Position]:
    """Get moves in diagonal lines (for bishop and queen)."""
    moves = []
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    
    for row_dir, col_dir in directions:
        for distance in range(1, 8):
            new_pos = Position(
                piece.position.row + row_dir * distance,
                piece.position.col + col_dir * distance
            )
            if not new_pos.is_valid():
                break
            
            target = board.get_piece(new_pos)
            if target is None:
                moves.append(new_pos)
            elif target.color != piece.color:
                moves.append(new_pos)
                break
            else:
                break
    
    return moves


def create_piece(piece_type: PieceType, color: Color, position: Position) -> Piece:
    """Factory function to create a piece."""
    piece_classes = {
        PieceType.PAWN: Pawn,
        PieceType.ROOK: Rook,
        PieceType.KNIGHT: Knight,
        PieceType.BISHOP: Bishop,
        PieceType.QUEEN: Queen,
        PieceType.KING: King,
    }
    return piece_classes[piece_type](color, position)
