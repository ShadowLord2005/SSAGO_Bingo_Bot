from typing import TYPE_CHECKING

from sqlalchemy import MetaData, Table, delete

from alembic import op

if TYPE_CHECKING:
    from typing import Any

    from sqlalchemy.engine import Connection

core_type : list[dict[str, Any]] = [
    {
        "type_id":0,
        "type_name":"Core",
        "type_description":"This is a type to be used a a generic parent type for types with no other parent. It contains a squares that should be in every type"
    }
]

core_square : list[dict[str, Any]] = [
    {
        "square_id":0,
        "game_type_id":0,
        "square":"Free Space"
    }
]

def get_data_tables(bind : Connection) -> list[Table]:
    meta = MetaData()

    game_types = Table("game_types", meta, autoload_with=bind)
    squares = Table("squares", meta, autoload_with=bind)
    return [game_types, squares]

def add_data(bind : Connection) -> None:
    tables = get_data_tables(bind)

    op.bulk_insert(tables[0], core_type)


    op.bulk_insert(tables[1], core_square)

def remove_data(bind : Connection):
    tables = get_data_tables(bind)
    type_stmt = delete(tables[0]).where(tables[0].c.type_id == 0)
    bind.execute(type_stmt)
    square_stmt = delete(tables[1]).where(tables[1].c.square_id == 0)
    bind.execute(square_stmt)
