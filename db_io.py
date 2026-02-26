from datetime import datetime, timedelta
from enum import Enum
from os import environ
from pathlib import Path
from random import choices, randint
from string import ascii_letters, digits
from typing import TYPE_CHECKING

from psycopg import AsyncConnection

if TYPE_CHECKING:
    from string.templatelib import Template
    from typing import Any

database = environ.get("POSTGRES_DB")
user = environ.get("POSTGRES_USER")
server = environ.get("ADMINER_DEFAULT_SERVER")

password_file = "database_password.txt"

class Status(Enum):
    START_SCHEDULED = 'Start Scheduled'
    AWAITING_START = 'Awaiting Start'
    RUNNING = 'Running'
    FINISHED = 'Finished'

    @classmethod
    def transform(cls, status : str) -> Status: # pyright: ignore[reportReturnType]
        for i in Status:
            if i.value == status:
                return i
            else:
                continue

class AsyncCursor:
    def __init__(self):
        with Path(password_file).open() as pw_file:
            password = pw_file.read()
        self.conn_info = f"host={server} dbname={database} user={user} password={password}"

    async def execute(self, command: Template):
        async with await AsyncConnection.connect(conninfo=self.conn_info) as aconn:  # noqa: SIM117
            async with aconn.cursor() as cur:
                await cur.execute(command)
                results = await cur.fetchall()
                return results

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


class Game:
    def __init__(self, type_id : int, length : float, owner : int)-> None:
        self.type_id = type_id
        self.duration = timedelta(hours=length)
        self.owner = owner
        self.pin = "".join(choices(ascii_letters + digits,k=10))
        self.scheduled = False
        self.status = Status.AWAITING_START
        self.start = "NULL"

    def schedule(self, start_time : datetime):
        if start_time.tzinfo == None:
            raise Exception
        else:
            self.start = start_time
            self.status = Status.START_SCHEDULED
            self.scheduled = True

    def set_info(self) -> Template:
        info = t"{self.type_id}, {self.scheduled}, {self.start}, {self.duration}, {self.pin}, {self.owner}, {self.status}"
        return info

    def new_pin(self) -> None:
        self.pin = "".join(choices(ascii_letters + digits,k=10))




def shuffle(raw_list : list[Any]):
    shuffled_list : list[Any] = []
    num_iter = len(raw_list)
    while len(shuffled_list) != num_iter:
        index = randint(0, len(raw_list))
        shuffled_list.append(raw_list[index])
        raw_list.pop(index)
    return shuffled_list

# Obtain_xx: Get some data out of the database and return it
# Create_xx: Create data ready for inserting into the database and return the correct format for set commands. Generally doesn't interface with the database
# Set_xx: Insert data into the data, generally doesn't return anything


#Player Related Commands
async def obtain_player_id(discord_id : int, game_id : int) -> int:
    cursor = AsyncCursor()
    id_command = t"SELECT player_id FROM player_info WHERE discord_id = {discord_id} AND game_id = {game_id}"
    player_id = (await cursor.execute(id_command))[0][0]
    return player_id

async def set_player_id(discord_id : int, game_id : int) -> None:
    cursor = AsyncCursor()
    id_command = t"INSERT INTO player_info (discord_id, game_id) VALUES ({discord_id},{game_id})"
    await cursor.execute(id_command)


# Board Related Commands
async def obtain_square_options(type_id : int) -> list[int]:
    cursor = AsyncCursor()
    squares_command = t"SELECT square_id FROM square_type_rel WHERE type_id = {type_id}"
    raw_square_ids = await cursor.execute(squares_command)
    square_ids = [raw_square_ids[i][0] for i in range(len(raw_square_ids))]
    return square_ids

async def obtain_board(player_id : int) -> BoardStatements:
    cursor = AsyncCursor()
    board_command = t"SELECT square FROM card_squares INNER JOIN card_info USING (square_id) WHERE card_info.player_id = {player_id} ORDER BY card_info.square_position"
    board_squares = await cursor.execute(board_command)
    board = BoardStatements()
    k = 0
    for i in range(5):
        row = board.add_row()
        for j in range(5):
            square = board_squares[k][0]
            row.append(square)
            k += 1
    return board

async def create_board(square_options: list[int]) -> list[int]:
    chosen_squares : list[int] = []
    while len(chosen_squares) < 24:
        i = randint(0,len(square_options))
        chosen_squares.append(square_options[i])
        square_options.pop(i)
    chosen_squares = shuffle(chosen_squares)
    chosen_squares.insert(12, 0)
    return chosen_squares

async def set_board(player_id: int, board_ids : list[int]) -> None:
    cursor = AsyncCursor()
    for i in range(len(board_ids)):
        square_id = board_ids[i]
        square_position = i
        card_command = t"INSERT INTO card_info (player_id, square_id, square_position) VALUES ({player_id}, {square_id}, {square_position})"
        await cursor.execute(card_command)

async def obtain_board_state(player_id : int) -> BoardState:
    cursor = AsyncCursor()
    status_command = t"SELECT square_status FROM card_info WHERE player_id = {player_id} ORDER BY square_position"
    returned_status = await cursor.execute(status_command)
    state = BoardState()
    k = 0
    for _ in range(5):
        row = state.add_row()
        for _ in range(5):
            square = returned_status[k][0]
            row.append(square)
            k += 1
    return state

async def set_square_status(player_id : int, square_position : int, status : bool) -> None:
    cursor = AsyncCursor()
    set_command = t"UPDATE card_info SET square_status = {status} WHERE player_id = {player_id} AND square_position = {square_position}"
    await cursor.execute(set_command)


# Game Related Commands
async def set_game_info(game : Game) -> None:
    cursor = AsyncCursor()
    info_command = t"INSERT INTO games (type_id, is_scheduled, game_start, game_length, game_pin, game_owner, game_status) VALUES ({game.set_info():q})"
    await cursor.execute(info_command)

async def set_game_status(game_id : int, status : Status) -> None:
    cursor = AsyncCursor()
    status_command = t"UPDATE games SET game_status = {status} WHERE game_id = {game_id}"
    await cursor.execute(status_command)


# Admin Related Commands
async def obtain_types() -> list[tuple[str]]:
    cursor = AsyncCursor()
    types_command = t"SELECT type_name, type_description FROM game_types WHERE type_id > 0"
    raw_types = await cursor.execute(types_command)
    return raw_types





if __name__ == "__main__":
    import asyncio
    squares = asyncio.run(obtain_types())
    print(squares)


