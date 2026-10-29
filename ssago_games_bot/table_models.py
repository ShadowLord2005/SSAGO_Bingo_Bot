from datetime import datetime, timedelta  # noqa: TC003
from enum import Enum
from random import choices
from string import ascii_letters, digits
from typing import List, Optional  # noqa: UP035

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    validates,
)

from ssago_games_bot.core_classes import Status  # noqa: TC001


class Base(DeclarativeBase):
    pass


class GameType(Base):
    __tablename__ = "game_types"
    type_id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type_name : Mapped[str] = mapped_column(String(50))
    type_description : Mapped[str] = mapped_column(Text, default="No Description has been provided")
    parent_type : Mapped[int] = mapped_column(ForeignKey("game_types.type_id"), default=0, nullable=True)
    squares : Mapped[List["Square"]] = relationship()
    games : Mapped[List["Game"]] = relationship()

class Square(Base):
    __tablename__ = "squares"
    square_id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_type_id : Mapped[int] = mapped_column(ForeignKey("game_types.type_id"))
    square : Mapped[str] = mapped_column(Text, nullable=False)


def new_game_pin() -> str:
    pin = "".join(choices(ascii_letters + digits,k=10))
    return pin

class Game(Base):
    __tablename__ = "games"
    game_id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type_id : Mapped[int] = mapped_column(ForeignKey("game_types.type_id"))
    game_start : Mapped[datetime] = mapped_column(nullable=False)
    game_end : Mapped[datetime] = mapped_column(nullable=False)
    game_pin : Mapped[str] = mapped_column(String(10), default = new_game_pin, unique=True)
    game_owner : Mapped[int] = mapped_column(nullable=False)
    game_status : Mapped[Status] = mapped_column()
    players : Mapped[List["Player"]] = relationship()


class Player(Base):
    __tablename__ = "player_info"
    player_id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    discord_id : Mapped[int] = mapped_column(nullable=False)
    game_id : Mapped[int] = mapped_column(ForeignKey("games.game_id"))
    card : Mapped[List["CardSquare"]] = relationship(order_by="card_info.square_position")

class CardSquare(Base):
    __tablename__ = "card_info"
    mapping_id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    player_id : Mapped[int] = mapped_column(ForeignKey("player_info.player_id"))
    square_id : Mapped[int] = mapped_column(ForeignKey("squares.square_id"))
    square_position : Mapped[int] = mapped_column(nullable=False)
    square_status : Mapped[bool] = mapped_column(default=False)

    @validates("square_position")
    def validate_position(self,key,position):
        if not 0<=position<=24:
            raise ValueError("Position must be between 0 and 24 inclusive")
        return position

class Models:
    CARD = CardSquare
    PLAYER = Player
    GAME = Game
    SQUARE = Square
    TYPE = GameType

