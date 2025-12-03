"""Game constants."""

# Window and board dimensions
BOARD_SIZE = 512
SQUARE_SIZE = BOARD_SIZE // 8
PANEL_WIDTH = 220
WINDOW_WIDTH = BOARD_SIZE + PANEL_WIDTH
WINDOW_HEIGHT = BOARD_SIZE
BOARD_OFFSET_X = 0
BOARD_OFFSET_Y = 0
FPS = 60

# Colors
COLOR_HIGHLIGHT = (186, 202, 68, 150)  # Yellow-green for valid moves
COLOR_SELECTED = (246, 246, 105, 180)  # Bright yellow for selected piece
COLOR_LAST_MOVE = (170, 162, 58, 100)  # Dim yellow for last move
COLOR_CHECK = (235, 97, 80, 180)  # Red for king in check
COLOR_BG = (49, 46, 43)  # Dark background
COLOR_PANEL_BG = (39, 37, 34)  # Slightly darker for panel
COLOR_TEXT = (255, 255, 255)
COLOR_TEXT_DIM = (180, 180, 180)
COLOR_PROMOTION_BG = (30, 30, 30, 230)
COLOR_BUTTON = (70, 68, 65)
COLOR_BUTTON_HOVER = (90, 88, 85)
COLOR_BUTTON_DISABLED = (50, 48, 45)
COLOR_MOVE_HIGHLIGHT = (80, 78, 75)
