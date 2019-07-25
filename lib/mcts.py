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
import time
from math import *
import random
from multiprocessing import Queue, Process
from operator import itemgetter

from lib.board import Board


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


def uct_multi(rootstate: Board, itermax):
    moves = rootstate.get_moves()
    if len(moves) == 1:
        return moves[0]

    avg_iters = itermax // len(moves)
    queue = Queue()

    processes = []
    for move in moves:
        current_state = rootstate.__copy__()
        current_state.make_move(move)
        result = current_state.get_result(current_state.playerJustMoved ^ 1)
        if result is not None:
            print(f'Immediate result. Move: {rootstate.moveGenerator.print_move(move)}, score: {result}')
            queue.put((move, result, 1))
            continue  # here 1 referes to number of visits

        p = Process(target=uct, args=(queue, move, current_state, avg_iters))
        p.start()
        processes.append(p)

    for process in processes:
        process.join()
    # for move in moves:
    #     state = rootstate.__copy__()
    #     state.make_move(move)
    #     uct(queue, move, state, avg_iters, verbose)

    results = []
    while not queue.empty():
        move, wins, visits = queue.get()
        print(f'Move: {rootstate.moveGenerator.print_move(move)}, score: {wins / visits}')
        results.append((move, wins/visits))

    # the score here refers to the score of the best enemy reply -> we choose a move which leads to a best enemy reply
    # with the least score
    best_move, score = sorted(results, key=itemgetter(1))[0]
    return best_move


def rand_choice(x):  # fastest way to get random item from list
    return x[int(random.random() * len(x))]


def uct(queue: Queue, move_origin, rootstate, itermax):
    """ Conduct a UCT search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
        Assumes 2 alternating players (player 1 starts), with game results in the range [0.0, 1.0]."""

    rootnode = Node(state=rootstate)

    state = rootstate
    for i in range(itermax):
        node = rootnode
        moves_to_root = 0

        game_over = False
        # Select
        while not node.untriedMoves and node.childNodes:  # node is fully expanded and non-terminal
            node = node.uct_select_child()
            state.make_move(node.move)
            moves_to_root += 1
            if state.get_result(state.playerJustMoved) is not None:
                # Backpropagate
                while node is not None:  # backpropagate from the expanded node and work back to the root node
                    # state is terminal. Update node with result from POV of node.playerJustMoved
                    result = state.get_result(node.playerJustMoved)
                    node.update(result)
                    node = node.parentNode

                for _ in range(moves_to_root):
                    state.take_move()

                game_over = True
                break
        if game_over:
            continue

        # Expand
        if node.untriedMoves:  # if we can expand (i.e. state/node is non-terminal)
            m = rand_choice(node.untriedMoves)
            state.make_move(m)
            moves_to_root += 1
            node = node.add_child(m, state)  # add child and descend tree

        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        while state.get_result(state.side) is None:  # while state is non-terminal
            state.make_move(rand_choice(state.get_moves()))
            moves_to_root += 1

        # Backpropagate
        while node is not None:  # backpropagate from the expanded node and work back to the root node
            # state is terminal. Update node with result from POV of node.playerJustMoved
            node.update(state.get_result(node.playerJustMoved))
            node = node.parentNode

        for _ in range(moves_to_root):
            state.take_move()

    # return sorted(rootnode.childNodes, key=lambda c: c.visits)[-1].move  # return the move that was most visited
    best_node = sorted(rootnode.childNodes, key=lambda c: c.visits)[-1]
    queue.put((move_origin, best_node.wins, best_node.visits))


def uct_play_game():
    """ Play a sample game between two UCT players where each player gets a different number 
        of UCT iterations (= simulations = tree nodes).
    """
    state = Board()
    # mate_in_2 = '3k4/Q7/8/3K4/8/8/8/8 w --'
    mate_in_3 = 'r5rk/5p1p/5R2/4B3/8/8/7P/7K w --'
    state.parse_fen(mate_in_3)

    while state.get_moves():
        print(state)
        start = time.time()
        m = uct_multi(rootstate=state, itermax=400)  # play with values for itermax and verbose = True
        print('Time it took', time.time() - start)
        print("Best Move: " + state.moveGenerator.print_move(m) + "\n")
        state.make_move(m)
    print(state)
    if state.get_result(state.playerJustMoved) == 1.0:
        print("Player " + str(state.playerJustMoved) + " wins!")
    elif state.get_result(state.playerJustMoved) == 0.0:
        print("Player " + str(3 - state.playerJustMoved) + " wins!")
    else:
        print("Nobody wins!")


if __name__ == "__main__":
    """ Play a single game to the end using UCT for both players. 
    """
    # uct_play_game()
    state = Board()
    # mate_in_2 = '3k4/Q7/8/3K4/8/8/8/8 w --'
    mate_in_3 = 'r5rk/5p1p/5R2/4B3/8/8/7P/7K w --'
    state.parse_fen(mate_in_3)
    print(state)
    while state.get_result(state.playerJustMoved) is None:
        start = time.time()
        m = uct_multi(state, itermax=4000)
        print('Time it took', time.time()-start)
        state.make_move(m)
        print(state)

    # results = []
    # item = [1, 3, 4]
    # for _ in range(10000):
    #     start = time.time()
    #     if not item:
    #         pass
    #     results.append(time.time()-start)
    #
    # print('Avg: ', sum(results)/ len(results))
