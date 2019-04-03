from lib.search import *


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
        if pos.side == engine_side and pos.get_result() is None:
            # info.StartTime = time.time()

            # if moveTime != 0:
            #     info.TimeSet = True
            #     info.StopTime = moveTime

            # pos, info = SearchPosition(pos, info)
            move = search_position(pos, simulations=1000)
            print("\n\n***!! Hugo makes move {} !!***\n\n".format(pos.moveGenerator.print_move(move)))
            pos.make_move(move)
            print(pos)

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

            print("Moves found: {}".format(len(list(move_list))))
            continue

        if "getres" in command:
            print("Winner is: {}".format(pos.get_result()))
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
