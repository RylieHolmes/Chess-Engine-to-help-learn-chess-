import pygame
from constants import WIDTH, HEIGHT, SIDEBAR_WIDTH
from game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH + SIDEBAR_WIDTH, HEIGHT))
    pygame.display.set_caption("Upgraded Chess Trainer")
    
    game = Game(screen)
    game.run()

if __name__ == "__main__":
    main()