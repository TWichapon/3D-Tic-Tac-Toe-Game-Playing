#BUG FIXED

import math
import copy
import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 600
CELL_SIZE = WIDTH // 3
FONT_SIZE = 40

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Fonts
FONT = pygame.font.Font(None, FONT_SIZE)
selected_piece = None
winner = None

# Game initialization
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Big Eats Small Tic Tac Toe")
clock = pygame.time.Clock()


# Create an empty board
def create_board():
    return [[None for _ in range(3)] for _ in range(3)]


# Draw the game board
def draw_board(board, selected_piece, winner):
    screen.fill(WHITE)

    # Draw grid
    for x in range(1, 3):
        pygame.draw.line(screen, BLACK, (x * CELL_SIZE, 0), (x * CELL_SIZE, HEIGHT), 3)
        pygame.draw.line(screen, BLACK, (0, x * CELL_SIZE), (WIDTH, x * CELL_SIZE), 3)

    # Draw pieces
    for row in range(3):
        for col in range(3):
            cell = board[row][col]
            if cell:
                player, size = cell
                color = RED if player == 'X' else BLUE
                text = FONT.render(f"{player} {size}", True, color)
                text_rect = text.get_rect(center=((col + 0.5) * CELL_SIZE, (row + 0.5) * CELL_SIZE))
                screen.blit(text, text_rect)

    # Draw piece selection
    if winner is None or winner is False:
        pygame.draw.rect(screen, GRAY, (0, WIDTH, WIDTH, HEIGHT - WIDTH))
        text = FONT.render("Choose a piece: S | M | L", True, BLACK)
        screen.blit(text, (10, WIDTH + 10))

        # Highlight selected piece
        if selected_piece is not None:
            highlight_text = FONT.render(f"Selected: {selected_piece}", True, BLACK)
            screen.blit(highlight_text, (10, WIDTH + 50))
    else:
        # Display winner message
        message = f"Winner: {winner}" if winner != "Tie" else "It's a Tie!"
        winner_text = FONT.render(message, True, BLACK)
        screen.blit(winner_text, (WIDTH // 4, HEIGHT // 2))


# Check for a winner
def check_winner(board, player):
    for i in range(3):
        if all(cell and cell[0] == player for cell in board[i]):  # Row
            return True
        if all(cell and cell[0] == player for cell in [board[j][i] for j in range(3)]):  # Column
            return True
    if all(cell and cell[0] == player for cell in [board[i][i] for i in range(3)]):  # Main diagonal
        return True
    if all(cell and cell[0] == player for cell in [board[i][2 - i] for i in range(3)]):  # Anti-diagonal
        return True
    return False


# Check if the game is a draw
def is_draw(board, pieces):
    # Check if there are any empty cells
    for row in range(3):
        for col in range(3):
            if board[row][col] is None:
                return False

    # Check if any player has remaining valid moves
    for player in ['X', 'O']:
        for row in range(3):
            for col in range(3):
                for size in ['S', 'M', 'L']:
                    if can_place(board, row, col, player, size, pieces[player]):
                        return False

    # If no empty cells and no valid moves, it's a draw
    return True


# Heuristic evaluation function
def evaluate_board(board, player):
    opponent = 'X' if player == 'O' else 'O'
    score = 0

    def line_score(line):
        nonlocal score
        player_count = sum(1 for cell in line if cell and cell[0] == player)
        opponent_count = sum(1 for cell in line if cell and cell[0] == opponent)
        piece_values = sum(piece_size(cell[1]) for cell in line if cell and cell[0] == player)
        if opponent_count == 0:
            score += piece_values + player_count
        elif player_count == 0:
            score -= piece_values + opponent_count

    # Evaluate rows, columns, and diagonals
    for i in range(3):
        line_score(board[i])  # Rows
        line_score([board[j][i] for j in range(3)])  # Columns
    line_score([board[i][i] for i in range(3)])  # Main diagonal
    line_score([board[i][2 - i] for i in range(3)])  # Anti-diagonal

    return score


# Minimax algorithm with depth limit and heuristic
def minimax(board, depth, is_maximizing, alpha, beta, pieces, player):
    if check_winner(board, 'O'):
        return 10000 - depth
    if check_winner(board, 'X'):
        return -10000 + depth
    if is_draw(board, pieces) or depth >= 5:
        return evaluate_board(board, player)

    if is_maximizing: # Max Value
        max_eval = -math.inf
        for row in range(3):
            for col in range(3):
                for piece in ['S', 'M', 'L']:
                    if can_place(board, row, col, 'O', piece, pieces['O']):
                        previous_state = place_piece(board, row, col, 'O', piece)
                        eval = minimax(board, depth + 1, False, alpha, beta, pieces, player)
                        remove_piece(board, row, col, previous_state)
                        max_eval = max(max_eval, eval)
                        alpha = max(alpha, eval)
                        if beta <= alpha:
                            break
        return max_eval
    else: # Min Value
        min_eval = math.inf
        for row in range(3):
            for col in range(3):
                for piece in ['S', 'M', 'L']:
                    if can_place(board, row, col, 'X', piece, pieces['X']):
                        previous_state = place_piece(board, row, col, 'X', piece)
                        eval = minimax(board, depth + 1, True, alpha, beta, pieces, player)
                        remove_piece(board, row, col, previous_state)
                        min_eval = min(min_eval, eval)
                        beta = min(beta, eval)
                        if beta <= alpha:
                            break
        return min_eval


# Check if a piece can be placed
def can_place(board, row, col, player, piece, available_pieces):
    if available_pieces[piece] == 0:
        return False
    if board[row][col] is None:
        return True
    if piece_size(board[row][col][1]) < piece_size(piece):
        return True
    return False


# Get the size of a piece
def place_piece(board, row, col, player, piece):
    previous_state = board[row][col]
    board[row][col] = (player, piece)
    return previous_state


# Remove a piece from the board
def remove_piece(board, row, col, previous_state):
    board[row][col] = previous_state


# Get the size of a piece
def piece_size(piece):
    sizes = {'S': 1, 'M': 2, 'L': 3}
    return sizes[piece]


# Find the best move for the AI
def find_best_move(original_board, pieces, is_first_move, player='O'):
    board = copy.deepcopy(original_board)  # Create a snapshot of the board
    if is_first_move:
        # Prioritize placing "OL" in the center if it's empty
        if can_place(board, 1, 1, 'O', 'L', pieces['O']):
            return 1, 1, 'L'
        # Otherwise, place "OL" in the top-left corner
        elif can_place(board, 0, 0, 'O', 'L', pieces['O']):
            return 0, 0, 'L'

    best_score = -math.inf
    move = None
    for row in range(3):
        for col in range(3):
            for piece in ['S', 'M', 'L']:
                if can_place(board, row, col, player, piece, pieces[player]):
                    board[row][col] = (player, piece)
                    score = minimax(board, 0, False, -math.inf, math.inf, pieces, player)
                    board[row][col] = None
                    if score > best_score:
                        best_score = score
                        move = (row, col, piece)
    return move


def main():
    board = create_board()
    pieces = {'X': {'S': 3, 'M': 3, 'L': 3}, 'O': {'S': 3, 'M': 3, 'L': 3}}
    running = True
    turn = 'X'
    selected_piece = None
    winner = None
    is_first_move = True

    while running:
        draw_board(board, selected_piece, winner)
        pygame.display.flip()

        if is_draw(board, pieces):
            winner = "Tie"
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            continue

        if winner:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            continue

        if turn == 'X':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        selected_piece = 'S'
                    elif event.key == pygame.K_m:
                        selected_piece = 'M'
                    elif event.key == pygame.K_l:
                        selected_piece = 'L'

                if event.type == pygame.MOUSEBUTTONDOWN and selected_piece:
                    x, y = pygame.mouse.get_pos()
                    col, row = x // CELL_SIZE, y // CELL_SIZE
                    if row < 3 and can_place(board, row, col, 'X', selected_piece, pieces['X']):
                        board[row][col] = ('X', selected_piece)
                        pieces['X'][selected_piece] -= 1
                        selected_piece = None
                        turn = 'O'
                        if check_winner(board, "X"):
                            winner = "Player"
            # board = handle_player_move(board, pieces, 'X')
            # turn = 'O'
        else:
            row, col, size = find_best_move(board, pieces, is_first_move)
            is_first_move = False
            board[row][col] = ('O', size)
            pieces['O'][size] -= 1
            turn = 'X'
            if check_winner(board, "O"):
                winner = "AI"

        # Check for events to quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()


# Run the game
if __name__ == "__main__":
    main()



