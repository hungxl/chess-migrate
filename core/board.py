"""Chess board class with game state management."""

from typing import Optional
import chess
import chess.pgn
import time
from pathlib import Path
from .types import Color, Position, Move
from .pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King, create_piece

import chess
class Board:
    def __init__(self, white_player: str = "Minimax", black_player: str = "Minimax"):
        self.grid: list[list[Optional[Piece]]] = [[None] * 8 for _ in range(8)]
        self.current_turn = Color.WHITE
        self.white_player = white_player
        self.black_player = black_player
        self.move_history: list[Move] = []
        self.redo_stack: list[Move] = []  # For redo functionality
        self.en_passant_target: Optional[Position] = None
        self.white_king_pos: Optional[Position] = None
        self.black_king_pos: Optional[Position] = None
        self.game_over = False
        self.winner: str | None = None
        self.is_stalemate = False
        self.is_main_board = True  # To differentiate between main and AI boards
        self.start_time = 0.0
        self.chess_board = chess.Board() # Important, will migrate to it instead using the whole class in future

        self._setup_initial_position()
        self.setup_record()
    
    def switch_to_bot_mode(self, is_bot_board: bool = True):
        """Set whether this board is in the minimax/ ai mode.
        Recording PGN is only done for the main board."""
        self.is_main_board = not is_bot_board
        if is_bot_board:
            # Create a separate chess.Board for AI calculations
            self._saved_board = self.chess_board.copy()
        else:
            # Restore the main chess.Board
            self.chess_board = self._saved_board


    def setup_record(self):
        self.record = chess.pgn.Game()
        self.record.headers["Event"] = f"{self.white_player} vs {self.black_player} Chess"
        self.record.headers["Date"] = time.strftime("%Y.%m.%d_%H.%M.%S")
        self.record.headers["White"] = self.white_player
        self.record.headers["Black"] = self.black_player
        self.node = self.record

    def save_record(self):
        record_dir=Path(__file__).parent.parent / "records"
        record_dir.mkdir(exist_ok=True)
        
        record = record_dir / f"chess_record_{self.record.headers['Date']}.pgn"
        with open(record, "w", encoding="utf-8") as f:
            print(self.record, file=f)
    
    def _setup_initial_position(self):
        """Set up the initial chess position."""
        # Place pawns
        for col in range(8):
            self.grid[6][col] = Pawn(Color.WHITE, Position(6, col))
            self.grid[1][col] = Pawn(Color.BLACK, Position(1, col))
        
        # Place other pieces
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        
        for col, piece_class in enumerate(piece_order):
            self.grid[7][col] = piece_class(Color.WHITE, Position(7, col))
            self.grid[0][col] = piece_class(Color.BLACK, Position(0, col))
        
        # Track king positions
        self.white_king_pos = Position(7, 4)
        self.black_king_pos = Position(0, 4)

        self.start_time = time.time()
    
    def get_piece(self, pos: Position) -> Optional[Piece]:
        if pos.is_valid():
            return self.grid[pos.row][pos.col]
        return None
    
    def set_piece(self, pos: Position, piece: Optional[Piece]):
        if pos.is_valid():
            self.grid[pos.row][pos.col] = piece
            if piece:
                piece.position = pos
    
    def move_piece(self, start: Position, end: Position, 
                   promotion_type: Optional[chess.PieceType] = None) -> Optional[Move]:
        """Execute a move and return the Move object."""
        piece = self.get_piece(start)
        if piece is None or piece.color != self.current_turn:
            return None
        
        valid_moves = piece.get_valid_moves(self)
        if end not in valid_moves:
            return None
        
        # Clear redo stack when a new move is made
        self.redo_stack.clear()
        
        captured = self.get_piece(end)
        is_castling = False
        is_en_passant = False
        castling_rook_start = None
        castling_rook_end = None
        
        # Save state for undo
        piece_had_moved = piece.has_moved
        rook_had_moved = False
        previous_en_passant = self.en_passant_target
        
        # Check for en passant
        if isinstance(piece, Pawn) and end == self.en_passant_target:
            is_en_passant = True
            capture_row = start.row
            captured = self.get_piece(Position(capture_row, end.col))
            self.set_piece(Position(capture_row, end.col), None)
        
        # Check for castling
        if isinstance(piece, King) and abs(end.col - start.col) == 2:
            is_castling = True
            if end.col == 6:  # Kingside
                castling_rook_start = Position(start.row, 7)
                castling_rook_end = Position(start.row, 5)
            else:  # Queenside
                castling_rook_start = Position(start.row, 0)
                castling_rook_end = Position(start.row, 3)
            
            # Move the rook
            rook = self.get_piece(castling_rook_start)
            if rook:
                rook_had_moved = rook.has_moved
                self.set_piece(castling_rook_start, None)
                self.set_piece(castling_rook_end, rook)
                rook.has_moved = True
        
        # Move the piece
        self.set_piece(start, None)
        self.set_piece(end, piece)
        piece.has_moved = True
        
        # Handle pawn promotion
        original_piece = piece
        if isinstance(piece, Pawn) and (end.row == 0 or end.row == 7):
            if promotion_type is None:
                promotion_type = chess.QUEEN
            new_piece = create_piece(promotion_type, piece.color, end)
            new_piece.has_moved = True
            self.set_piece(end, new_piece)
        
        # Update king position
        if isinstance(piece, King):
            if piece.color == Color.WHITE:
                self.white_king_pos = end
            else:
                self.black_king_pos = end
        
        # Update en passant target
        if isinstance(original_piece, Pawn) and abs(end.row - start.row) == 2:
            self.en_passant_target = Position((start.row + end.row) // 2, start.col)
        else:
            self.en_passant_target = None
        
        # Create move record with undo info
        move = Move(
            start=start, end=end, piece=original_piece, captured=captured,
            is_castling=is_castling, is_en_passant=is_en_passant,
            promotion_type=promotion_type if isinstance(original_piece, Pawn) and (end.row == 0 or end.row == 7) else None,
            castling_rook_start=castling_rook_start,
            castling_rook_end=castling_rook_end,
            piece_had_moved=piece_had_moved,
            rook_had_moved=rook_had_moved,
            previous_en_passant=previous_en_passant,
        )
        # Update internal chess.Board
        chess_move = chess.Move.from_uci(move.to_uci())
        self.chess_board.push(chess_move)

        move.timestamp = time.time()
        self.move_history.append(move)

        # Update PGN record after move (only for main board)
        if self.is_main_board and hasattr(self, 'record') and hasattr(self, 'node'):
            uci = move.to_uci()
            if uci:
                chess_move = chess.Move.from_uci(uci)
                self.node = self.node.add_variation(chess_move)
                # Add time taken as comment if possible
                if len(self.move_history) > 1:
                    prev_move = self.move_history[-2]
                    if hasattr(prev_move, 'timestamp'):
                        time_taken = move.timestamp - prev_move.timestamp
                        self.node.comment = f"Time: {time_taken:.6f}s"
                else:
                    time_taken = move.timestamp - self.start_time
                    self.node.comment = f"Time: {time_taken:.6f}s"
        
        # Switch turn
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        
        # Check for game end
        self._check_game_end()
        
        return move
    
    def undo_move(self) -> Optional[Move]:
        """Undo the last move. Returns the undone move or None if no moves to undo."""
        if not self.move_history:
            return None
        
        move = self.move_history.pop()
        self.redo_stack.append(move)

        undomove = self.chess_board.pop()
        
        # Get the piece at the end position
        piece_at_end = self.get_piece(move.end)
        
        # Handle pawn promotion - restore original pawn
        if move.promotion_type:
            piece_to_restore = move.piece
            piece_to_restore.has_moved = move.piece_had_moved
        else:
            piece_to_restore = piece_at_end
            if piece_to_restore:
                piece_to_restore.has_moved = move.piece_had_moved
        
        # Move piece back
        self.set_piece(move.end, None)
        self.set_piece(move.start, piece_to_restore)
        
        # Restore captured piece
        if move.captured:
            if move.is_en_passant:
                # En passant: captured pawn was on same row as moving pawn started
                capture_pos = Position(move.start.row, move.end.col)
                self.set_piece(capture_pos, move.captured)
            else:
                self.set_piece(move.end, move.captured)
        
        # Handle castling
        if move.is_castling and move.castling_rook_start and move.castling_rook_end:
            rook = self.get_piece(move.castling_rook_end)
            if rook:
                rook.has_moved = move.rook_had_moved
                self.set_piece(move.castling_rook_end, None)
                self.set_piece(move.castling_rook_start, rook)
        
        # Update king position
        if isinstance(move.piece, King):
            if move.piece.color == Color.WHITE:
                self.white_king_pos = move.start
            else:
                self.black_king_pos = move.start
        
        # Restore en passant target
        self.en_passant_target = move.previous_en_passant
        
        # Switch turn back
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        
        # Reset game over state
        self.game_over = False
        self.winner = None
        self.is_stalemate = False
        
        return move
    
    def redo_move(self) -> Optional[Move]:
        """Redo a previously undone move. Returns the redone move or None."""
        if not self.redo_stack:
            return None
        
        move = self.redo_stack.pop()

        self.chess_board.push(chess.Move.from_uci(move.to_uci()))

        # Re-execute the move
        piece = self.get_piece(move.start)
        if piece is None:
            # This shouldn't happen, but handle gracefully
            self.redo_stack.append(move)
            return None
        
        # Handle en passant capture
        if move.is_en_passant:
            capture_pos = Position(move.start.row, move.end.col)
            self.set_piece(capture_pos, None)
        
        # Handle castling
        if move.is_castling and move.castling_rook_start and move.castling_rook_end:
            rook = self.get_piece(move.castling_rook_start)
            if rook:
                self.set_piece(move.castling_rook_start, None)
                self.set_piece(move.castling_rook_end, rook)
                rook.has_moved = True
        
        # Move the piece
        self.set_piece(move.start, None)
        self.set_piece(move.end, piece)
        piece.has_moved = True
        
        # Handle pawn promotion
        if move.promotion_type:
            new_piece = create_piece(move.promotion_type, piece.color, move.end)
            new_piece.has_moved = True
            self.set_piece(move.end, new_piece)
        
        # Update king position
        if isinstance(piece, King):
            if piece.color == Color.WHITE:
                self.white_king_pos = move.end
            else:
                self.black_king_pos = move.end
        
        # Update en passant target
        if isinstance(piece, Pawn) and abs(move.end.row - move.start.row) == 2:
            self.en_passant_target = Position((move.start.row + move.end.row) // 2, move.start.col)
        else:
            self.en_passant_target = None
        
        self.move_history.append(move)
        
        # Switch turn
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        
        # Check for game end
        self._check_game_end()
        
        return move
    
    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return len(self.move_history) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return len(self.redo_stack) > 0
    
    def _check_game_end(self):
        """Check if the game has ended (checkmate or stalemate)."""
        # Check if current player has any valid moves
        has_valid_moves = False
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and piece.color == self.current_turn:
                    if piece.get_valid_moves(self):
                        has_valid_moves = True
                        break
            if has_valid_moves:
                break
        
        if not has_valid_moves:
            self.game_over = True
            if self.is_in_check(self.current_turn):
                # Checkmate - the other player wins
                self.winner = self.white_player if self.current_turn == Color.WHITE else self.black_player
                # Update PGN result
                if hasattr(self, 'record'):
                    self.record.headers["Result"] = "1-0" if self.current_turn == Color.WHITE else "0-1"
            else:
                # Stalemate
                self.is_stalemate = True
                if hasattr(self, 'record'):
                    self.record.headers["Result"] = "1/2-1/2"

        if (self.chess_board.is_insufficient_material() or
            self.chess_board.is_seventyfive_moves() or
            self.chess_board.is_fivefold_repetition() or
            self.chess_board.is_fifty_moves() or
            self.chess_board.is_repetition(3)):
            self.game_over = True
            self.is_stalemate = True
            if hasattr(self, 'record'):
                self.record.headers["Result"] = "1/2-1/2"
        
    
    def is_in_check(self, color: Color) -> bool:
        """Check if the given color's king is in check."""
        king_pos = self.white_king_pos if color == Color.WHITE else self.black_king_pos
        if king_pos is None:
            return False
        return self.is_square_attacked(king_pos, color)
    
    def is_square_attacked(self, pos: Position, by_color: Color) -> bool:
        """Check if a square is attacked by the opponent of the given color."""
        opponent_color = Color.BLACK if by_color == Color.WHITE else Color.WHITE
        
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and piece.color == opponent_color:
                    # For pawns, only check diagonal attacks
                    if isinstance(piece, Pawn):
                        direction = -1 if piece.color == Color.WHITE else 1
                        if (pos.row == piece.position.row + direction and
                            abs(pos.col - piece.position.col) == 1):
                            return True
                    # For kings, check adjacent squares (avoid infinite recursion)
                    elif isinstance(piece, King):
                        if (abs(pos.row - piece.position.row) <= 1 and
                            abs(pos.col - piece.position.col) <= 1):
                            return True
                    else:
                        if pos in piece.get_potential_moves(self):
                            return True
        
        return False
    
    def would_be_in_check_after_move(self, start: Position, end: Position, color: Color) -> bool:
        """Simulate a move and check if it would leave the king in check."""
        # Save state
        piece = self.get_piece(start)
        captured = self.get_piece(end)
        old_en_passant = self.en_passant_target
        
        en_passant_captured_pos = None
        en_passant_captured_piece = None
        
        # Handle en passant capture
        if isinstance(piece, Pawn) and end == self.en_passant_target:
            en_passant_captured_pos = Position(start.row, end.col)
            en_passant_captured_piece = self.get_piece(en_passant_captured_pos)
            self.set_piece(en_passant_captured_pos, None)
        
        # Make the move
        self.set_piece(start, None)
        self.set_piece(end, piece)
        
        # Update king position temporarily if moving king
        old_king_pos = None
        if isinstance(piece, King):
            if color == Color.WHITE:
                old_king_pos = self.white_king_pos
                self.white_king_pos = end
            else:
                old_king_pos = self.black_king_pos
                self.black_king_pos = end
        
        # Check if in check
        in_check = self.is_in_check(color)
        
        # Restore state
        self.set_piece(start, piece)
        self.set_piece(end, captured)
        if piece:
            piece.position = start
        self.en_passant_target = old_en_passant
        
        if en_passant_captured_pos:
            self.set_piece(en_passant_captured_pos, en_passant_captured_piece)
        
        if old_king_pos:
            if color == Color.WHITE:
                self.white_king_pos = old_king_pos
            else:
                self.black_king_pos = old_king_pos
        
        return in_check
    
    def get_current_move_index(self) -> int:
        """Get the current move index (for display purposes)."""
        return len(self.move_history)
