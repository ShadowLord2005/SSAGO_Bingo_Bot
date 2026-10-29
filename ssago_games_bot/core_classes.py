import logging
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

handler = logging.StreamHandler()

logger = logging.getLogger("SSAGO Game Bot")
logger.setLevel(logging.INFO)
logger.addHandler(handler)



class Status(Enum):
    AWAITING_START = 1
    RUNNING = 2
    FINISHED = 3

    @classmethod
    def transform(cls, status : str) -> Status: # pyright: ignore[reportReturnType]
        for i in Status:
            if i.value == status:
                return i
            else:
                continue

class ROWS(Enum):
    ONE =   (1, (0, 1,  2,  3,  4))
    TWO =   (2, (5, 6,  7,  8,  9))
    THREE = (3, (10,11, 12, 13, 14))
    FOUR =  (4, (15,16, 17, 18, 19))
    FIVE =  (5, (20,21, 22, 23, 24))

    def __getitem__(self, index : int):
        return self.value[1][index]

    def row_num(self):
        return self.value[0]

    def row_index(self):
        return (self.value[0]-1)


class Grid:
    def __init__(self) -> None:
        self.board: list[list[Any]] = []

    def __str__(self) -> str:
        printable = ""

        for row in self.board:
            printable = printable + (str(row)) + "\n"

        return(printable)

    def __iter__(self):
        self.row_num = 0
        return self

    def __next__(self):
        if self.row_num < len(self.board):
            row = self.board[self.row_num]
            self.row_num += 1
            return row
        else:
            raise StopIteration

    def add_row(self) -> list:
        row: list[str] = []
        self.board.append(row)
        return row

class BoardStatements(Grid):
    def __init__(self) -> None:
        super().__init__()
        self.board : list[list[str]] = []

class BoardIDs(Grid):
    def __init__(self) -> None:
        super().__init__()
        self.board : list[list[int]] = []

class BoardState(Grid):
    def __init__(self) -> None:
        super().__init__()
        self.board : list[list[bool]] = []

