4
# Initialize the game board
board = [" " for _ in range(9)] # Represents a 3x3 board

def print_board(board):
    """Prints the current state of the Tic-Tac-Toe board."""
    print(f"| {board[0]} | {board[1]} | {board[2]} |")
    print("-------------")
    print(f"| {board[3]} | {board[4]} | {board[5]} |")
    print("-------------")
    print(f"| {board[6]} | {board[7]} | {board[8]} |")

def player_move(player_symbol):
    """Gets a valid move from the current player."""
    while True:
        try:
            choice = int(input(f"Player {player_symbol}, enter your move (1-9): ")) - 1
            if 0 <= choice < 9 and board[choice] == " ":
                return choice
            else:
                print("Invalid move. That spot is already taken or out of range. Try again.")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 9.")

def check_win(board, player_symbol):
    """Checks if the current player has won."""
    # Check rows
    for i in range(0, 9, 3):
        if board[i] == board[i+1] == board[i+2] == player_symbol:
            return True
    # Check columns
    for i in range(3):
        if board[i] == board[i+3] == board[i+6] == player_symbol:
            return True
    # Check diagonals
    if board[0] == board[4] == board[8] == player_symbol:
        return True
    if board[2] == board[4] == board[6] == player_symbol:
        return True
    return False

def check_draw(board):
    """Checks if the game is a draw."""
    return " " not in board

def play_game():
    """Manages the main game loop."""
    current_player = "X"
    game_over = False

    print("Welcome to Tic-Tac-Toe!")
    print_board(board)

    while not game_over:
        move = player_move(current_player)
        board[move] = current_player
        print_board(board)

        if check_win(board, current_player):
            print(f"Player {current_player} wins!")
            game_over = True
        elif check_draw(board):
            print("It's a draw!")
            game_over = True
        else:
            current_player = "O" if current_player == "X" else "X"

if __name__ == "__main__":
    play_game()