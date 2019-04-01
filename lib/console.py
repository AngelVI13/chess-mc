from lib.constants import *
from lib.board import Board
from lib.search import search_position


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
        print("1/2-1/2:fifty move rule (claimed by Hugo)\n")
        return DRAW

    if get_threefold_repetition_count(pos) >= 2:
        print("1/2-1/2:3-fold repetition (claimed by Hugo)\n")
        return DRAW

    if is_position_draw(pos):
        print("1/2-1/2:insufficient material (claimed by Hugo)\n")
        return DRAW

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
            print("0-1:black mates (claimed by Hugo)\n")
            return WINNER_BLACK

        print("1-0:white mates (claimed by Hugo)\n")
        return WINNER_WHITE

    # not in check but no legal moves left -> stalemate
    print("\n1/2-1/2:stalemate (claimed by Hugo)\n")
    return DRAW


def console_loop(pos: Board):
    # InitHashTable(pos.HashTable)

    print("Welcome to Hugo In Console Mode!\n")
    print("Type help for commands\n\n")

    # info.GameMode = ConsoleMode
    # info.PostThinking = True

    move_time = 3000  # 3 seconds move time

    engine_side = BLACK
    pos.parse_fen(START_FEN)

    while True:
        if pos.side == engine_side and get_winner(pos) is not None:
            # info.StartTime = time.time()

            # if moveTime != 0:
            #     info.TimeSet = True
            #     info.StopTime = moveTime

            # pos, info = SearchPosition(pos, info)
            move = search_position(pos)

        command = input("\nHugo > ")
        if len(command) < 2:
            continue

        if "help" in command:
            print("Commands:\n")
            print("quit - quit game\n")
            print("force - computer will not think\n")
            print("print - show board\n")
            print("post - show thinking\n")
            print("nopost - do not show thinking\n")
            print("new - start new game\n")
            print("mirror - prints the current position and then it's mirrored image.\n")
            print("setboard x - set position to fen x\n")
            print("go - set computer thinking\n")
            print("depth x - set depth to x\n")
            print("time x - set thinking time to x seconds (depth still applies if set)\n")
            print("view - show current depth and moveTime settings\n")
            print("showline - show current move line so far\n")
            print("** note ** - to reset time and depth, set to 0\n")
            print("enter moves using b7b8q notation\n\n\n")
            continue

        if "setboard" in command:
            engine_side = BOTH
            start_str = "setboard "
            fen = command[command.index(start_str) + len(start_str):]
            pos.parse_fen(fen)
            continue

        if "quit" in command:
            # info.Quit = True
            break

        if "post" in command == 0:
            # info.PostThinking = True
            continue

        if "print" in command:
            print(pos)
            continue

        if "nopost" in command == 0:
            # info.PostThinking = False
            continue

        if "force" in command:
            engine_side = BOTH
            continue

        if "view" in command:
            if move_time != 0:
                print(" moveTime {}".format(move_time/1000))
            else:
                print(" moveTime not set\n")

            continue

        if "genmoves" in command:
            move_list = pos.generate_moves()

            print("Moves found: {}".format(len(move_list)))
            continue

        if "getres" in command:
            print("Winner is: {}".format(get_winner(pos)))
            continue

        # if "showline" in command: TODO
        #     print(GetBookMove(pos))
        #     continue

        if "depth" in command:
            # does not support depth
            continue

        if "time" in command:
            move_time_str1 = command[command.index("time ") + len("time "):]
            # moveTimeStr2 = moveTimeStr1[:moveTimeStr1.index(' ')]
            move_time = int(move_time_str1)
            move_time *= 1000
            continue

        if "new" in command:
            engine_side = BLACK
            pos.parse_fen(START_FEN)
            continue

        if "go" in command:
            engine_side = pos.side
            continue

        if "take" in command:
            pos.take_move()
            continue

        move = pos.parse_move(command)
        if move == NO_MOVE:
            print("Command unknown: {}".format(command))
            continue

        pos.make_move(move)
