from ctypes import c_uint64
from random import getrandbits
from typing import List, Dict

BOARD_SQUARE_NUMBER = 120
PIECE_CHARACTER_STRING = ".PNBRQKpnbrqk"
SIDE_CHAR = "wb-"
START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


EMPTY = 0
WHITE_PAWN = 1
WHITE_KNIGHT = 2
WHITE_BISHOP = 3
WHITE_ROOK = 4
WHITE_QUEEN = 5
WHITE_KING = 6
BLACK_PAWN = 7
BLACK_KNIGHT = 8
BLACK_BISHOP = 9
BLACK_ROOK = 10
BLACK_QUEEN = 11
BLACK_KING = 12


RANK_1, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8, RANK_NONE = range(9)
FILE_A, FILE_B, FILE_C, FILE_D, FILE_E, FILE_F, FILE_G, FILE_H, FILE_NONE = range(9)

WHITE = 0
BLACK = 1
BOTH = 2


# Defines for board square indexes based on 120-square board
A1, B1, C1, D1, E1, F1, G1, H1 = range(21, 28 + 1)  # Rank 1
A2, B2, C2, D2, E2, F2, G2, H2 = range(31, 38 + 1)  # Rank 2
A3, B3, C3, D3, E3, F3, G3, H3 = range(41, 48 + 1)  # Rank 3
A4, B4, C4, D4, E4, F4, G4, H4 = range(51, 58 + 1)  # Rank 4
A5, B5, C5, D5, E5, F5, G5, H5 = range(61, 68 + 1)  # Rank 5
A6, B6, C6, D6, E6, F6, G6, H6 = range(71, 78 + 1)  # Rank 6
A7, B7, C7, D7, E7, F7, G7, H7 = range(81, 88 + 1)  # Rank 7
A8, B8, C8, D8, E8, F8, G8, H8 = range(91, 98 + 1)  # Rank 8
# No square
NO_SQUARE = 99
OFF_BOARD = 100

# PieceNotationMap maps piece notations (i.e. 'p', 'N') to piece values (i.e. 'BlackPawn', 'WhiteKnight')
PIECE_NOTATION_MAP = {
    "p": BLACK_PAWN,
    "r": BLACK_ROOK,
    "n": BLACK_KNIGHT,
    "b": BLACK_BISHOP,
    "k": BLACK_KING,
    "q": BLACK_QUEEN,
    "P": WHITE_PAWN,
    "R": WHITE_ROOK,
    "N": WHITE_KNIGHT,
    "B": WHITE_BISHOP,
    "K": WHITE_KING,
    "Q": WHITE_QUEEN,
}

# FileNotationMap maps file notations (i.e. 'a', 'h') to file values (i.e. 'FileA', 'FileH')
FILE_NOTATION_MAP = {
    "a": FILE_A,
    "b": FILE_B,
    "c": FILE_C,
    "d": FILE_D,
    "e": FILE_E,
    "f": FILE_F,
    "g": FILE_G,
    "h": FILE_H,
}

# A map used to identify a piece's colour
PIECE_COLOR_MAP: Dict[int, int] = {
    EMPTY: BOTH,
    WHITE_PAWN: WHITE,
    WHITE_KNIGHT: WHITE,
    WHITE_BISHOP: WHITE,
    WHITE_ROOK: WHITE,
    WHITE_QUEEN: WHITE,
    WHITE_KING: WHITE,
    BLACK_PAWN: BLACK,
    BLACK_KNIGHT: BLACK,
    BLACK_BISHOP: BLACK,
    BLACK_ROOK: BLACK,
    BLACK_QUEEN: BLACK,
    BLACK_KING: BLACK,
}

# A list that returns which file a particular square is on
FilesBoard: List[int] = [OFF_BOARD] * BOARD_SQUARE_NUMBER

# A list that returns which file a particular square is on
RanksBoard: List[int] = [OFF_BOARD] * BOARD_SQUARE_NUMBER


# --- Maps used to quickly resolve the type of a piece regardless of its colour
IS_PIECE_KNIGHT: Dict[int, bool] = {
    EMPTY: False,
    WHITE_PAWN: False,
    WHITE_KNIGHT: True,
    WHITE_BISHOP: False,
    WHITE_ROOK: False,
    WHITE_QUEEN: False,
    WHITE_KING: False,
    BLACK_PAWN: False,
    BLACK_KNIGHT: True,
    BLACK_BISHOP: False,
    BLACK_ROOK: False,
    BLACK_QUEEN: False,
    BLACK_KING: False,
}

IS_PIECE_KING: Dict[int, bool] = {
    EMPTY: False,
    WHITE_PAWN: False,
    WHITE_KNIGHT: False,
    WHITE_BISHOP: False,
    WHITE_ROOK: False,
    WHITE_QUEEN: False,
    WHITE_KING: True,
    BLACK_PAWN: False,
    BLACK_KNIGHT: False,
    BLACK_BISHOP: False,
    BLACK_ROOK: False,
    BLACK_QUEEN: False,
    BLACK_KING: True,
}

IS_PIECE_ROOK_QUEEN: Dict[int, bool] = {
    EMPTY: False,
    WHITE_PAWN: False,
    WHITE_KNIGHT: False,
    WHITE_BISHOP: False,
    WHITE_ROOK: True,
    WHITE_QUEEN: True,
    WHITE_KING: False,
    BLACK_PAWN: False,
    BLACK_KNIGHT: False,
    BLACK_BISHOP: False,
    BLACK_ROOK: True,
    BLACK_QUEEN: True,
    BLACK_KING: False,
}

IS_PIECE_BISHOP_QUEEN: Dict[int, bool] = {
    EMPTY: False,
    WHITE_PAWN: False,
    WHITE_KNIGHT: False,
    WHITE_BISHOP: True,
    WHITE_ROOK: False,
    WHITE_QUEEN: True,
    WHITE_KING: False,
    BLACK_PAWN: False,
    BLACK_KNIGHT: False,
    BLACK_BISHOP: True,
    BLACK_ROOK: False,
    BLACK_QUEEN: True,
    BLACK_KING: False,
}

IS_PIECE_PAWN: Dict[int, bool] = {
    EMPTY: False,
    WHITE_PAWN: True,
    WHITE_KNIGHT: False,
    WHITE_BISHOP: False,
    WHITE_ROOK: False,
    WHITE_QUEEN: False,
    WHITE_KING: False,
    BLACK_PAWN: True,
    BLACK_KNIGHT: False,
    BLACK_BISHOP: False,
    BLACK_ROOK: False,
    BLACK_QUEEN: False,
    BLACK_KING: False,
}

IS_PIECE_SLIDING: Dict[int, bool] = {
    EMPTY: False,
    WHITE_PAWN: False,
    WHITE_KNIGHT: False,
    WHITE_BISHOP: True,
    WHITE_ROOK: True,
    WHITE_QUEEN: True,
    WHITE_KING: False,
    BLACK_PAWN: False,
    BLACK_KNIGHT: False,
    BLACK_BISHOP: True,
    BLACK_ROOK: True,
    BLACK_QUEEN: True,
    BLACK_KING: False,
}


# squares increment for each direction of movement
PIECE_MOVEMENT_INCREMENT: Dict[int, List[int]] = {
    EMPTY: [0, 0, 0, 0, 0, 0, 0],
    WHITE_PAWN: [0, 0, 0, 0, 0, 0, 0],
    WHITE_KNIGHT: [-8, -19, -21, -12, 8, 19, 21, 12],
    WHITE_BISHOP: [-9, -11, 11, 9, 0, 0, 0, 0],
    WHITE_ROOK: [-1, -10, 1, 10, 0, 0, 0, 0],
    WHITE_QUEEN: [-1, -10, 1, 10, -9, -11, 11, 9],
    WHITE_KING: [-1, -10, 1, 10, -9, -11, 11, 9],
    BLACK_PAWN: [0, 0, 0, 0, 0, 0, 0],
    BLACK_KNIGHT: [-8, -19, -21, -12, 8, 19, 21, 12],
    BLACK_BISHOP: [-9, -11, 11, 9, 0, 0, 0, 0],
    BLACK_ROOK: [-1, -10, 1, 10, 0, 0, 0, 0],
    BLACK_QUEEN: [-1, -10, 1, 10, -9, -11, 11, 9],
    BLACK_KING: [-1, -10, 1, 10, -9, -11, 11, 9],
}

# number of directions in which each piece can move
DIRECTIONS_OF_MOVEMENT: Dict[int, int] = {
    EMPTY: 0,
    WHITE_PAWN: 0,
    WHITE_KNIGHT: 8,
    WHITE_BISHOP: 4,
    WHITE_ROOK: 4,
    WHITE_QUEEN: 8,
    WHITE_KING: 8,
    BLACK_PAWN: 0,
    BLACK_KNIGHT: 8,
    BLACK_BISHOP: 4,
    BLACK_ROOK: 4,
    BLACK_QUEEN: 8,
    BLACK_KING: 8,
}

# KnightDir Squares increment to find places where the knight will be attacking the current piece
# For example if we want to check if square 55 (e4) is attacked. We need to check if there is a
# opposite coloured knight on square 55-8 = 47, 55-19=36 etc.
KNIGHT_MOVE_INCREMENT = [-8, -19, -21, -12, 8, 19, 21, 12]
ROOK_MOVE_INCREMENT = [-1, -10, 1, 10]  # horizontal and vertical direction from a given pos
BISHOP_MOVE_INCREMENT = [-9, -11, 11, 9]
KING_MOVE_INCREMENT = [-1, -10, 1, 10, -9, -11, 11, 9]

# Defines for castling rights
# The values are such that they each represent a bit from a 4 bit int value for example if white can castle
# kingside and black can castle queenside the 4 bit int value is going to be 1001
WHITE_KING_CASTLING, WHITE_QUEEN_CASTLING, BLACK_KING_CASTLING, BLACK_QUEEN_CASTLING = [2**x for x in range(4)]


def get_2d_list(num_lists, size_lists, default_val) -> List[List[int]]:
    """Generate a NON linked list of lists"""
    main_list = []
    empty_list = [default_val] * size_lists

    for i in range(num_lists):
        main_list.append(list(empty_list))
    return main_list


class HashData:
    def __init__(self):
        # Hashkeys for each piece for each possible position for the key
        self.pieceKeys: List[List[c_uint64]] = get_2d_list(num_lists=13, size_lists=BOARD_SQUARE_NUMBER, default_val=0)

        # SideKey the hashkey associated with the current side
        self.sideKey: c_uint64 = 0

        # CastleKeys haskeys associated with castling rights
        self.castleKeys: List[int] = [0]*16  # castling value ranges from 0-15 -> we need 16 hashkeys

        self._fill_values()  # Generate values of all hash related fields

    def _fill_values(self):
        """initializes hashkeys for all pieces and possible positions, for castling rights, for side to move"""

        for piece in range(13):
            for square in range(BOARD_SQUARE_NUMBER):
                self.pieceKeys[piece][square] = getrandbits(64)  # returns a random 64 bit number

        self.sideKey = getrandbits(64)
        for i in range(16):
            self.castleKeys[i] = getrandbits(64)
