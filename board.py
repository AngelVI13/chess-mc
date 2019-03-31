from constants import *
from movegenerator import MoveGenerator


class Board:
    def __init__(self):
        self.pieces: List[int] = [0] * BOARD_SQUARE_NUMBER
        self.side: int = 0
        self.castlePerm: int = 0  # castle permissions
        # position key is a unique key stored for each position (used to keep track of 3fold repetition)
        self.posKey: c_uint64 = 0
        self.kingSquare: List[int] = [0] * 2  # White's & black's king position
        self.enPassantSquare: int = 0  # square in which en passant capture is possible
        self.fiftyMove: int = 0  # how many moves from the fifty move rule have been made
        self.histPly: int = 0  # how many half moves have been made

        # The piece list below make it easier to determine drawn positions or insufficient material
        self.pieceNumber: List[int] = [0] * 13  # how many pieces of each type are there currently on the board

        # Create related objects
        self.hashData = HashData()
        self.moveGenerator = MoveGenerator(self)

        # Initialize convertion tables
        initialize_square_convertion_lists()  # todo potentially move somewhere else
        initialize_file_rank_board()  # todo potentially move somewhere else

    def __str__(self):
        board_rep = ["\nGame Board:\n\n"]

        for rank in reversed(range(RANK_8 + 1)):
            rank_line = ["{}  ".format(rank + 1)]
            for file in range(FILE_H + 1):
                sq = convert_file_rank_to_square(file, rank)
                piece = self.pieces[sq]
                rank_line.append(" {} ".format(PIECE_CHARACTER_STRING[piece]))

            rank_line.append('\n')
            board_rep.append(''.join(rank_line))

        board_rep.append("\n   ")

        bottom_line = []
        for file in range(FILE_H + 1):
            bottom_line.append(" {} ".format(chr(ord('a') + file)).upper())

        board_rep.append(''.join(bottom_line))

        board_rep.append("\n\n")
        board_rep.append("side: {}\n".format(SIDE_CHAR[self.side]))
        board_rep.append("enPas: {}\n".format(self.enPassantSquare))

        # Compute castling permissions. w_kca - white kingside castling, b_qca - black queenside castling etc
        w_kca = "-"
        if self.castlePerm & WHITE_KING_CASTLING != 0:
            w_kca = "K"

        w_qca = "-"
        if self.castlePerm & WHITE_QUEEN_CASTLING != 0:
            w_qca = "Q"

        b_kca = "-"
        if self.castlePerm & BLACK_KING_CASTLING != 0:
            b_kca = "k"

        b_qca = "-"
        if self.castlePerm & BLACK_QUEEN_CASTLING != 0:
            b_qca = "q"

        board_rep.append("castle: {}{}{}{}\n".format(w_kca, w_qca, b_kca, b_qca))
        board_rep.append("PosKey: {}\n".format(self.posKey))

        return ''.join(board_rep)

    def __hash__(self):
        """Generate a unique hashkey for a given position"""
        final_key: c_uint64 = 0

        for sq in range(BOARD_SQUARE_NUMBER):
            piece = self.pieces[sq]
            # Do not calculate hashkey for squares that are not on the actual board, i.e. have value of NoSquare
            # Also do not calculate hashkey for an empty square
            if piece != NO_SQUARE and piece != EMPTY and piece != OFF_BOARD:
                # Check if we have a valid piece
                assert WHITE_PAWN <= piece <= BLACK_KING
                # Add/remove (xor) the hash value for a given piece and for a given position from the final hash value
                final_key ^= self.hashData.pieceKeys[piece][sq]

        if self.side == WHITE:
            final_key ^= self.hashData.sideKey

        if self.enPassantSquare != NO_SQUARE:
            assert 0 <= self.enPassantSquare < BOARD_SQUARE_NUMBER
            # We have already generated hash keys for all pieces + EMPTY
            # => the hashkeys for value empty are used for en passant hash calculations
            final_key ^= self.hashData.pieceKeys[EMPTY][self.enPassantSquare]

        assert 0 <= self.castlePerm <= 15

        final_key ^= self.hashData.castleKeys[self.castlePerm]

        return c_uint64(final_key)

    def reset(self):
        # Set all board positions to OFF_BOARD
        for i in range(BOARD_SQUARE_NUMBER):
            self.pieces[i] = OFF_BOARD

        # Set all real board positions to EMPTY
        for i in range(64):
            self.pieces[Sq64ToSq120[i]] = EMPTY

        # Reset piece number
        for i in range(13):  # todo replace magical number
            self.pieceNumber[i] = 0

        self.kingSquare[WHITE] = NO_SQUARE
        self.kingSquare[BLACK] = NO_SQUARE

        self.side = BOTH
        self.enPassantSquare = NO_SQUARE
        self.fiftyMove = 0
        self.histPly = 0
        self.castlePerm = 0
        self.posKey = 0

    def _parse_fen_pieces(self, fen) -> int:
        """Parses fen piece & square information and return char index of fen string at end of parsing"""

        rank = RANK_8  # we start from rank 8 since the notation starts from rank 8
        file = FILE_A
        char_idx = 0

        while (rank >= RANK_1) and char_idx < len(fen):
            count = 1
            char = fen[char_idx]

            if char in PIECE_NOTATION_MAP:
                # If we have a piece related char -> set the piece to corresponding value, i.e p -> BlackPawn
                piece = PIECE_NOTATION_MAP[char]
            elif char in ("1", "2", "3", "4", "5", "6", "7", "8"):
                # otherwise it must be a count of a number of empty squares
                piece = EMPTY
                count = int(char)  # get number of empty squares and store in count
            elif char in ("/", " "):
                # if we have / or space then we are either at the end of the rank or at the end of the piece list
                # -> reset variables and continue the while loop
                rank -= 1
                file = FILE_A
                char_idx += 1
                continue
            else:
                raise ValueError("------------!!! --- FEN error --- !!!------------------")

            # This loop, skips over all empty positions in a rank
            # When it comes to a piece that is different that "1"-"8" it places it on the corresponding square
            for i in range(count):
                sq64 = rank * 8 + file
                sq120 = Sq64ToSq120[sq64]
                if piece != EMPTY:
                    self.pieces[sq120] = piece

                file += 1

            char_idx += 1

        return char_idx

    def _parse_fen_options(self, fen, char_idx):
        """Parses position information i.e. en passant square, castling permission etc. from fen str and starting
        char index (index points to part of fen that starts listing position options)
        """
        # char should be set to the side to move part of the FEN string here
        char = fen[char_idx]
        assert (char == "w" or char == "b")

        self.side = WHITE if char == "w" else BLACK

        # move character pointer 2 characters further and it should now point to
        # the start of the castling permissions part of FEN
        char_idx += 2

        # Iterate over the next 4 chars-they show if white is allowed to castle king or queenside and the same for black
        for i in range(4):
            char = fen[char_idx]
            if char == " ":
                # when we hit a space, it means there are no more castling permissions => break
                break

            # Depending on the char, enable the corresponding castling permission related bit
            if char is "K":
                self.castlePerm |= WHITE_KING_CASTLING
            elif char is "Q":
                self.castlePerm |= WHITE_QUEEN_CASTLING
            elif char is "k":
                self.castlePerm |= BLACK_KING_CASTLING
            elif char is "q":
                self.castlePerm |= BLACK_QUEEN_CASTLING
            else:
                break

            char_idx += 1

        assert 0 <= self.castlePerm <= 15
        # move to the en passant square related part of FEN
        char_idx += 1
        char = fen[char_idx]

        if char != "-":
            file = FILE_NOTATION_MAP[char]
            char_idx += 1
            rank = int(fen[char_idx])  # get rank number
            rank -= 1  # decrement rank to match our indexes, i.e. Rank1 == 0

            assert FILE_A <= file <= FILE_H
            assert RANK_1 <= rank <= RANK_8

            self.enPassantSquare = convert_file_rank_to_square(file, rank)

    def parse_fen(self, fen):
        """parse fen position string and setup a position accordingly"""

        assert (fen != "")

        self.reset()  # resets board

        char_idx = self._parse_fen_pieces(fen)
        self._parse_fen_options(fen, char_idx)

        self.posKey = self.__hash__()  # generate pos key for new position
        self.update_material_lists()

    def update_material_lists(self):  # todo why not do this while parsing fen pieces
        """updates all material related piece lists"""
        for index in range(BOARD_SQUARE_NUMBER):
            piece = self.pieces[index]
            if piece != OFF_BOARD and piece != EMPTY:
                colour = PIECE_COLOR_MAP[piece]

                self.pieceNumber[piece] += 1  # increment piece number

                if piece == WHITE_KING or piece == BLACK_KING:
                    self.kingSquare[colour] = index

    @staticmethod
    def is_square_on_board(square) -> bool:
        return FilesBoard[square] != OFF_BOARD

    @staticmethod
    def is_side_valid(side) -> bool:
        return side == WHITE or side == BLACK

    @staticmethod
    def is_piece_valid(piece) -> bool:
        return WHITE_PAWN <= piece <= BLACK_KING

    @staticmethod
    def is_piece_valid_or_empty(piece) -> bool:
        return EMPTY <= piece <= BLACK_KING

    def is_square_attacked(self, sq: int, side: int) -> bool:  # todo move this to movegen ?
        """Determines if a given square is attacked from the opponent.
        NOTE: side here is the attacking side
        """
        assert self.is_square_on_board(sq)
        assert self.is_side_valid(side)

        # pawns
        # if attacking side is white and there are pawns infornt to the left and right of us, then we are attacked
        if side == WHITE:
            if self.pieces[sq - 11] == WHITE_PAWN or self.pieces[sq - 9] == WHITE_PAWN:
                return True

        else:
            if self.pieces[sq + 11] == BLACK_PAWN or self.pieces[sq + 9] == BLACK_PAWN:
                return True

        # knights
        # Loop through 8 directions
        for index in range(8):
            # find what piece is in that direction
            pce = self.pieces[sq + KNIGHT_MOVE_INCREMENT[index]]
            # if there is a knight of the opposite side at that piece -> return True
            if pce != OFF_BOARD and IS_PIECE_KNIGHT[pce] and PIECE_COLOR_MAP[pce] == side:
                return True

        # rooks, queens
        for index in range(4):
            dir_ = ROOK_MOVE_INCREMENT[index]  # get current direction
            to_sq = sq + dir_  # take the first square
            pce = self.pieces[to_sq]  # see what piece is there
            while pce != OFF_BOARD:  # while the piece is not OFF_BOARD
                if pce != EMPTY:  # if we hit a piece
                    # if that piece is a rook or queen from the opposite side
                    if IS_PIECE_ROOK_QUEEN[pce] and PIECE_COLOR_MAP[pce] == side:
                        return True  # our square is under attack -> return True

                    break  # otherwise we hit a piece that is not an attacker -> try another direction

                to_sq += dir_  # increment new piece square and perform check again
                pce = self.pieces[to_sq]  # get new piece

        # bishops, queens
        for index in range(4):  # todo could be rewriten as for _, dir = range bishopDir !!!!!!
            dir_ = BISHOP_MOVE_INCREMENT[index]
            to_sq = sq + dir_
            pce = self.pieces[to_sq]
            while pce != OFF_BOARD:
                if pce != EMPTY:
                    if IS_PIECE_BISHOP_QUEEN[pce] and PIECE_COLOR_MAP[pce] == side:
                        return True

                    break

                to_sq += dir_
                pce = self.pieces[to_sq]

        # kings
        for index in range(8):
            pce = self.pieces[sq + KING_MOVE_INCREMENT[index]]
            if pce != OFF_BOARD and IS_PIECE_KING[pce] and PIECE_COLOR_MAP[pce] == side:
                return True

        return False

    def generate_moves(self):
        return self.moveGenerator.generate_all_moves()


def initialize_square_convertion_lists():
    """Initializes square convertions lists to map from 120 to 64 based board representation"""
    sq64 = 0
    for rank in range(RANK_8 + 1):
        for file in range(FILE_H + 1):
            sq = convert_file_rank_to_square(file, rank)
            Sq64ToSq120[sq64] = sq
            Sq120ToSq64[sq] = sq64
            sq64 += 1


# Sq120ToSq64 would return the index of 120 mapped to a 64 square board
Sq120ToSq64: List[int] = [0]*BOARD_SQUARE_NUMBER

# Sq64ToSq120 would return the index of 64 mapped to a 120 square board
Sq64ToSq120: List[int] = [0]*64


def initialize_file_rank_board():
    """initialize lists that hold information about which rank & file a square is on the board"""
    # todo this method could be merged exactly with initialize_square_convertion_lists() !!!

    for rank in range(RANK_8 + 1):
        for file in range(FILE_H + 1):
            sq = convert_file_rank_to_square(file, rank)
            FilesBoard[sq] = file
            RanksBoard[sq] = rank


def convert_file_rank_to_square(file: int, rank: int) -> int:
    """Converts given file and rank to a square index (120-based)"""
    return (21 + file) + (rank * 10)


if __name__ == '__main__':
    # todo add unittests for ParseFen, UpdateMaterial, Hashing etc !!!!!!!!!!!!!!!!!!!!!!

    b = Board()
    move_gen_test_fen = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"
    b.parse_fen(move_gen_test_fen)
    print(b)
    moves = b.generate_moves()
    print(len(moves))
    for move in moves:
        print(b.moveGenerator.print_move(move))
