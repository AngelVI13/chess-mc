from lib.console import console_loop
from lib.board import Board


if __name__ == '__main__':
    fen = "3k4/3Q4/3K4/8/8/8/8/8 w --"

    board = Board()
    # info = SearchInfo()

    print("Welcome to Hugo! Type 'hugo' for console mode...\n")

    while True:
        line = input("")
        if len(line) < 2:
            continue

        if "uci" in line:
            # board, info = UciLoop(board, info)
            # if info.Quit:
            #     break
            continue
        elif "hugo" in line:
            console_loop(board)
            # if info.Quit:
            #     break
            # continue
            break
        elif "quit" in line:
            break
