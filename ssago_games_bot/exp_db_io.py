from os import environ
from pathlib import Path
from random import randint
from typing import TYPE_CHECKING

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

import ssago_games_bot.core_classes as cc
from ssago_games_bot.table_models import Models

if TYPE_CHECKING:
    from datetime import datetime, timedelta
    from typing import Any


database = environ.get("POSTGRES_DB")
user = environ.get("POSTGRES_USER")
server = environ.get("ADMINER_DEFAULT_SERVER")

password_file = "database_password.txt"

with Path(password_file).open() as pw_file:
            password = pw_file.read()

engine_url = f"postgresql://{user}:{password}@{server}/{database}"

engine = create_engine(engine_url)

Session = sessionmaker(engine)

# Utility Functions

def shuffle[T](raw_list : list[T]):
    shuffled_list : list[T] = []
    num_iter = len(raw_list)
    while len(shuffled_list) != num_iter:
        index = randint(0, len(raw_list))
        shuffled_list.append(raw_list[index])
        raw_list.pop(index)
    return shuffled_list

# DB IO Functions
#Gets all the game types, their ids and descriptions in the correct format for the select wrapper for sending to the UI. This is in the order of label, description, value
def get_game_types() -> list[tuple[str,str,str]]:
    stmt = select(Models.TYPE).order_by(Models.TYPE.type_id)

    output : list[tuple[str,str,str]] = []

    with Session() as session, session.begin():
        game_types = session.scalars(stmt).all()

    for game_type in game_types:
        output.append((game_type.type_name, game_type.type_description, str(game_type.type_id)))

    return output


def new_game(owner_id : int, game_type : int, start_time : datetime, end_time : datetime) -> str:


    game = Models.GAME(
          game_owner = owner_id,
          type_id = game_type,
          game_start = start_time,
          game_end = end_time
    )

    game.game_status = cc.Status.AWAITING_START


    with Session() as session, session.begin():
          session.add(game)

    return game.game_pin



if __name__ == "__main__":
    stmt = select(Models.SQUARE)

    with Session() as session, session.begin():
        result = session.execute(stmt)

        squares = result.mappings().all()

        for square in squares:
            print(square)
            print(square.items())
            print(square.keys())
            print(square.values())


