from csv import DictReader

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy import Connection



def get_data(folder_name : str, bind : Connection):
    pass