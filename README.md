# My Python Chess Trainer

This is a chess trainer I built from scratch using Python and Pygame. I wanted to create a full-featured application to practice my skills, so it's more than just a game. You can play against a custom AI I wrote or switch to a Puzzle Mode to practice tactics.

### Features I Implemented:

*   **Play against an AI:** The engine uses a Minimax algorithm with alpha-beta pruning and an evaluation function that understands piece positions, not just material count.
*   **Puzzle Mode:** A dedicated mode with several tactical puzzles (mates, forks, etc.) to solve.
*   **Instant Move Feedback:** The trainer analyzes every move you make and tells you if it was a blunder, mistake, or good move.
*   **"Best Move" Hint:** If you make a mistake, the engine will highlight the best move you missed.
*   **Polished UI:** I added smooth piece animations, legal move highlighting, and a clean layout for captured pieces and the evaluation bar.

### How to Run it:

1.  Make sure you have Python 3 installed.
2.  Install the required libraries:
    ```bash
    pip install pygame python-chess
    ```
3.  Run the main script from your terminal:
    ```bash
    python main.py
    ```

### Code Structure:

I split the code into a few files to keep things organized:
*   `main.py` - Just starts the game.
*   `game.py` - Handles the main game loop, UI, and all user input.
*   `engine.py` - Contains all the AI logic and the puzzle data.
*   `constants.py` - Stores all the colors, fonts, and screen sizes.
