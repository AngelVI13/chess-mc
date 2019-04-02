import operator
import sys
from copy import deepcopy
from multiprocessing import Queue, Process

from lib.board import Board
from lib.constants import *


sys.setrecursionlimit(5000)


def get_threefold_repetition_count(pos: Board) -> int:
    """Detects how many repetitions for a given position"""
    repetition = 0

    for i in range(pos.histPly):
        if pos.history[i].posKey.value == pos.posKey.value:
            repetition += 1

    return repetition


def is_position_draw(pos: Board) -> bool:
    """Determine if position is a draw"""

    # if there are pawns on the board the one of the sides can get mated
    if pos.pieceNumber[WHITE_PAWN] != 0 or pos.pieceNumber[BLACK_PAWN] != 0:
        return False

    # if there are major pieces on the board the one of the sides can get mated
    if pos.pieceNumber[WHITE_QUEEN] != 0 or pos.pieceNumber[BLACK_QUEEN] != 0 or pos.pieceNumber[WHITE_ROOK] != 0 or (
            pos.pieceNumber[BLACK_ROOK] != 0):
        return False

    if pos.pieceNumber[WHITE_BISHOP] > 1 or pos.pieceNumber[BLACK_BISHOP] > 1:
        return False

    if pos.pieceNumber[WHITE_KNIGHT] > 1 or pos.pieceNumber[BLACK_KNIGHT] > 1:
        return False

    if pos.pieceNumber[WHITE_KNIGHT] != 0 and pos.pieceNumber[WHITE_BISHOP] != 0:
        return False

    if pos.pieceNumber[BLACK_KNIGHT] != 0 and pos.pieceNumber[BLACK_BISHOP] != 0:
        return False

    return True


def get_winner(pos: Board):
    """is called every time a move is made this method is called to check if the game is ended"""

    if pos.fiftyMove > 100:
        # print("1/2-1/2:fifty move rule (claimed by Hugo)\n")
        return NO_PLAYER

    if get_threefold_repetition_count(pos) >= 2:
        # print("1/2-1/2:3-fold repetition (claimed by Hugo)\n")
        return NO_PLAYER

    if is_position_draw(pos):
        # print("1/2-1/2:insufficient material (claimed by Hugo)\n")
        return NO_PLAYER

    move_list = pos.generate_moves()

    found = 0
    for move in move_list:
        result = pos.make_move(move)
        if not result:
            continue

        found += 1
        pos.take_move()
        break

    # we have legal moves -> game is not over
    if found != 0:
        return None

    in_check = pos.is_square_attacked(pos.kingSquare[pos.side], pos.side ^ 1)

    if in_check:
        if pos.side == WHITE:
            # print("0-1:black mates (claimed by Hugo)\n")
            return PLAYER_BLACK

        # print("1-0:white mates (claimed by Hugo)\n")
        return PLAYER_WHITE

    # not in check but no legal moves left -> stalemate
    # print("\n1/2-1/2:stalemate (claimed by Hugo)\n")
    return NO_PLAYER


def search_position(pos: Board, simulations=10000) -> int:
    move = r_playout_multi(pos, simulations)
    return move


def get_killer_move(board_: Board, root_side: int):
    for move in board_.generate_moves():
        success = board_.make_move(move)
        if not success:
            continue

        winner = get_winner(board_)
        board_.take_move()

        if winner is not None:
            if winner == root_side:
                return root_side, move
            elif winner == -root_side:
                return -root_side, move
            return NO_PLAYER, move

    return None, None


def nr_playout(board_: Board, root_side: int, simulations: int):
    wins, total = 0, 0

    has_killer_move, move = get_killer_move(board_, root_side)
    if has_killer_move is not None:
        if has_killer_move == root_side:
            wins += 1
        elif has_killer_move == -root_side:
            wins -= 1

        total += 1
        return wins, total  # todo unnecessary maths

    for move in board_.generate_moves():
        success = board_.make_move(move)
        if not success:
            continue

        winner = get_winner(board_)
        if winner is None:
            node_wins, node_total = nr_playout(board_, root_side, simulations)
            board_.take_move()

            wins += node_wins
            total += node_total

            # check total simulations so far
            if total > simulations:
                return wins, total
            continue

        board_.take_move()  # take back move

        if winner == root_side:  # if winner is the person who triggered the playout, increment counter
            wins += 1  # todo check if this is ever executed due to the forced/killer move above
        total += 1

        # check total simulations so far
        if total > simulations:
            return wins, total

    return wins, total


def node_playout(queue: Queue, b_: Board, move: int, root_side: int, simulations: int) -> (int, float):
    success = b_.make_move(move)
    if not success:
        return

    winner = get_winner(b_)
    if winner is None:
        node_wins, node_total = nr_playout(b_, root_side, simulations)
        score = node_wins / node_total

        b_.take_move()
        queue.put((move, score))
        return

    b_.take_move()  # take back move

    # if the player who made last move also won
    score = 1.0 if winner == root_side else 0.0
    queue.put((move, score))


def r_playout_multi(b_: Board, simulations=10000):
    queue = Queue()  # todo pass pointer to ?
    processes = []

    # generate tuples of arguments
    moves = b_.generate_moves()
    avg_simulations = simulations // len(moves)  # avg simulations per node

    for move in moves:
        p = Process(target=node_playout, args=(queue, deepcopy(b_), move, SIDE_TO_PLAYER_MAP[b_.side],
                                               avg_simulations,))
        processes.append(p)
        p.start()

    for process in processes:
        process.join()

    move_score = []
    while not queue.empty():
        move_score.append(queue.get())

    # sort moves by their score and return move with highest score
    move_, value = sorted(move_score, key=operator.itemgetter(1))[-1]
    # l = sorted(move_score, key=operator.itemgetter(1))
    # new_l = []
    # for move_int, score in l:
    #     new_l.append((b_.moveGenerator.print_move(move_int), score))
    # print(new_l)
    return move_


if __name__ == '__main__':
    board = Board()
    mate_in_3 = 'r5rk/5p1p/5R2/4B3/8/8/7P/7K w --'  # todo doesn't find forced move here...
    mate_in_2 = '3k4/Q7/8/3K4/8/8/8/8 w --'
    board.parse_fen(mate_in_3)
    print(board)

    m = search_position(board, simulations=600000)
    if m != NO_MOVE:
        board.make_move(m)
        print("\n\n***!! Hugo makes move {} !!***\n\n".format(board.moveGenerator.print_move(m)))
        print(board)

    # while get_winner(board) is None:
    #     m = search_position(board, simulations=500000)
    #     if m != NO_MOVE:
    #         board.make_move(m)
    #         print("\n\n***!! Hugo makes move {} !!***\n\n".format(board.moveGenerator.print_move(m)))
    #         print(board)
    #
    # print('\n\nWinner is:', get_winner(board))
