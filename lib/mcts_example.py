# This is a very simple implementation of the UCT Monte Carlo Tree Search algorithm in Python 2.7.
# The function UCT(rootstate, itermax, verbose = False) is towards the bottom of the code.
# It aims to have the clearest and simplest possible code, and for the sake of clarity, the code
# is orders of magnitude less efficient than it could be made, particularly by using a 
# state.GetRandomMove() or state.DoRandomRollout() function.
# 
# Example GameState classes for Nim, OXO and Othello are included to give some idea of how you
# can write your own GameState use UCT in your 2-player game. Change the game to be played in 
# the UCTPlayGame() function at the bottom of the code.
# 
# Written by Peter Cowling, Ed Powley, Daniel Whitehouse (University of York, UK) September 2012.
# 
# Licence is granted to freely use and distribute for any sensible/legal purpose so long as this comment
# remains in any distributed code.
# 
# For more information about Monte Carlo Tree Search check out our web site at www.mcts.ai

from math import *
import random


class GameState:
    """ A state of the game, i.e. the game board. These are the only functions which are
        absolutely necessary to implement UCT in any 2-player complete information deterministic 
        zero-sum game, although they can be enhanced and made quicker, for example by using a 
        GetRandomMove() function to generate a random move during rollout.
        By convention the players are numbered 1 and 2.
    """

    def __copy__(self):
        """ Create a deep clone of this game state.
        """
        raise NotImplementedError

    def make_move(self, move):
        """ Update a state by carrying out the given move.
            Must update playerJustMoved.
        """
        raise NotImplementedError

    def get_moves(self):
        """ Get all possible moves from this state.
        """
        raise NotImplementedError

    def get_result(self, playerjm):
        """ Get the game result from the viewpoint of playerjm. 
        """
        raise NotImplementedError


class OXOState(GameState):
    """ A state of the game, i.e. the game board.
        Squares in the board are in this arrangement
        012
        345
        678
        where 0 = empty, 1 = player 1 (X), 2 = player 2 (O)
    """

    def __init__(self):
        self.playerJustMoved = 2  # At the root pretend the player just moved is p2 - p1 has the first move
        self.board = [0, 0, 0, 0, 0, 0, 0, 0, 0]  # 0 = empty, 1 = player 1, 2 = player 2

    def __copy__(self):
        """ Create a deep clone of this game state.
        """
        st = OXOState()
        st.playerJustMoved = self.playerJustMoved
        st.board = self.board[:]
        return st

    def make_move(self, move):
        """ Update a state by carrying out the given move.
            Must update playerToMove.
        """
        assert 0 <= move <= 8 and self.board[move] == 0
        self.playerJustMoved = 3 - self.playerJustMoved
        self.board[move] = self.playerJustMoved

    def get_moves(self):
        """ Get all possible moves from this state.
        """
        return [i for i in range(9) if self.board[i] == 0]

    def get_result(self, playerjm):
        """ Get the game result from the viewpoint of playerjm. 
        """
        for (x, y, z) in [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]:
            if self.board[x] == self.board[y] == self.board[z]:
                if self.board[x] == playerjm:
                    return 1.0
                else:
                    return 0.0

        if not self.get_moves():
            return 0.5  # draw
        assert False  # Should not be possible to get here

    def __repr__(self):
        s = ""
        for i in range(9):
            s += ".XO"[self.board[i]]
            if i % 3 == 2:
                s += "\n"
        return s


# -----------------------------
# PLAYER_X = 1
# PLAYER_O = -1
# NO_PLAYER = 0
# STR_MATRIX = {
#     PLAYER_X: 'X',
#     PLAYER_O: 'O',
#     NO_PLAYER: '-'
# }
# ROWS = 3
# BOARD_SIZE = ROWS*ROWS
#
#
# class Board:
#     def __init__(self):
#         self.pos = [0] * BOARD_SIZE
#         self.playerJustMoved = PLAYER_O
#
#     def __str__(self):
#         lines = []
#         for combo in zip(*[self.pos[i::ROWS] for i in range(ROWS)]):
#             lines.extend(['{:<5}'.format(STR_MATRIX[elem]) for elem in combo])
#             lines.append('\n')
#         return ''.join(lines)
#
#     def __hash__(self):
#         """Hashing function to turn a tttoe position to a single signed integer
#         SUM (3^i)*Vi -> where i is index and Vi is value at index.
#         We are using 3 to the power of index since total number of values to be hashed are 3
#         (0 - empty, 1- player X, -1 - player O)
#         """
#         return sum([(3**i) * self.pos[i] for i in range(BOARD_SIZE)])
#
#     def __copy__(self):
#         _b = Board()
#         _b.pos = self.pos.copy()
#         _b.playerJustMoved = self.playerJustMoved
#         return _b
#
#     def clear(self):
#         self.pos = [0] * BOARD_SIZE
#
#     def make_move(self, move):
#         assert move in self.get_moves(), 'Position is already occupied'
#
#         self.playerJustMoved = -self.playerJustMoved  # change side to move
#         self.pos[move] = self.playerJustMoved
#         # print(self)
#         return self.get_winner(self.pos)
#
#     @classmethod
#     def take_move(cls, move, board):
#         board.pos[move] = NO_PLAYER
#         board.playerJustMoved = -board.playerJustMoved  # change side to move
#
#     def get_moves(self):
#         return [idx for idx, value in enumerate(self.pos) if value == NO_PLAYER]
#
#     @staticmethod
#     def get_winner(pos):
#         cols_combo = [pos[i::ROWS] for i in range(ROWS)]
#         rows_combo = list(zip(*cols_combo))
#         # print(cols_combo)
#         # print(row s_combo)
#
#         for i in range(ROWS):
#             # Sum a row and a column
#             row_result, col_result = sum(rows_combo[i]), sum(cols_combo[i])
#
#             # Check if sum of values of a row is not equal to number of rows i.e. all 1s or all -1s
#             if abs(row_result) == ROWS:
#                 return int(row_result / ROWS)
#
#             if abs(col_result) == ROWS:
#                 return int(col_result / ROWS)
#
#         # Sum values on Right diagonal
#         # Look at right Diagonal
#         # exclude last element since it is not part of the diagonal
#         # i.e. if you have [1, 2, 3,
#         #                   4, 5, 6,
#         #                   7 ,8 ,9] then right diagonal is [3, 5, 7]
#         # i.e. starting from the right corner the diagonal is formed by every second number
#         # (3, 5, 7), however this will also result in 9 being included which it should not be
#         # therefore we remove it
#         result = sum(pos[ROWS - 1::ROWS - 1][:-1])
#         if abs(result) == ROWS:
#             return int(result / ROWS)
#
#         # Left diagonal
#         result = sum(pos[::ROWS + 1])
#         if abs(result) == ROWS:
#             return int(result / ROWS)
#
#         # Lastly check if no available squares are on the board => TIE
#         if sum([abs(elem) for elem in pos]) == BOARD_SIZE:
#             return NO_PLAYER
#
#     def get_result(self, playerjm):
#         """ Get the game result from the viewpoint of playerjm.
#         """
#         for (x, y, z) in [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]:
#             if self.pos[x] == self.pos[y] == self.pos[z]:
#                 if self.pos[x] == playerjm:
#                     return 1.0
#                 else:
#                     return 0.0
#
#         if not self.get_moves():
#             return 0.5  # draw
#         assert False  # Should not be possible to get here

# -----------------------------


class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
        Crashes if state not specified.
    """

    def __init__(self, move=None, parent=None, state=None):
        self.move = move  # the move that got us to this node - "None" for the root node
        self.parentNode = parent  # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.untriedMoves = state.get_moves()  # future child nodes
        self.playerJustMoved = state.playerJustMoved  # the only part of the state that the Node needs later

    def uct_select_child(self):
        """ Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
            exploration versus exploitation.
        """
        s = sorted(self.childNodes, key=lambda c: c.wins / c.visits + sqrt(2 * log(self.visits) / c.visits))[-1]
        return s

    def add_child(self, m, s):
        """ Remove m from untriedMoves and add a new child node for this move.
            Return the added child node
        """
        n = Node(move=m, parent=self, state=s)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n

    def update(self, result):
        """ Update this node - one additional visit and result additional wins. result must be from
            the viewpoint of playerJustmoved.
        """
        self.visits += 1
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(
            self.untriedMoves) + "]"

    def convert_tree_to_string(self, indent):
        s = self.get_indent_string(indent) + str(self)
        for c in self.childNodes:
            s += c.convert_tree_to_string(indent + 1)
        return s

    @staticmethod
    def get_indent_string(indent):
        s = "\n"
        for i in range(1, indent + 1):
            s += "| "
        return s

    def convert_children_to_string(self):
        s = ""
        for c in self.childNodes:
            s += str(c) + "\n"
        return s


def uct(rootstate, itermax, verbose=False):
    """ Conduct a UCT search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
        Assumes 2 alternating players (player 1 starts), with game results in the range [0.0, 1.0]."""

    rootnode = Node(state=rootstate)

    for i in range(itermax):
        node = rootnode
        state = rootstate.__copy__()

        # Select
        while node.untriedMoves == [] and node.childNodes != []:  # node is fully expanded and non-terminal
            node = node.uct_select_child()
            state.make_move(node.move)

        # Expand
        if node.untriedMoves:  # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(node.untriedMoves)
            state.make_move(m)
            node = node.add_child(m, state)  # add child and descend tree

        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        while state.get_result(state.side) is None:  # while state is non-terminal
            state.make_move(random.choice(state.get_moves()))

        # Backpropagate
        while node is not None:  # backpropagate from the expanded node and work back to the root node
            node.update(state.get_result(
                node.playerJustMoved))  # state is terminal. Update node with result from POV of node.playerJustMoved
            node = node.parentNode

    # Output some information about the tree - can be omitted
    if verbose:
        print(rootnode.convert_tree_to_string(0))
    else:
        print(rootnode.convert_children_to_string())

    return sorted(rootnode.childNodes, key=lambda c: c.visits)[-1].move  # return the move that was most visited


def uct_play_game():
    """ Play a sample game between two UCT players where each player gets a different number 
        of UCT iterations (= simulations = tree nodes).
    """
    # state = OXOState()  # uncomment to play OXO
    from lib.board import Board
    from lib.constants import WHITE
    state = Board()
    mate_in_2 = '3k4/Q7/8/3K4/8/8/8/8 w --'
    state.parse_fen(mate_in_2)

    while state.get_moves():
        print(state)
        # if state.playerJustMoved == WHITE:
        #     m = uct(rootstate=state, itermax=20000, verbose=False)  # play with values for itermax and verbose = True
        # else:
        #     # m = uct(rootstate=state, itermax=100, verbose=False)
        #     m = int(input('Enter move:'))
        m = uct(rootstate=state, itermax=20000, verbose=False)  # play with values for itermax and verbose = True
        print("Best Move: " + str(m) + "\n")
        state.make_move(m)
    if state.get_result(state.playerJustMoved) == 1.0:
        print("Player " + str(state.playerJustMoved) + " wins!")
    elif state.get_result(state.playerJustMoved) == 0.0:
        print("Player " + str(3 - state.playerJustMoved) + " wins!")
    else:
        print("Nobody wins!")


if __name__ == "__main__":
    """ Play a single game to the end using UCT for both players. 
    """
    uct_play_game()
