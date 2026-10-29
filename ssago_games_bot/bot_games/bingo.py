
from datetime import datetime, time, timedelta
from typing import TYPE_CHECKING, Any

import discord
from discord import app_commands, ui
from discord.ext import commands

from ssago_games_bot.core_classes import ROWS, BoardStatements, logger
from ssago_games_bot.exp_db_io import get_game_types, new_game

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence



#Three Lists of tuples in the correct format for the Select Wrapper that contain the appropriate values for the Date Time Picker
ALL_HOURS = [
    ('00', None, '0'), ('01', None, '1'), ('02', None, '2'), ('03', None, '3'), ('04', None, '4'), ('05', None, '5'), ('06', None, '6'), ('07', None, '7'), ('08', None, '8'), ('09', None, '9'), ('10', None, '10'), ('11', None, '11'), ('12', None, '12'), ('13', None, '13'), ('14', None, '14'), ('15', None, '15'), ('16', None, '16'), ('17', None, '17'), ('18', None, '18'), ('19', None, '19'), ('20', None, '20'), ('21', None, '21'), ('22', None, '22'), ('23', None, '23')]

ALL_MINUTES = [
    ('00', None, None), ('10', None, None), ('15', None, None), ('20', None, None), ('25', None, None), ('30', None, None), ('35', None, None), ('40', None, None), ('45', None, None), ('50', None, None), ('55', None, None)]

ALL_DAYS = [
    ('Today at ', None, '0'), ('In 1 day at ', None, '1'), ('In 2 days at', None, '2'), ('In 3 days at', None, '3'), ('In 4 days at', None, '4'), ('In 5 days at', None, '5'), ('In 6 days at', None, '6'), ('In 7 days at', None, '7'), ('In 8 days at', None, '8'), ('In 9 days at', None, '9'), ('In 10 days at', None, '10'), ('In 11 days at', None, '11'), ('In 12 days at', None, '12'), ('In 13 days at', None, '13'), ('In 14 days at', None, '14')]


#This is a wrapper class that subclasses the discord select to aid with setup
class SelectWrapper(ui.Select):
    def __init__(self, placeholder : str, options_list : Sequence[tuple[str, str | None, str | None]], default_index : int | None = None) -> None:

        #This converts the list of tuples into a list of discord select options, allowing for the use of descriptions, alt values and a default value if desired.
        options : list[discord.SelectOption] = []
        for i in range(len(options_list)):
            label, description, value = options_list[i]
            option = discord.SelectOption(label=label, description=description)

            if value:
                option.value = value
            if i == default_index:
                option.default = True

            options.append(option)
        super().__init__(placeholder=placeholder, options=options)

        self.used = False

    #As all processing of the result if left to the parent object this merely acknowledges the interaction to prevent the interaction failed message in discord, gets the value selected and then sets the used flag to true to enable detection of a value being set.
    async def callback(self, interaction: discord.Interaction) -> Any:
        await interaction.response.defer()
        self.selected = self.values[0]
        self.used = True


#This is a generic base class for containers used within information gathering layout views, It defines the existence of both a key property, name, and key function, submit actions
class FormContainer(ui.Container):

    #The init function is purposefully left as such as this is a base class os needs the flexibility of the original class ui.Container
    def __init__(self, *children: ui.Item, accent_colour: discord.Colour | int | None = None, accent_color: discord.Colour | int | None = None, spoiler: bool = False, id: int | None = None) -> None:
        super().__init__(*children, accent_colour=accent_colour, accent_color=accent_color, spoiler=spoiler, id=id)
        #This is the form fields name which is used for accessing it's result in a dictionary
        self.name : str

    #This is called by the parent view when it needs to be submitted it returns false with a string error message when a check fails (For example the field is left blank when it is required) and true with the appropriate data type when it is successfully completed
    async def submit_action(self, interaction : discord.Interaction) -> tuple[bool, str | Any]:
        return (False, None)

#This is a subclass of FormContainer which is tailored for outputting a date-time from a number of days from now and hour and minute values
class DateTimePicker(FormContainer):
    def __init__(self, date_time_type : str) -> None:
        super().__init__()

        #This takes the select wrapper previously defined and tells it to use the constant list of day options as well as setting the placeholder text to use the type of time pass to the init of the class (Start/Finish, etc)
        #It then adds the item to an action row and then adds it to itself. This is necessary as selects can't be added to a container but action rows can
        self.day_select = SelectWrapper(f"Please Select the {date_time_type} Day", ALL_DAYS)
        self.add_item(ui.ActionRow(self.day_select))

        #This repeats the same as above but for the hours and the minutes
        self.hour_select = SelectWrapper(f"Please Select the {date_time_type} Hour", ALL_HOURS)
        self.add_item(ui.ActionRow(self.hour_select))

        self.minute_select = SelectWrapper(f"Please Select the {date_time_type} Minutes", ALL_MINUTES)
        self.add_item(ui.ActionRow(self.minute_select))

        #This creates a list of all the different select objects to enable iterating across them to retrieve their information when required
        self.selects = [self.day_select, self.hour_select, self.minute_select]

        #A pair of properties for the class itself are defined here for use within other functions
        self.date_time_type = date_time_type

        self.name = f"{date_time_type.lower()}_time"


    #This is the function that is called whenever an interaction is performed. It checks that each select has had a value assigned by checking the status of the `used` bool for each item in the list of selects
    async def interaction_check(self, interaction : discord.Interaction) -> bool:
        for select in self.selects:
            if not select.used:
                return False
        return await super().interaction_check(interaction)

    #This is the specific subclass version of the super classes submit function that is called by the parent form
    async def submit_action(self, interaction: discord.Interaction) -> tuple[bool, str | datetime]:
        #This applies the interaction check and if it fails returns the bool indicating something is wrong and then the error message to be sent to the user
        if not await self.interaction_check(interaction):
            return (False, f"Please select both a {self.date_time_type} time and date")
        else:
            #These get the selected values for the hour and minute and then converts them to int and then a python time
            submitted_hour = int(self.hour_select.selected)
            submitted_minute = int(self.minute_select.selected)
            picked_time = time(hour = submitted_hour, minute=submitted_minute)

            #This gets the number of days from now and then converts it to an absolute date
            submitted_day = int(self.day_select.selected)
            picked_date = datetime.now().date() + timedelta(days = submitted_day)

            #This combines the date and time and then makes available a variable the is the correct format for displaying in discord before returning with true to indicate that everything went okay and the selected datetime output
            self.picked_datetime = datetime.combine(picked_date,picked_time)
            self.display_datetime = f"<t:{int(self.picked_datetime.timestamp())}:R>"
            return (True, self.picked_datetime)


#This is a subclass of the form container designed to take a function which talks to the database and then returns a list of tuples of strings in the required format for SelectWrapper. The overall select returns the value for the selected item from the unique ID column
#It also takes a str that is used to fill in the placeholder and the name
class DataBaseSourcePicker(FormContainer):
    def __init__(self, db_function: Callable[[],list[tuple[str,str,str]]], placeholder_filler: str) -> None:
        super().__init__()

        #This takes the provided callable and then gets the resulting list before passing to the the select wrapper to create the required select and uses the placeholder filler converting the first letter of each word to uppercase to be consistent. It then adds the select to and action row and then the container itself
        select_list = db_function()
        self.select = SelectWrapper(f"Please Select the {placeholder_filler.title()}",select_list)
        self.add_item(ui.ActionRow(self.select))

        #This saves the placeholder filler for later and also generates the name based on that
        self.placeholder_filler = placeholder_filler
        self.name = self.placeholder_filler.replace(" ", "_").lower()

    #This checks that the select has been used when the submit action is called
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.select.used

    #This is called by the parent view when needed and checks if a value has been selected. It then returns the correct bool and value based on that
    async def submit_action(self, interaction: discord.Interaction) -> tuple[bool, str | int]:
        #This returns the error message and false to indicate an error if the interaction check fails
        if not await self.interaction_check(interaction):
            return (False, f"Please select a {self.placeholder_filler.lower()}")
        else:
            #This returns true to indicate success and the value of the id for the db item converted to an int type
            return (True, int(self.select.selected))


#This is the parent view which holds all of the other components that make up the bingo setup menu
class GameMenu(ui.LayoutView):
    #This creates a child row which will hold the submit button which is defined using a decorator above its callback
    button_row = ui.ActionRow()

    #This takes the user who triggered the setup command and adds all the other necessary objects
    def __init__(self, command_user: discord.User | discord.Member) -> None:
        #This ensures that the view wil not timeout if the user takes their time filling it out
        super().__init__(timeout=None)
        self.command_user = command_user

        #This sets up the list of form fields and says that they will all be of either the FormContainer class or a subclass
        self.form_fields : list[FormContainer] = []

        #These set up the three selects wrappers, adds them to the view and then adds them to the form fields list
        self.start_picker = DateTimePicker("Start")
        self.add_item(self.start_picker)
        self.form_fields.append(self.start_picker)

        self.finish_picker = DateTimePicker("End")
        self.add_item(self.finish_picker)
        self.form_fields.append(self.finish_picker)

        self.type_picker = DataBaseSourcePicker(get_game_types, "Game Type")
        self.add_item(self.type_picker)
        self.form_fields.append(self.type_picker)

        #This then ensures that the button row will appear at the bottom of the view
        self.remove_item(self.button_row)
        self.add_item(self.button_row)

    #This is the check that is performed to confirm that the user who is submitting the view is the one who first triggered the command
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.command_user:
            return await super().interaction_check(interaction)
        else:
            #If the check fails then a message is sent that only the person who attempted to submit the view is able to see
            logger.warning("Wrong user submitted Bingo Setup")
            await interaction.response.send_message(content="The same person who triggered the command must complete the set up form", ephemeral=True, delete_after=5.0)
            return False


    #This decorator adds the button to the action row and sets the decorated function as the callback used when it is clicked
    @button_row.button(label="Submit", style=discord.ButtonStyle.green)
    async def submit(self, interaction : discord.Interaction, button : ui.Button):
        #This sets up the format of the errors and output lists. The errors is a list of the error messages to be sent and the outputs is a dict where the keys are the names of the corresponding columns in the tables and the values are returned from the creation form
        errors : list[str] = []
        outputs : dict[str, Any]= {}
        logger.info(f"Bingo Setup submitted by {interaction.user.display_name}")

        #Ths interaction check is performed and then the submit action is function for each of the form fields is called.
        await self.interaction_check(interaction)
        for field in self.form_fields:
            result = await field.submit_action(interaction)
            #This checks is a False is returned indicating that there was an error and adds it to errors or if true adds the output to outputs using the field name as the key
            if not result[0]:
                errors.append(result[1])
            else:
                outputs[field.name] = result[1]
        #This checks if there are any errors and if so sends the error message which only the user can see detailing all the problems
        if len(errors) != 0:
            content = "\n".join(errors)
            await interaction.response.send_message(content=content, ephemeral=True, delete_after=5.0)
        else:
            #THis defers the response so that it returns successfully before calling the new game function and sending an acknowledgement message
            await interaction.response.defer(thinking=True)
            game_pin = new_game(interaction.user.id, outputs["game_type"],outputs["start_time"], outputs["end_time"])
            ack_message = f"A {outputs["game_type"]} bingo game has been created and will start at {self.start_picker.display_datetime} \n \n If you would like to join please type `/join_game {game_pin}`"
            await interaction.response.send_message(content=ack_message)


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
            self.add_item(CardRow(board.board[row.row_index()], row, self))




def start_game(game_id):
    pass



class GameSetup(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="test")
    async def test(self, ctx: commands.Context):
        pass

    @app_commands.command(name="bingo", description="Setup a server based game of Bingo to be played at an event")
    async def setup_game(self, interaction: discord.Interaction):
        user = interaction.user
        logger.info(f"Bingo Setup Started by {user.display_name}")
        await interaction.response.send_message(view=GameMenu(user))



async def setup(bot : commands.Bot):
    await bot.add_cog(GameSetup(bot))
