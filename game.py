import pygame
import chess
import os
import sys
from collections import Counter
from constants import *
from engine import PUZZLES, get_best_move_ai, evaluate_board

# --- Asset Loading ---
def load_piece_images():
    pieces = {}
    for filename in os.listdir('pieces'):
        if filename.endswith('.png'):
            piece_name = filename.strip('.png')
            image = pygame.image.load(os.path.join('pieces', filename)).convert_alpha()
            pieces[piece_name] = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
    piece_map = {'P': pieces.get('wP'), 'R': pieces.get('wR'), 'N': pieces.get('wN'), 'B': pieces.get('wB'), 'K': pieces.get('wK'), 'Q': pieces.get('wQ'), 'p': pieces.get('bP'), 'r': pieces.get('bR'), 'n': pieces.get('bN'), 'b': pieces.get('bB'), 'k': pieces.get('bK'), 'q': pieces.get('bQ')}
    return piece_map

# --- Game Class ---
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.board = chess.Board()
        self.piece_images = load_piece_images()
        self.mode = "play"
        self.game_over = False
        self.game_over_message = ""
        self.move_feedback = ""
        self.show_best_move = None
        
        # UI State
        self.selected_square = None
        self.player_clicks = []
        self.legal_moves_for_selected = []
        self.last_move = None
        
        # Animation State
        self.animating = False
        self.is_return_anim = False
        self.anim_piece, self.anim_start_pos, self.anim_end_pos = None, None, None
        self.anim_progress = 0
        
        # Puzzle State
        self.puzzle_num = 0
        self.puzzle_step = 0
        self.puzzle_solved = False
        
        # UI Elements
        self.play_mode_button = pygame.Rect(BOARD_SIZE + 20, 20, 100, 40)
        self.puzzle_mode_button = pygame.Rect(BOARD_SIZE + 120, 20, 100, 40)
        self.new_game_button = pygame.Rect(BOARD_SIZE + 20, 150, 200, 50)
        self.take_back_button = pygame.Rect(BOARD_SIZE + 20, 220, 200, 50)
        self.next_puzzle_button = pygame.Rect(BOARD_SIZE + 20, 150, 200, 50)
        self.restart_puzzle_button = pygame.Rect(BOARD_SIZE + 20, 220, 200, 50)
        self.solution_button = pygame.Rect(BOARD_SIZE + 20, 290, 200, 50)

        if self.piece_images is None: sys.exit()

    def reset_game(self):
        self.board = chess.Board()
        self.game_over, self.move_feedback, self.last_move, self.show_best_move = False, "", None, None
        self.clear_selection()
    
    def load_puzzle(self):
        self.board = chess.Board(PUZZLES[self.puzzle_num]["fen"])
        self.puzzle_step, self.puzzle_solved, self.last_move, self.move_feedback = 0, False, None, ""
        self.clear_selection()
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if not self.animating and event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            
            if self.mode == "play" and self.board.turn == chess.BLACK and not self.game_over and not self.animating:
                self.make_ai_move()

            self.update()
            clock.tick(60)
        pygame.quit()

    def start_animation(self, move, is_return=False):
        self.is_return_anim = is_return
        self.animating = True
        self.anim_piece = self.board.piece_at(move.from_square) if not is_return else self.last_move_piece
        self.anim_start_pos = (chess.square_file(move.from_square) * SQUARE_SIZE, (7 - chess.square_rank(move.from_square)) * SQUARE_SIZE)
        self.anim_end_pos = (chess.square_file(move.to_square) * SQUARE_SIZE, (7 - chess.square_rank(move.to_square)) * SQUARE_SIZE)
        self.anim_progress = 0

    def update(self):
        self.draw_all()
        if self.animating:
            self.anim_progress += 0.1
            if self.anim_progress >= 1:
                self.animating, self.is_return_anim = False, False
                self.anim_progress = 1
        if self.mode == "play" and not self.game_over and self.board.is_game_over():
            self.game_over = True
            self.game_over_message = f"Checkmate! {'Black' if self.board.turn == chess.WHITE else 'White'} wins." if self.board.is_checkmate() else "Game Over: Draw"
        pygame.display.flip()

    def make_move(self, move, is_player=False):
        if is_player: self.analyze_player_move(move)
        self.start_animation(move)
        self.last_move = move
        self.board.push(move)

    def handle_click(self, pos):
        if self.play_mode_button.collidepoint(pos): self.mode = "play"; self.reset_game(); return
        if self.puzzle_mode_button.collidepoint(pos): self.mode = "puzzle"; self.load_puzzle(); return
        if self.mode == "play":
            if self.new_game_button.collidepoint(pos): self.reset_game()
            elif self.take_back_button.collidepoint(pos): self.take_back()
        elif self.mode == "puzzle":
            if self.next_puzzle_button.collidepoint(pos): self.puzzle_num=(self.puzzle_num+1)%len(PUZZLES);self.load_puzzle()
            elif self.restart_puzzle_button.collidepoint(pos): self.load_puzzle()
            elif self.solution_button.collidepoint(pos): self.show_solution()
        
        if pos[0] <= BOARD_SIZE: self.handle_board_click(pos)

    def handle_board_click(self, pos):
        col, row = pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE
        square_clicked = chess.square(col, 7 - row)
        
        # If no piece is selected yet
        if not self.player_clicks:
            piece = self.board.piece_at(square_clicked)
            if piece and piece.color == self.board.turn:
                self.selected_square = square_clicked
                self.player_clicks.append(square_clicked)
                self.legal_moves_for_selected = [m.to_square for m in self.board.legal_moves if m.from_square == square_clicked]
        
        # If a piece is already selected
        else:
            from_sq = self.player_clicks[0]
            
            # Case 1: User clicked the same piece again to de-select it
            if from_sq == square_clicked:
                self.clear_selection()
                return

            # Case 2: User clicked another one of their own pieces to switch selection
            new_piece = self.board.piece_at(square_clicked)
            if new_piece and new_piece.color == self.board.turn:
                self.clear_selection()
                self.selected_square = square_clicked
                self.player_clicks.append(square_clicked)
                self.legal_moves_for_selected = [m.to_square for m in self.board.legal_moves if m.from_square == square_clicked]
                return

            # Case 3: User clicked a destination square for a move
            move_uci = chess.square_name(from_sq) + chess.square_name(square_clicked)
            piece_to_move = self.board.piece_at(from_sq)
            if piece_to_move.piece_type == chess.PAWN and (row == 0 or row == 7):
                move_uci += 'q'
            
            self.clear_selection()

            if self.mode == "play":
                move = chess.Move.from_uci(move_uci)
                if move in self.board.legal_moves:
                    self.make_move(move, is_player=True)
            elif self.mode == "puzzle" and not self.puzzle_solved:
                self.check_puzzle_move(move_uci)

    def clear_selection(self):
        self.selected_square, self.player_clicks, self.legal_moves_for_selected = None, [], []

    def check_puzzle_move(self, move_uci):
        solution_move_uci = PUZZLES[self.puzzle_num]["solution"][self.puzzle_step]
        if move_uci == solution_move_uci:
            move = chess.Move.from_uci(move_uci)
            self.start_animation(move)
            self.board.push(move)
            self.last_move = move
            self.puzzle_step += 1
            if self.puzzle_step >= len(PUZZLES[self.puzzle_num]["solution"]):
                self.puzzle_solved = True
            else: # Auto-play the next move in the solution
                pygame.time.wait(300)
                next_move = chess.Move.from_uci(PUZZLES[self.puzzle_num]["solution"][self.puzzle_step])
                self.start_animation(next_move)
                self.board.push(next_move)
                self.last_move = self.board.peek()
                self.puzzle_step += 1
                if self.puzzle_step >= len(PUZZLES[self.puzzle_num]["solution"]):
                    self.puzzle_solved = True
        else:
            self.move_feedback = "Incorrect!"
            # Animate the piece back
            self.last_move_piece = self.board.piece_at(chess.Move.from_uci(move_uci).from_square)
            self.start_animation(chess.Move.from_uci(move_uci[2:4]+move_uci[0:2]), is_return=True)

    def analyze_player_move(self, move):
        eval_before = evaluate_board(self.board)
        self.board.push(move)
        eval_after = -evaluate_board(self.board)
        self.board.pop()
        eval_change = eval_after - eval_before
        
        if eval_change < -75:
            self.show_best_move = get_best_move_ai(self.board, depth=3)
        else:
            self.show_best_move = None

        if eval_change < -300: self.move_feedback = "Blunder!"
        elif eval_change < -150: self.move_feedback = "Mistake."
        elif eval_change < -75: self.move_feedback = "Inaccuracy."
        else: self.move_feedback = "Good Move."

    def make_ai_move(self):
        ai_move = get_best_move_ai(self.board, depth=3)
        if ai_move: self.make_move(ai_move)

    def take_back(self):
        if len(self.board.move_stack) >= 2:
            self.board.pop(); self.board.pop()
            self.game_over, self.move_feedback, self.last_move, self.show_best_move = False, "", None, None
            self.clear_selection()

    def show_solution(self):
        self.load_puzzle()
        for move_uci in PUZZLES[self.puzzle_num]["solution"]:
            self.board.push_uci(move_uci)
        self.last_move = self.board.peek(); self.puzzle_solved = True

    def draw_all(self):
        self.screen.fill(SIDEBAR_BG)
        self.draw_board_and_pieces()
        self.draw_sidebar()
        if self.game_over: self.draw_game_over()
        
    def draw_board_and_pieces(self):
        for row in range(8):
            for col in range(8):
                color = WHITE_SQUARE if (row + col) % 2 == 0 else GREEN_SQUARE
                pygame.draw.rect(self.screen, color, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        if self.last_move:
            self.highlight_square(self.last_move.from_square, LAST_MOVE_COLOR); self.highlight_square(self.last_move.to_square, LAST_MOVE_COLOR)
        if self.show_best_move:
            self.highlight_square(self.show_best_move.from_square, BEST_MOVE_COLOR); self.highlight_square(self.show_best_move.to_square, BEST_MOVE_COLOR)
        
        for square in self.legal_moves_for_selected:
            x = chess.square_file(square) * SQUARE_SIZE + SQUARE_SIZE // 2
            y = (7 - chess.square_rank(square)) * SQUARE_SIZE + SQUARE_SIZE // 2
            pygame.draw.circle(self.screen, LEGAL_MOVE_COLOR, (x, y), 15)
            
        for sq in chess.SQUARES:
            pc = self.board.piece_at(sq)
            is_anim_piece = self.animating and sq == chess.square(int(self.anim_start_pos[0]/SQUARE_SIZE), 7-int(self.anim_start_pos[1]/SQUARE_SIZE))
            if pc and not (is_anim_piece and not self.is_return_anim):
                self.screen.blit(self.piece_images[pc.symbol()], (chess.square_file(sq)*SQUARE_SIZE, (7-chess.square_rank(sq))*SQUARE_SIZE))
        
        if self.animating:
            start_pos, end_pos = (self.anim_start_pos, self.anim_end_pos) if not self.is_return_anim else (self.anim_end_pos, self.anim_start_pos)
            x = start_pos[0] * (1-self.anim_progress) + end_pos[0] * self.anim_progress
            y = start_pos[1] * (1-self.anim_progress) + end_pos[1] * self.anim_progress
            self.screen.blit(self.piece_images[self.anim_piece.symbol()], (x, y))

    def highlight_square(self, square, color):
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        s.fill(color)
        self.screen.blit(s, (chess.square_file(square) * SQUARE_SIZE, (7-chess.square_rank(square)) * SQUARE_SIZE))

    def draw_sidebar(self):
        self.draw_button(self.play_mode_button, "Play AI", self.mode == "play")
        self.draw_button(self.puzzle_mode_button, "Puzzles", self.mode == "puzzle")
        if self.mode == "play": self.draw_play_mode_sidebar()
        else: self.draw_puzzle_mode_sidebar()

    def draw_play_mode_sidebar(self):
        if self.board.turn == chess.WHITE and self.move_feedback:
            feedback_text = FONT_MEDIUM.render(self.move_feedback, True, TEXT_COLOR)
            self.screen.blit(feedback_text, feedback_text.get_rect(center=(BOARD_SIZE + SIDEBAR_WIDTH // 2, 105)))
            if self.show_best_move:
                best_move_text = FONT_SMALL.render(f"Best was: {self.show_best_move.uci()}", True, BEST_MOVE_COLOR)
                self.screen.blit(best_move_text, best_move_text.get_rect(center=(BOARD_SIZE + SIDEBAR_WIDTH // 2, 130)))
        else:
            turn_text = FONT_MEDIUM.render("Black's Turn", True, TEXT_COLOR)
            self.screen.blit(turn_text, turn_text.get_rect(center=(BOARD_SIZE + SIDEBAR_WIDTH // 2, 105)))
        
        self.draw_button(self.new_game_button, "New Game")
        self.draw_button(self.take_back_button, "Take Back")
        self.draw_captured_pieces()
        self.draw_eval_bar()

    def draw_puzzle_mode_sidebar(self):
        goal_text = FONT_MEDIUM.render(PUZZLES[self.puzzle_num]["goal"], True, TEXT_COLOR)
        self.screen.blit(goal_text, goal_text.get_rect(center=(BOARD_SIZE + SIDEBAR_WIDTH // 2, 105)))
        self.draw_button(self.next_puzzle_button, "Next Puzzle")
        self.draw_button(self.restart_puzzle_button, "Restart Puzzle")
        self.draw_button(self.solution_button, "Show Solution")
        if self.puzzle_solved or self.move_feedback == "Incorrect!":
            feedback = "Correct!" if self.puzzle_solved else self.move_feedback
            color = SUCCESS_COLOR if self.puzzle_solved else (255, 69, 0) # Reddish-orange for incorrect
            self.draw_feedback_overlay(feedback, color)
            if not self.puzzle_solved: self.move_feedback = "" # Reset after showing

    def draw_button(self, rect, text, is_active=False):
        mouse_pos = pygame.mouse.get_pos()
        color = BUTTON_HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR
        if is_active: color = GREEN_SQUARE
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        text_surf = FONT_MEDIUM.render(text, True, TEXT_COLOR)
        self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))
       
    def draw_eval_bar(self):
        score = evaluate_board(self.board)
        clamped_score = max(min(score, 1000), -1000)
        normalized_score = (clamped_score + 1000) / 2000
        
        bar_height = 200
        bar_margin_bottom = 20
        bar_y_start = HEIGHT - bar_height - bar_margin_bottom
        
        bar_rect = pygame.Rect(BOARD_SIZE + 70, bar_y_start, 100, bar_height)
        
        white_height = bar_height * normalized_score
        black_height = bar_height - white_height
        
        white_rect = pygame.Rect(bar_rect.x, bar_rect.y + black_height, bar_rect.width, white_height)
        black_rect = pygame.Rect(bar_rect.x, bar_rect.y, bar_rect.width, black_height)
        
        pygame.draw.rect(self.screen, (220,220,220), white_rect)
        pygame.draw.rect(self.screen, (70,70,70), black_rect)
        pygame.draw.rect(self.screen, TEXT_COLOR, bar_rect, 2, border_radius=5)

    def draw_captured_pieces(self):
        STARTING_PIECES = {'P':8,'R':2,'N':2,'B':2,'Q':1,'p':8,'r':2,'n':2,'b':2,'q':1}
        board_counts = Counter(p.symbol() for p in self.board.piece_map().values())
        captured_by_white, captured_by_black = [], []
        for symbol, start_count in STARTING_PIECES.items():
            captured_count = start_count - board_counts[symbol]
            if captured_count > 0:
                for _ in range(captured_count): (captured_by_white if symbol.islower() else captured_by_black).append(symbol)
        piece_order = 'qrbnp'; captured_by_white.sort(key=lambda s:piece_order.find(s.lower())); captured_by_black.sort(key=lambda s:piece_order.find(s.lower()))
        y_offset = 290
        self.screen.blit(FONT_SMALL.render("Captured by Black:", True, TEXT_COLOR), (BOARD_SIZE + 20, y_offset))
        for i, symbol in enumerate(captured_by_black):
            img = pygame.transform.scale(self.piece_images[symbol], (30,30))
            self.screen.blit(img, (BOARD_SIZE + 20 + i*32, y_offset + 25))
        self.screen.blit(FONT_SMALL.render("Captured by White:", True, TEXT_COLOR), (BOARD_SIZE + 20, y_offset + 70))
        for i, symbol in enumerate(captured_by_white):
            img = pygame.transform.scale(self.piece_images[symbol], (30,30))
            self.screen.blit(img, (BOARD_SIZE + 20 + i*32, y_offset + 95))

    def draw_game_over(self):
        overlay = pygame.Surface((BOARD_SIZE, HEIGHT), pygame.SRCALPHA)
        overlay.fill((40, 40, 40, 180))
        self.screen.blit(overlay, (0, 0))
        text_surf = FONT_LARGE.render(self.game_over_message, True, (255, 255, 255))
        self.screen.blit(text_surf, text_surf.get_rect(center=(BOARD_SIZE / 2, HEIGHT / 2)))

    def draw_feedback_overlay(self, text, color):
        overlay = pygame.Surface((BOARD_SIZE, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        text_surf = FONT_LARGE.render(text, True, color)
        text_rect = text_surf.get_rect(center=(BOARD_SIZE / 2, HEIGHT / 2))
        self.screen.blit(overlay, (0,0))
        self.screen.blit(text_surf, text_rect)