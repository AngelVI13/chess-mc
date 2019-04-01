import operator
import sys

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
    """is called everytime a move is made this method is called to check if the game is ended"""

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


def search_position(pos: Board) -> int:
    move = playout(pos, root_side=SIDE_TO_PLAYER_MAP[pos.side], root=True, simulations=5000)
    return move


def get_killer_move(board: Board, root_side: int):
    for move in board.generate_moves():
        success = board.make_move(move)
        if not success:
            continue

        winner = get_winner(board)
        board.take_move()

        if winner is not None:
            if winner == root_side:
                return root_side, move
            elif winner == -root_side:
                return -root_side, move
            return NO_PLAYER, move

    return None, None


def playout(board: Board, root_side, root=False, simulations=5000):
    wins = 0
    total = 0
    move_score = {}

    # Search for forced moves (moves that win the position immediately). If such are found
    # it assume us or the opponent will definitely play them -> evaluate the whole node to the
    # result of the forced move
    has_killer_move, move = get_killer_move(board, root_side)
    if has_killer_move is not None:
        if root:
            return move

        if has_killer_move == root_side:
            wins += 1
        elif has_killer_move == -root_side:
            wins -= 1

        total += 1
        return wins, total  # todo unnecessary maths

    for move in board.generate_moves():
        success = board.make_move(move)
        if not success:
            continue

        winner = get_winner(board)
        if winner is None:
            node_wins, node_total = playout(board, root_side, simulations=simulations)
            board.take_move()

            # todo if an edge case is found i.e. 0/x or 100%/x -> don't bother looking for other moves ?

            wins += node_wins
            total += node_total

            if root:
                move_score[move] = node_wins / node_total
            else:
                # check total simulations so far
                if total > simulations:
                    return wins, total

            continue

        board.take_move()  # take back move
        if winner == root_side:
            wins += 1
        elif winner == -root_side:
            wins -= 1

        total += 1

        if root:  # this can happen when there is only 1 move available and it results in a winner
            move_score[move] = wins / total
        else:
            # check total simulations so far
            if total > simulations:
                return wins, total

    if root:
        # sort moves by their score and return move with highest score
        move, value = sorted(move_score.items(), key=operator.itemgetter(1))[-1]
        # print(sorted(move_score.items(), key=operator.itemgetter(1)))
        return move

    return wins, total
