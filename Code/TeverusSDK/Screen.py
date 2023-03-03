import msvcrt
import os
from typing import Union

import bext

from Code.TeverusSDK.Table import END_HIGHLIGHT, Table

########################################################################################
#    SCREEN CONFIGS                                                                    #
########################################################################################

SCREEN_WIDTH = 137
HALF = int((SCREEN_WIDTH - 3 - 2) / 2)
THIRD = int((SCREEN_WIDTH - (3 * 2) - 2) / 3)
GO_BACK_TEXT = "[Q] Go back    "


########################################################################################
#    ACTION                                                                            #
########################################################################################


class Action:
    def __init__(
        self,
        name=None,
        function=None,
        arguments: dict = None,
        immediate_action=False,
        go_back=False,
        shortcut: Union[bool, list] = False,
    ):
        """
        [arguments]
            * A dict where key is the name of the argument in the function, value - the actual value
            * Key and the name of the argument in the function must be identical
            * Example: {"game_title": row}
        """
        self.name = name
        self.function = function
        self.arguments = arguments
        self.immediate_action = immediate_action
        self.go_back = go_back
        self.shortcut = shortcut

    def __call__(self, *args, **kwargs):
        if self.arguments:
            self.function(**self.arguments)
        else:
            self.function()


########################################################################################
#    SCREEN                                                                            #
########################################################################################


class Screen:
    def __init__(
        self, table: Table, actions: Union[list[Action] or list[list[Action]]]
    ):
        self.table = table
        self.actions = actions

        # Set default highlight position if none was set before
        if self.table.highlight is None:
            self.table.highlight = [0, 0]

        # Clear the console
        os.system("cls")
        bext.hide()

        # Print the table
        self.table.print_table()

        # Start the infinite loop
        while True:
            # Check if there is an immediate action expected
            immediate_action = self.get_immediate_action()

            # Set action to immediate action if there is one
            if immediate_action:
                action = immediate_action

            # Get user action if no immediate action is required
            else:
                self.table.highlight, action = self.get_user_action()

            # If an action is expected, perform it
            if action:
                # Get the right action if Enter was pressed before
                action = self.get_table_action() if isinstance(action, bool) else action

                # Perform the action
                action()

                # Go back to the previous screen if this is expected
                if action.go_back:
                    break

            # Print the table with the new parameters
            self.table.print_table()

    ####################################################################################
    #   INTERNAL OPERATIONS                                                            #
    ####################################################################################
    def get_user_action(self):
        screen_specific_shortcuts = self.get_screen_specific_shortcuts()

        # Variables that will be returned
        highlight = self.table.highlight
        action = False

        # Get actual user input
        user_input = msvcrt.getch()

        # For debugging purposes only
        if user_input != b"\x00":
            ...

        # If the user chooses "Enter"
        if user_input == Key.ENTER:
            action = True

        # If the user chooses one of the movement keys
        elif user_input in MOVEMENT:
            delta = MOVEMENT[user_input]
            new_position = [c1 + c2 for c1, c2 in zip(self.table.highlight, delta)]
            if new_position in self.table.cage:
                highlight = new_position

        # If the user chooses one of the page changing keys
        elif user_input in PAGINATION.keys() and self.table.has_multiple_pages:
            delta = PAGINATION[user_input]
            go_before = delta == -1 and self.table.current_page == 1
            go_beyond = delta == 1 and self.table.current_page == self.table.max_page
            if not go_before and not go_beyond:
                self.table.current_page += delta

        elif user_input in screen_specific_shortcuts.keys():
            action = screen_specific_shortcuts[user_input]

        return highlight, action

    def get_table_action(self):
        x, y = self.table.highlight
        proper_actions = [[a] if not isinstance(a, list) else a for a in self.actions]
        proper_page = self.table.current_page - 1
        x += proper_page * self.table.max_rows
        try:
            action = proper_actions[x][y]
        except IndexError:
            action = Action(function=do_nothing)

        return action

    def get_immediate_action(self):
        immediate_actions = []
        for action in self.actions:
            action = [action] if not isinstance(action, list) else action
            for sub_action in action:
                if sub_action.immediate_action:
                    immediate_actions.append(sub_action)

        if immediate_actions:
            assert len(immediate_actions) == 1, "Too many immediate actions found!"

            return immediate_actions[0]

    def get_screen_specific_shortcuts(self):
        result = {}

        if self.table.footer:
            actions_with_shortcuts = [a for a in self.table.footer if a.shortcut]
            for action in actions_with_shortcuts:
                for key in action.shortcut:
                    result[key] = action

        return result


########################################################################################
#    INFO RELATED TO SCREEN                                                            #
########################################################################################


class Key:
    DOWN = b"P"
    UP = b"H"
    RIGHT = b"M"
    LEFT = b"K"

    ENTER = b"\r"

    Q = b"q"
    Q_RU = b"\xa9"
    Z = b"z"
    Z_RU = b"\xef"
    X = b"x"
    X_RU = b"\xe7"

    S = b"s"
    S_RU = b"\xeb"


MOVEMENT = {Key.DOWN: (1, 0), Key.UP: (-1, 0), Key.RIGHT: (0, 1), Key.LEFT: (0, -1)}
PAGINATION = {Key.Z: -1, Key.Z_RU: -1, Key.X: 1, Key.X_RU: 1}


########################################################################################
#    HELPER FUNCTIONS                                                                  #
########################################################################################


def do_nothing(*args, **kwargs):
    pass


def wait_for_key(target_key):
    key = msvcrt.getch()
    while key != target_key:
        key = msvcrt.getch()


def wait_for_enter():
    print('\n Press "Enter" to continue...')
    wait_for_key(Key.ENTER)


def show_message(
    text_message,
    color,
    border=" ",
    centered=True,
    upper=True,
    need_confirmation=True,
):
    print(color)
    print(f"{border * SCREEN_WIDTH}")
    message = text_message.upper() if upper else text_message
    text = message.center if centered else message.ljust
    print(text(SCREEN_WIDTH))
    print(f"{border * SCREEN_WIDTH}{END_HIGHLIGHT}")

    if need_confirmation:
        wait_for_enter()


########################################################################################
#    POPULAR ACTIONS                                                                   #
########################################################################################

QUIT_ACTION = Action(
    name="[Q] Quit",
    function=do_nothing,
    go_back=True,
    shortcut=[Key.Q, Key.Q_RU],
)

GO_BACK_ACTION = Action(
    name=GO_BACK_TEXT,
    function=do_nothing,
    go_back=True,
    shortcut=[Key.Q, Key.Q_RU],
)

ACTIONS_STUB = [Action(function=do_nothing)]
