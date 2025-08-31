import chess
import random

# --- AI Logic ---
piece_score = {
    chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
    chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000
}
piece_position_scores = {
    chess.PAWN: [
        0,  0,  0,  0,  0,  0,  0,  0, 50, 50, 50, 50, 50, 50, 50, 50, 10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5, 0,  0,  0, 20, 20,  0,  0,  0, 5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5, 0,  0,  0,  0,  0,  0,  0,  0
    ],
    chess.KNIGHT: [
        -50,-40,-30,-30,-30,-30,-40,-50, -40,-20,  0,  0,  0,  0,-20,-40, -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30, -30,  0, 15, 20, 20, 15,  0,-30, -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40, -50,-40,-30,-30,-30,-30,-40,-50,
    ],
    chess.BISHOP: [
        -20,-10,-10,-10,-10,-10,-10,-20, -10,  0,  0,  0,  0,  0,  0,-10, -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10, -10,  0, 10, 10, 10, 10,  0,-10, -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10, -20,-10,-10,-10,-10,-10,-10,-20,
    ],
    chess.ROOK: [
         0,  0,  0,  0,  0,  0,  0,  0,  5, 10, 10, 10, 10, 10, 10,  5, -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5, -5,  0,  0,  0,  0,  0,  0, -5, -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,  0,  0,  0,  5,  5,  0,  0,  0
    ],
    chess.QUEEN: [
        -20,-10,-10, -5, -5,-10,-10,-20, -10,  0,  0,  0,  0,  0,  0,-10, -10,  0,  5,  5,  5,  5,  0,-10,
         -5,  0,  5,  5,  5,  5,  0, -5,  0,  0,  5,  5,  5,  5,  0, -5, -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10, -20,-10,-10, -5, -5,-10,-10,-20
    ],
    chess.KING: [
        # Mid-game
        [
            -30,-40,-40,-50,-50,-40,-40,-30, -30,-40,-40,-50,-50,-40,-40,-30, -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30, -20,-30,-30,-40,-40,-30,-30,-20, -10,-20,-20,-20,-20,-20,-20,-10,
             20, 20,  0,  0,  0,  0, 20, 20,  20, 30, 10,  0,  0, 10, 30, 20
        ],
        # End-game
        [
            -50,-40,-30,-20,-20,-30,-40,-50, -30,-20,-10,  0,  0,-10,-20,-30, -30,-10, 20, 30, 30, 20,-10,-30,
            -30,-10, 30, 40, 40, 30,-10,-30, -30,-10, 30, 40, 40, 30,-10,-30, -30,-10, 20, 30, 30, 20,-10,-30,
            -30,-30,  0,  0,  0,  0,-30,-30, -50,-30,-30,-30,-30,-30,-30,-50
        ]
    ]
}

opening_book = {
    "": ["e2e4", "d2d4", "g1f3"], "e2e4": ["e7e5", "c7c5"], "e2e4 e7e5": ["g1f3", "f1c4"],
    "g1f3": ["d7d5", "g8f6"], "d2d4": ["d7d5", "g8f6"],
}

PUZZLES = [
    {
        "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
        "solution": ["f3e5", "c6e5", "d1h5"], "goal": "Win a free pawn"
    },
    {
        "fen": "6k1/5ppp/8/8/8/8/8/R4K2 w - - 0 1",
        "solution": ["a1a8"], "goal": "White to move, Mate in 1"
    },
    {
        "fen": "2r3k1/p4p1p/1p2p1p1/8/3P4/4P3/q4PPP/2Q3K1 w - - 0 1",
        "solution": ["c1c8"], "goal": "White to move, Win a Rook"
    },
    { 
        "fen": "r3k2r/ppp1q1pp/2np4/2b1p3/2B1P1b1/2PP1N2/P1P2PP1/R1BQ1RK1 w kq - 0 1",
        "solution": ["c4f7", "e8f7", "f3g5"], "goal": "White to move, Win the Queen"
    },
    {
        "fen": "2rq1rk1/pp1b1ppp/2np1n2/1B2p3/4P3/2P1BN2/P1P2PPP/R2Q1RK1 w - - 4 11",
        "solution": ["b5c6", "d7c6", "e3a7"], "goal": "White to move, Win a pawn"
    }
]

def get_opening_move(board):
    move_history = " ".join([move.uci() for move in board.move_stack])
    if move_history in opening_book: return chess.Move.from_uci(random.choice(opening_book[move_history]))
    return None

def evaluate_board(board):
    if board.is_checkmate(): return -99999 if board.turn == chess.WHITE else 99999
    if board.is_stalemate() or board.is_insufficient_material(): return 0
    is_endgame = len(board.piece_map()) <= 7
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            material_value = piece_score.get(piece.piece_type, 0)
            king_table = piece_position_scores[chess.KING][1 if is_endgame else 0]
            pos_scores = king_table if piece.piece_type == chess.KING else piece_position_scores[piece.piece_type]
            pos_square = square if piece.color == chess.WHITE else chess.square_mirror(square)
            positional_value = pos_scores[pos_square]
            if piece.color == chess.WHITE: score += material_value + positional_value
            else: score -= (material_value + positional_value)
    return score

def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over(): return evaluate_board(board), None
    best_move, legal_moves = None, list(board.legal_moves)
    legal_moves.sort(key=lambda move: board.is_capture(move), reverse=True)
    if maximizing_player:
        max_eval = -float('inf')
        for move in legal_moves:
            board.push(move)
            evaluation, _ = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            if evaluation > max_eval: max_eval, best_move = evaluation, move
            alpha = max(alpha, evaluation)
            if beta <= alpha: break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            evaluation, _ = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            if evaluation < min_eval: min_eval, best_move = evaluation, move
            beta = min(beta, evaluation)
            if beta <= alpha: break
        return min_eval, best_move

def get_best_move_ai(board, depth=3):
    if len(board.move_stack) < 4:
        move = get_opening_move(board)
        if move and move in board.legal_moves: return move

    return minimax(board, depth, -float('inf'), float('inf'), board.turn == chess.WHITE)[1]
