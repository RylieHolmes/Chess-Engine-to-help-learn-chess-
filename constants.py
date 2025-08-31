import pygame

# --- Screen dimensions ---
WIDTH, HEIGHT = 800, 640
SIDEBAR_WIDTH = 240
BOARD_SIZE = HEIGHT
SQUARE_SIZE = BOARD_SIZE // 8

# --- Colors ---
WHITE_SQUARE = (238, 238, 210)
GREEN_SQUARE = (118, 150, 86)
HIGHLIGHT_COLOR = (255, 255, 51, 128)
LAST_MOVE_COLOR = (170, 162, 58, 150)
LEGAL_MOVE_COLOR = (0, 0, 0, 40) # Subtle dark circles for legal moves
BEST_MOVE_COLOR = (0, 191, 255, 128) # Bright blue for the "best move" hint
SIDEBAR_BG = (40, 40, 40)
TEXT_COLOR = (230, 230, 230)
BUTTON_COLOR = (80, 80, 80)
BUTTON_HOVER_COLOR = (110, 110, 110)
SUCCESS_COLOR = (124, 252, 0)

# --- Fonts ---
pygame.font.init()
FONT_SMALL = pygame.font.SysFont('Arial', 18)
FONT_MEDIUM = pygame.font.SysFont('Arial', 24)
FONT_LARGE = pygame.font.SysFont('Arial', 32, bold=True)