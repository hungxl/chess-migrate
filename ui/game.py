"""Main chess game UI class."""

import pygame
import os
from typing import Optional

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.constants import (
    BOARD_SIZE, SQUARE_SIZE, PANEL_WIDTH, WINDOW_WIDTH, WINDOW_HEIGHT,
    BOARD_OFFSET_X, BOARD_OFFSET_Y, FPS,
    COLOR_HIGHLIGHT, COLOR_SELECTED, COLOR_LAST_MOVE, COLOR_CHECK,
    COLOR_BG, COLOR_PANEL_BG, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_PROMOTION_BG,
    COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_BUTTON_DISABLED, COLOR_MOVE_HIGHLIGHT
)
from core.types import PieceType, Color, Position, Move
from core.pieces import Piece, Pawn
from core.board import Board


class Button:
    """Simple button class for UI."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 font: pygame.font.Font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.enabled = True
        self.hovered = False
    
    def draw(self, screen: pygame.Surface):
        if not self.enabled:
            color = COLOR_BUTTON_DISABLED
            text_color = (100, 100, 100)
        elif self.hovered:
            color = COLOR_BUTTON_HOVER
            text_color = COLOR_TEXT
        else:
            color = COLOR_BUTTON
            text_color = COLOR_TEXT
        
        pygame.draw.rect(screen, color, self.rect, border_radius=4)
        
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_mouse_motion(self, pos: tuple[int, int]):
        self.hovered = self.rect.collidepoint(pos)
    
    def is_clicked(self, pos: tuple[int, int]) -> bool:
        return self.enabled and self.rect.collidepoint(pos)


class MoveHistoryPanel:
    """Panel showing move history in algebraic notation."""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.scroll_offset = 0
        self.max_visible_moves = 20
        self.selected_move_index: Optional[int] = None
        self.font = pygame.font.Font(None, 22)
        self.title_font = pygame.font.Font(None, 26)
        self.row_height = 22
    
    def draw(self, screen: pygame.Surface, moves: list[Move], current_index: int):
        # Draw background
        pygame.draw.rect(screen, COLOR_PANEL_BG, self.rect)
        
        # Draw title
        title = self.title_font.render("Move History", True, COLOR_TEXT)
        title_rect = title.get_rect(centerx=self.rect.centerx, top=self.rect.top + 8)
        screen.blit(title, title_rect)
        
        # Draw moves area
        moves_area = pygame.Rect(
            self.rect.x + 8,
            self.rect.y + 35,
            self.rect.width - 16,
            self.rect.height - 45
        )
        
        # Calculate which moves to show
        move_pairs = []
        for i in range(0, len(moves), 2):
            white_move = moves[i] if i < len(moves) else None
            black_move = moves[i + 1] if i + 1 < len(moves) else None
            move_pairs.append((white_move, black_move))
        
        # Auto-scroll to show current move
        visible_rows = moves_area.height // self.row_height
        current_row = (current_index) // 2
        if current_row >= self.scroll_offset + visible_rows:
            self.scroll_offset = current_row - visible_rows + 1
        elif current_row < self.scroll_offset:
            self.scroll_offset = current_row
        
        # Draw move pairs
        y = moves_area.top
        for pair_idx in range(self.scroll_offset, len(move_pairs)):
            if y + self.row_height > moves_area.bottom:
                break
            
            white_move, black_move = move_pairs[pair_idx]
            move_num = pair_idx + 1
            
            # Move number
            num_text = self.font.render(f"{move_num}.", True, COLOR_TEXT_DIM)
            screen.blit(num_text, (moves_area.x, y + 2))
            
            # White move
            if white_move:
                white_idx = pair_idx * 2
                is_current = white_idx == current_index - 1
                white_text = white_move.to_algebraic()
                
                if is_current:
                    # Highlight current move
                    highlight_rect = pygame.Rect(
                        moves_area.x + 28, y,
                        70, self.row_height
                    )
                    pygame.draw.rect(screen, COLOR_MOVE_HIGHLIGHT, highlight_rect, border_radius=3)
                
                text_color = COLOR_TEXT if is_current else COLOR_TEXT_DIM
                text_surface = self.font.render(white_text, True, text_color)
                screen.blit(text_surface, (moves_area.x + 32, y + 2))
            
            # Black move
            if black_move:
                black_idx = pair_idx * 2 + 1
                is_current = black_idx == current_index - 1
                black_text = black_move.to_algebraic()
                
                if is_current:
                    highlight_rect = pygame.Rect(
                        moves_area.x + 100, y,
                        70, self.row_height
                    )
                    pygame.draw.rect(screen, COLOR_MOVE_HIGHLIGHT, highlight_rect, border_radius=3)
                
                text_color = COLOR_TEXT if is_current else COLOR_TEXT_DIM
                text_surface = self.font.render(black_text, True, text_color)
                screen.blit(text_surface, (moves_area.x + 104, y + 2))
            
            y += self.row_height
        
        # Draw empty state
        if not moves:
            empty_text = self.font.render("No moves yet", True, COLOR_TEXT_DIM)
            empty_rect = empty_text.get_rect(center=moves_area.center)
            screen.blit(empty_text, empty_rect)
    
    def handle_scroll(self, direction: int, total_moves: int):
        """Handle mouse scroll."""
        max_pairs = (total_moves + 1) // 2
        visible_rows = (self.rect.height - 45) // self.row_height
        max_scroll = max(0, max_pairs - visible_rows)
        
        self.scroll_offset = max(0, min(max_scroll, self.scroll_offset - direction))


class ChessGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Chess")
        self.clock = pygame.time.Clock()
        
        self.board = Board()
        self.selected_piece: Optional[Piece] = None
        self.valid_moves: list[Position] = []
        self.promoting_pawn_move: Optional[tuple[Position, Position]] = None
        
        # Load assets
        self._load_images()
        self._load_sounds()
        
        # Create surfaces
        self._create_highlight_surfaces()
        
        # Create UI elements
        self._create_ui()
    
    def _load_images(self):
        """Load all piece images and the board."""
        # Get base path (go up from ui/ to project root)
        base_path = os.path.dirname(os.path.dirname(__file__))
        assets_path = os.path.join(base_path, "assets", "img")
        
        # Load board
        board_path = os.path.join(assets_path, "boards", "board_plain_01.png")
        self.board_image = pygame.image.load(board_path).convert()
        self.board_image = pygame.transform.scale(self.board_image, (BOARD_SIZE, BOARD_SIZE))
        
        # Load pieces
        pieces_path = os.path.join(assets_path, "16x32 pieces")
        self.piece_images = {}
        
        for color in Color:
            for piece_type in PieceType:
                filename = f"{color.value}_{piece_type.value}.png"
                filepath = os.path.join(pieces_path, filename)
                if os.path.exists(filepath):
                    img = pygame.image.load(filepath).convert_alpha()
                    # Scale to fit square (maintain aspect ratio, fit height to square)
                    scale_factor = SQUARE_SIZE / img.get_height()
                    new_width = int(img.get_width() * scale_factor)
                    new_height = SQUARE_SIZE
                    img = pygame.transform.scale(img, (new_width, new_height))
                    self.piece_images[(color, piece_type)] = img
        
        # Assign images to pieces on board
        self._assign_piece_images()
    
    def _assign_piece_images(self):
        """Assign images to all pieces on the board."""
        for row in range(8):
            for col in range(8):
                piece = self.board.grid[row][col]
                if piece:
                    piece.image = self.piece_images.get((piece.color, piece.piece_type))
    
    def _load_sounds(self):
        """Load sound effects."""
        base_path = os.path.dirname(os.path.dirname(__file__))
        sounds_path = os.path.join(base_path, "assets", "sound")
        
        self.sound_move = None
        self.sound_capture = None
        self.sound_notify = None
        
        try:
            move_path = os.path.join(sounds_path, "move-self.mp3")
            if os.path.exists(move_path):
                self.sound_move = pygame.mixer.Sound(move_path)
            
            capture_path = os.path.join(sounds_path, "capture.mp3")
            if os.path.exists(capture_path):
                self.sound_capture = pygame.mixer.Sound(capture_path)
            
            notify_path = os.path.join(sounds_path, "notify.mp3")
            if os.path.exists(notify_path):
                self.sound_notify = pygame.mixer.Sound(notify_path)
        except Exception as e:
            print(f"Warning: Could not load sounds: {e}")
    
    def _create_highlight_surfaces(self):
        """Create semi-transparent surfaces for highlighting."""
        self.highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        self.highlight_surface.fill(COLOR_HIGHLIGHT)
        
        self.selected_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        self.selected_surface.fill(COLOR_SELECTED)
        
        self.last_move_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        self.last_move_surface.fill(COLOR_LAST_MOVE)
        
        self.check_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        self.check_surface.fill(COLOR_CHECK)
    
    def _create_ui(self):
        """Create UI elements."""
        button_font = pygame.font.Font(None, 20)
        
        # Button dimensions
        btn_width = 48
        btn_height = 28
        btn_spacing = 4
        btn_y = WINDOW_HEIGHT - 45
        
        # Calculate starting x to center buttons in panel
        total_width = btn_width * 4 + btn_spacing * 3
        start_x = BOARD_SIZE + (PANEL_WIDTH - total_width) // 2
        
        # Create buttons
        self.btn_undo_all = Button(
            start_x, btn_y, btn_width, btn_height, "<<", button_font
        )
        self.btn_undo = Button(
            start_x + btn_width + btn_spacing, btn_y, btn_width, btn_height, "<", button_font
        )
        self.btn_redo = Button(
            start_x + (btn_width + btn_spacing) * 2, btn_y, btn_width, btn_height, ">", button_font
        )
        self.btn_redo_all = Button(
            start_x + (btn_width + btn_spacing) * 3, btn_y, btn_width, btn_height, ">>", button_font
        )
        
        self.buttons = [self.btn_undo_all, self.btn_undo, self.btn_redo, self.btn_redo_all]
        
        # Create move history panel
        self.move_history_panel = MoveHistoryPanel(
            BOARD_SIZE, 0, PANEL_WIDTH, WINDOW_HEIGHT - 55
        )
    
    def _update_button_states(self):
        """Update button enabled states based on game state."""
        can_undo = self.board.can_undo()
        can_redo = self.board.can_redo()
        
        self.btn_undo_all.enabled = can_undo
        self.btn_undo.enabled = can_undo
        self.btn_redo.enabled = can_redo
        self.btn_redo_all.enabled = can_redo
    
    def _get_square_from_mouse(self, pos: tuple[int, int]) -> Optional[Position]:
        """Convert mouse position to board position."""
        x, y = pos
        
        # Check if within board bounds
        if not (BOARD_OFFSET_X <= x < BOARD_OFFSET_X + BOARD_SIZE and
                BOARD_OFFSET_Y <= y < BOARD_OFFSET_Y + BOARD_SIZE):
            return None
        
        col = (x - BOARD_OFFSET_X) // SQUARE_SIZE
        row = (y - BOARD_OFFSET_Y) // SQUARE_SIZE
        
        return Position(row, col)
    
    def _get_screen_pos(self, pos: Position) -> tuple[int, int]:
        """Convert board position to screen position."""
        x = BOARD_OFFSET_X + pos.col * SQUARE_SIZE
        y = BOARD_OFFSET_Y + pos.row * SQUARE_SIZE
        return (x, y)
    
    def handle_click(self, mouse_pos: tuple[int, int]):
        """Handle mouse click."""
        # Check if in promotion dialog
        if self.promoting_pawn_move:
            self._handle_promotion_click(mouse_pos)
            return
        
        # Check button clicks
        if self.btn_undo_all.is_clicked(mouse_pos):
            self._undo_all()
            return
        if self.btn_undo.is_clicked(mouse_pos):
            self._undo()
            return
        if self.btn_redo.is_clicked(mouse_pos):
            self._redo()
            return
        if self.btn_redo_all.is_clicked(mouse_pos):
            self._redo_all()
            return
        
        board_pos = self._get_square_from_mouse(mouse_pos)
        if board_pos is None:
            self.selected_piece = None
            self.valid_moves = []
            return
        
        clicked_piece = self.board.get_piece(board_pos)
        
        # If a piece is selected and clicked on valid move
        if self.selected_piece and board_pos in self.valid_moves:
            # Check if pawn promotion
            if (isinstance(self.selected_piece, Pawn) and 
                (board_pos.row == 0 or board_pos.row == 7)):
                self.promoting_pawn_move = (self.selected_piece.position, board_pos)
            else:
                self._make_move(self.selected_piece.position, board_pos)
            
            self.selected_piece = None
            self.valid_moves = []
        
        # If clicking on own piece, select it
        elif clicked_piece and clicked_piece.color == self.board.current_turn:
            self.selected_piece = clicked_piece
            self.valid_moves = clicked_piece.get_valid_moves(self.board)
        
        # Otherwise, deselect
        else:
            self.selected_piece = None
            self.valid_moves = []
    
    def _handle_promotion_click(self, mouse_pos: tuple[int, int]):
        """Handle click during pawn promotion."""
        if not self.promoting_pawn_move:
            return
        
        # Check which promotion piece was clicked
        center_x = BOARD_SIZE // 2
        center_y = WINDOW_HEIGHT // 2
        piece_size = SQUARE_SIZE
        total_width = piece_size * 4
        start_x = center_x - total_width // 2
        
        x, y = mouse_pos
        
        if center_y - piece_size // 2 <= y <= center_y + piece_size // 2:
            promotion_pieces = [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]
            for i, piece_type in enumerate(promotion_pieces):
                px = start_x + i * piece_size
                if px <= x <= px + piece_size:
                    start, end = self.promoting_pawn_move
                    self._make_move(start, end, piece_type)
                    self.promoting_pawn_move = None
                    return
    
    def _make_move(self, start: Position, end: Position, 
                   promotion_type: Optional[PieceType] = None):
        """Execute a move and play sounds."""
        piece = self.board.get_piece(start)
        captured = self.board.get_piece(end)
        is_en_passant = isinstance(piece, Pawn) and end == self.board.en_passant_target
        
        move = self.board.move_piece(start, end, promotion_type)
        
        if move:
            # Update piece image if promoted
            if move.promotion_type:
                promoted_piece = self.board.get_piece(end)
                if promoted_piece:
                    promoted_piece.image = self.piece_images.get(
                        (promoted_piece.color, promoted_piece.piece_type)
                    )
            
            self._play_move_sound(captured is not None or is_en_passant)
    
    def _play_move_sound(self, is_capture: bool = False):
        """Play appropriate sound for a move."""
        if self.board.game_over:
            if self.sound_notify:
                self.sound_notify.play()
        elif is_capture:
            if self.sound_capture:
                self.sound_capture.play()
        else:
            if self.sound_move:
                self.sound_move.play()
        
        # Play check sound
        if not self.board.game_over and self.board.is_in_check(self.board.current_turn):
            if self.sound_notify:
                self.sound_notify.play()
    
    def _undo(self):
        """Undo the last move."""
        move = self.board.undo_move()
        if move:
            self._assign_piece_images()
            self.selected_piece = None
            self.valid_moves = []
            if self.sound_move:
                self.sound_move.play()
    
    def _redo(self):
        """Redo a previously undone move."""
        move = self.board.redo_move()
        if move:
            self._assign_piece_images()
            self.selected_piece = None
            self.valid_moves = []
            if self.sound_move:
                self.sound_move.play()
    
    def _undo_all(self):
        """Undo all moves."""
        while self.board.can_undo():
            self.board.undo_move()
        self._assign_piece_images()
        self.selected_piece = None
        self.valid_moves = []
        if self.sound_move:
            self.sound_move.play()
    
    def _redo_all(self):
        """Redo all moves."""
        while self.board.can_redo():
            self.board.redo_move()
        self._assign_piece_images()
        self.selected_piece = None
        self.valid_moves = []
        if self.sound_move:
            self.sound_move.play()
    
    def _reset_game(self):
        """Reset the game to initial state."""
        self.board = Board()
        self.selected_piece = None
        self.valid_moves = []
        self.promoting_pawn_move = None
        self._assign_piece_images()
    
    def draw(self):
        """Draw the game."""
        self.screen.fill(COLOR_BG)
        
        # Draw board
        self.screen.blit(self.board_image, (BOARD_OFFSET_X, BOARD_OFFSET_Y))
        
        # Draw last move highlight
        if self.board.move_history:
            last_move = self.board.move_history[-1]
            self.screen.blit(self.last_move_surface, self._get_screen_pos(last_move.start))
            self.screen.blit(self.last_move_surface, self._get_screen_pos(last_move.end))
        
        # Draw selected piece highlight
        if self.selected_piece:
            self.screen.blit(self.selected_surface, 
                           self._get_screen_pos(self.selected_piece.position))
        
        # Draw valid moves
        for move_pos in self.valid_moves:
            self.screen.blit(self.highlight_surface, self._get_screen_pos(move_pos))
        
        # Draw check highlight
        if self.board.is_in_check(self.board.current_turn):
            king_pos = (self.board.white_king_pos if self.board.current_turn == Color.WHITE 
                       else self.board.black_king_pos)
            if king_pos:
                self.screen.blit(self.check_surface, self._get_screen_pos(king_pos))
        
        # Draw pieces
        for row in range(8):
            for col in range(8):
                piece = self.board.grid[row][col]
                if piece and piece.image:
                    screen_pos = self._get_screen_pos(Position(row, col))
                    # Center the piece in the square
                    offset_x = (SQUARE_SIZE - piece.image.get_width()) // 2
                    self.screen.blit(piece.image, 
                                    (screen_pos[0] + offset_x, screen_pos[1]))
        
        # Draw side panel
        self._draw_side_panel()
        
        # Draw promotion dialog
        if self.promoting_pawn_move:
            self._draw_promotion_dialog()
        
        # Draw game over message
        if self.board.game_over:
            self._draw_game_over()
        
        pygame.display.flip()
    
    def _draw_side_panel(self):
        """Draw the side panel with move history and controls."""
        # Draw panel background
        panel_rect = pygame.Rect(BOARD_SIZE, 0, PANEL_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, panel_rect)
        
        # Draw turn indicator at top of panel
        font = pygame.font.Font(None, 24)
        if self.board.game_over:
            if self.board.is_stalemate:
                turn_text = "Stalemate!"
            else:
                winner = "White" if self.board.winner == Color.WHITE else "Black"
                turn_text = f"{winner} wins!"
        else:
            turn_text = "White's turn" if self.board.current_turn == Color.WHITE else "Black's turn"
            if self.board.is_in_check(self.board.current_turn):
                turn_text += " - Check!"
        
        # Draw move history panel
        self.move_history_panel.draw(
            self.screen, 
            self.board.move_history, 
            self.board.get_current_move_index()
        )
        
        # Update and draw buttons
        self._update_button_states()
        for button in self.buttons:
            button.draw(self.screen)
        
        # Draw turn indicator below history
        text_surface = font.render(turn_text, True, COLOR_TEXT)
        text_rect = text_surface.get_rect(
            centerx=BOARD_SIZE + PANEL_WIDTH // 2,
            bottom=WINDOW_HEIGHT - 52
        )
        self.screen.blit(text_surface, text_rect)
    
    def _draw_promotion_dialog(self):
        """Draw the pawn promotion selection dialog."""
        # Draw semi-transparent overlay over board only
        overlay = pygame.Surface((BOARD_SIZE, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLOR_PROMOTION_BG)
        self.screen.blit(overlay, (0, 0))
        
        # Draw promotion pieces
        color = Color.WHITE if self.board.current_turn == Color.BLACK else Color.BLACK
        promotion_pieces = [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]
        
        center_x = BOARD_SIZE // 2
        center_y = WINDOW_HEIGHT // 2
        piece_size = SQUARE_SIZE
        total_width = piece_size * 4
        start_x = center_x - total_width // 2
        
        # Draw background for pieces
        bg_rect = pygame.Rect(start_x - 10, center_y - piece_size // 2 - 10,
                             total_width + 20, piece_size + 20)
        pygame.draw.rect(self.screen, (60, 60, 60), bg_rect, border_radius=5)
        
        for i, piece_type in enumerate(promotion_pieces):
            img = self.piece_images.get((color, piece_type))
            if img:
                x = start_x + i * piece_size + (piece_size - img.get_width()) // 2
                y = center_y - img.get_height() // 2
                self.screen.blit(img, (x, y))
    
    def _draw_game_over(self):
        """Draw game over message."""
        font = pygame.font.Font(None, 48)
        
        if self.board.is_stalemate:
            text = "Stalemate!"
        else:
            winner = "White" if self.board.winner == Color.WHITE else "Black"
            text = f"Checkmate! {winner} wins!"
        
        text_surface = font.render(text, True, COLOR_TEXT)
        text_rect = text_surface.get_rect(center=(BOARD_SIZE // 2, WINDOW_HEIGHT // 2))
        
        # Draw background
        bg_rect = text_rect.inflate(40, 20)
        pygame.draw.rect(self.screen, (0, 0, 0, 200), bg_rect, border_radius=5)
        
        self.screen.blit(text_surface, text_rect)
        
        # Draw restart hint
        hint_font = pygame.font.Font(None, 24)
        hint_text = hint_font.render("Press R to restart", True, COLOR_TEXT_DIM)
        hint_rect = hint_text.get_rect(center=(BOARD_SIZE // 2, WINDOW_HEIGHT // 2 + 35))
        self.screen.blit(hint_text, hint_rect)
    
    def run(self):
        """Main game loop."""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                    elif event.button == 4:  # Scroll up
                        self.move_history_panel.handle_scroll(1, len(self.board.move_history))
                    elif event.button == 5:  # Scroll down
                        self.move_history_panel.handle_scroll(-1, len(self.board.move_history))
                elif event.type == pygame.MOUSEMOTION:
                    for button in self.buttons:
                        button.handle_mouse_motion(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Reset game
                        self._reset_game()
                    elif event.key == pygame.K_z:
                        if event.mod & pygame.KMOD_CTRL:
                            if event.mod & pygame.KMOD_SHIFT:
                                self._undo_all()
                            else:
                                self._undo()
                    elif event.key == pygame.K_y:
                        if event.mod & pygame.KMOD_CTRL:
                            if event.mod & pygame.KMOD_SHIFT:
                                self._redo_all()
                            else:
                                self._redo()
                    elif event.key == pygame.K_LEFT:
                        self._undo()
                    elif event.key == pygame.K_RIGHT:
                        self._redo()
                    elif event.key == pygame.K_HOME:
                        self._undo_all()
                    elif event.key == pygame.K_END:
                        self._redo_all()
            
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
