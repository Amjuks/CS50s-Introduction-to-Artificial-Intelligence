"""
Tic Tac Toe Player
"""

import math, copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    # create a variable to keep track of empty boxes
    empty_boxes = 0

    # search through every row
    for row in board:

        # search through every column in the row
        for column in row:

            # increment number of empty boxes if they are empty
            empty_boxes += 1 if column is None else 0

    # return the players turn
    return X if empty_boxes % 2 != 0 else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    
    # initialize a set to store all possible actions
    actions_set = set()

    # look through the rows
    for i, row in enumerate(board):
        # look through the columns
        for j, col in enumerate(row):
            # add the position to the set if its empty
            if col is None:
                actions_set.add((i, j))

    # return the set
    return actions_set


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    # replace the x and y co-ordinates
    res = copy.deepcopy(board)
    res[action[0]][action[1]] = player(board)
    return res


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # check if there is a horizontal win
    for row in board:
        if len(set(row)) == 1 and None not in row:
            return row[0][0]
    
    # check if there is a vertical win
    for col in zip(*board):
        if len(set(col)) == 1 and None not in col:
            return col[0]

    # check if there is a diagonal win
    if (board[0][0] == board[1][1] == board[2][2]) or (board[0][2] == board[1][1] == board[2][0]):
        return board[1][1]
    
    # return None since there is no winner
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    # if there is a winner, the game ends
    if winner(board):
        return True

    # if the board isn't completed the game isn't over
    for row in board:
        if None in row:
            return False

    # the game ends if the board is completed
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    if terminal(board):
        # check for the winner
        value = winner(board)

        # return the value
        if value == X:
            return 1
        elif value == O:
            return -1
        else:
            return 0 


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    # return None if game is over
    if terminal(board):
        return None

    # return the best move for X
    if player(board) == X:
        return MAX_VALUE(board)[1]
    
    # return the best move for O
    return MIN_VALUE(board)[1]


def MAX_VALUE(state):

    # return the utility if the game is over
    if terminal(state):
        return utility(state), None

    # set a value to the lowest value possible in the game
    value = -2

    # go through all possible actions in the game
    for action in actions(state):
        MAX, play = MIN_VALUE(result(state, action))

        # alpha-beta pruning to optimise minimax
        if MAX < value:
            break

        # if the MAX value is greater than the current value, update value and move
        if MAX > value or move is None:
            value = MAX
            move = action

            # depth-limited minimax
            if value == 1:
                return value, move

    # return the value and move
    return value, move


def MIN_VALUE(state):

    # return the utility if the game is over
    if terminal(state):
        return utility(state), None

    # set a value to the highest value possible in the game
    value = 2

    # go through all possible actions in the game
    for action in actions(state):
        MIN, play = MAX_VALUE(result(state, action))

        # alpha-beta pruning
        if MIN > value:
            break

        # if the MIN value is lesser than the current value, update value and move
        if MIN < value or move is None:
            value = MIN
            move = action

            # depth-limited minimax
            if value == -1:
                return value, move

    # return the value and move
    return value, move