import logging

from discord.utils import MISSING

handler = logging.StreamHandler()

logger = logging.getLogger("SSAGO Game Bot")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

from enum import Enum
from os import getenv

import discord
from discord import app_commands, ui
from discord.ext import commands
from html2image import Html2Image

from db_io import BoardStatements, set_square_status

dev_guild_id = getenv("DEV_GUILD_ID")
logger.info(dev_guild_id)
guild = discord.Object(int(dev_guild_id)) if dev_guild_id != None else None

discord_token = getenv("DISCORD_TOKEN")

if discord_token == None:
    raise Exception

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

class GameMenu(discord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(title="Bingo Game Setup")



class BingoSquare(ui.Button):
    def __init__(self, label : str, square_position : int, row: CardRow):
        super().__init__(label=label, style=discord.ButtonStyle.gray)
        self.position = square_position
        self.card_row = row

    async def callback(self, interaction: discord.Interaction):
        self.style = discord.ButtonStyle.green
        player_id = interaction.user.id
        #await set_square_got(player_id, self.position)
        await interaction.response.edit_message(view=self.card_row.card)
        await interaction.followup.send(content=f"Player{player_id} has marked square {self.position} as got")
        logger.info("Player: %s has marked square %s as got", player_id, self.position)


class CardRow(ui.ActionRow):
    def __init__(self, row_statements: list[str], row : ROWS, card: BingoCard) -> None:
        super().__init__()
        for i in range(5):
            self.add_item(BingoSquare(row_statements[i], row[i], self))
        self.card = card



class BingoCard(ui.LayoutView):
    def __init__(self, board: BoardStatements) -> None:
        super().__init__(timeout=None)
        for row in ROWS:
            num = row.row_num() - 1
            self.add_item(CardRow(board.board[num], row, self))



class SSAGOGameBot(commands.Bot):
    #Suppress error on the User attribute being None
    user: discord.ClientUser # type: ignore

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=commands.when_mentioned_or("$$"),intents=intents)


    async def on_ready(self):
        logger.info("Logged in as %s", self.user)
        try:
            synced = await bot.tree.sync(guild=guild)
            id = guild.id if guild != None else "all"
            logger.info("Synced %s commands with server %s", len(synced), id)
        except Exception as e:
            logger.error(e)



test_card = BoardStatements()

k = 0
for i in range(5):
    row = test_card.add_row()
    for j in range(5):
        square = "Test Square" + str(k)
        row.append(square)
        k += 1


bot = SSAGOGameBot()

@bot.command("Grid")
async def grid(ctx : commands.Context[SSAGOGameBot]):
    await ctx.send(view=BingoCard(test_card))


@bot.tree.command(name="bingo", guild=guild)
async def demo(interaction : discord.Interaction):
    await interaction.response.send_message("Hello")


bot.run(discord_token, log_handler=handler)

