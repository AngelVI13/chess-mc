import sys

from lib.board import Board
from lib.mcts import uct


sys.setrecursionlimit(5000)


def search_position(pos: Board, simulations=1000) -> int:
    return uct(rootstate=pos, itermax=simulations)
