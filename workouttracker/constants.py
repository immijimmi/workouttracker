from managedstate.extensions import PartialQuery

from json import decoder


class Constants:
    WEEKDAY_KEY_STRINGS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

    PATH_DYNAMIC_KEY = PartialQuery(lambda key: key)

    WINDOW_MINSIZE = (255, 33)
    WINDOW_TITLE = "Workout Logger"

    DATE_KEY_FORMAT = "%Y/%m/%d"
    # Should be used whenever a label does not contain the same kind of information as is standard for its section
    META_LABEL_FORMAT = "({0})"

    TIP_PLACEHOLDER = "You have not added any tips."

    ALERT_DURATION = 3000
    PROGRESS_BAR_WIDTH = 60

    # Padding
    PAD__TINY = 2
    PAD__TINY_SMALL = 3
    PAD__SMALL = 4
    PAD__SMALL_NORMAL = 5
    PAD__NORMAL = 6

    # Min Sizes
    DIVIDER_SIZE = 4
    WORKOUT_TYPES_SIZE = 180
    WORKOUT_SETS_ACTUALS_SIZE = 80

    # Border Sizes
    BORDERWIDTH__TINY = 1
    BORDERWIDTH__SMALL = 2
    BORDERWIDTH__NORMAL = 3

    # Font Sizes
    FONTSIZE_TINY = 9
    FONTSIZE_SMALL = 10
    FONTSIZE_NORMAL = 11

    # Fonts
    NORMAL_FONT = ("Bahnschrift", FONTSIZE_NORMAL)
    SMALL_FONT = ("Bahnschrift", FONTSIZE_SMALL)
    TINY_FONT = ("Bahnschrift", FONTSIZE_TINY)
    BOLD_FONT = ("Bahnschrift", FONTSIZE_NORMAL, "bold")
    ITALICS_FONT = ("Bahnschrift", FONTSIZE_NORMAL, "italic")
    SMALL_ITALICS_FONT = ("Bahnschrift", FONTSIZE_SMALL, "italic")
    SYMBOL_FONT = ("Bahnschrift", FONTSIZE_NORMAL)

    # Update Intervals
    INTERVAL__TINY_DELAY = 20
    INTERVAL__SHORT_DELAY = 500

    # File Handling Errors
    READ_ERRORS = (FileNotFoundError, decoder.JSONDecodeError)
    WRITE_ERRORS = (OSError,)

    # Misc
    COLOURS = {
        "orange": "#FF9859",
        "yellow": "#FFD800",
        "blue": "#667FFF",
        "green": "#00B211",
        "grey": "#CCCCCC",
        "white": "#FFFFFF",
        "cool_off_white": "#FAFAFF",
        "cool_dark_grey": "#37373C",
        "cool_dark_grey_green_tint": "#333E39",  # #37373C@255 + #00B211@15
        "cool_dark_grey_blue_tint": "#3A3C4B",  # #37373C@255 + #667FFF@20
        "cool_dark_grey_yellow_tint": "#444036",  # #37373C@255 + #D1AA00@22
        "cool_dark_grey_purple_tint": "#363246",  # #37373C@255 + #3200BF@20
        "cool_dark_grey_white_tint": "#46464B",  # #37373C@255 + #FFFFFF@20
        "cool_less_dark_grey": "#46464C",
        "cool_less_dark_grey_green_tint": "#414C48",  # #46464C@255 + #00B211@15
        "cool_less_dark_grey_blue_tint": "#484A5A",  # #46464C@255 + #667FFF@20
        "cool_less_dark_grey_yellow_tint": "#514E45",  # #46464C@255 + #D1AA00@22
        "cool_less_dark_grey_purple_tint": "#444055",  # #46464C@255 + #3200BF@20
        "cool_less_dark_grey_white_tint": "#54545A",  # #46464C@255 + #FFFFFF@20
        "tk_default_grey": "#f0f0f0"
    }

    BOARD_SPECIFIC_COLOURS = {  # The keys used here are the class names of each board
        # Meta boards
        "BoardController": {
            "bg": COLOURS["cool_dark_grey_green_tint"],
            "highlight": COLOURS["cool_less_dark_grey_green_tint"]
        },
        "File": {
            "bg": COLOURS["cool_dark_grey_green_tint"],
            "highlight": COLOURS["cool_less_dark_grey_green_tint"]
        },

        # Editor boards
        "Schedule": {
            "bg": COLOURS["cool_dark_grey_yellow_tint"],
            "highlight": COLOURS["cool_less_dark_grey_yellow_tint"]
        },
        "SchedulesEditor": {
            "bg": COLOURS["cool_dark_grey_yellow_tint"],
            "highlight": COLOURS["cool_less_dark_grey_yellow_tint"]
        },
        "WorkoutsEditor": {
            "bg": COLOURS["cool_dark_grey_yellow_tint"],
            "highlight": COLOURS["cool_less_dark_grey_yellow_tint"]
        },

        # Tracking boards
        "Actuals": {
            "bg": COLOURS["cool_dark_grey_blue_tint"],
            "highlight": COLOURS["cool_less_dark_grey_blue_tint"]
        },
        "Timer": {
            "bg": COLOURS["cool_dark_grey_blue_tint"],
            "highlight": COLOURS["cool_less_dark_grey_blue_tint"]
        }
    }

    DEFAULT_STYLE_ARGS = {
        "fg": COLOURS["cool_off_white"],
        "bg": COLOURS["cool_dark_grey"],
        "font": NORMAL_FONT,
        "padx": PAD__SMALL,
        "pady": PAD__SMALL
    }

    DEFAULT_STYLES = {
        "label": {
            "font": DEFAULT_STYLE_ARGS["font"],
            "fg": DEFAULT_STYLE_ARGS["fg"],
            "bg": DEFAULT_STYLE_ARGS["bg"],
            "padx": DEFAULT_STYLE_ARGS["padx"],
            "pady": DEFAULT_STYLE_ARGS["pady"]
        },
        "button": {
            "font": DEFAULT_STYLE_ARGS["font"],
            "fg": DEFAULT_STYLE_ARGS["fg"],
            "bg": DEFAULT_STYLE_ARGS["bg"],
            "padx": DEFAULT_STYLE_ARGS["padx"],
        },
        "symbol_button": {
            "font": DEFAULT_STYLE_ARGS["font"],
            "fg": DEFAULT_STYLE_ARGS["fg"],
            "bg": DEFAULT_STYLE_ARGS["bg"],
            "padx": PAD__NORMAL,
            "width": 1
        },
        "highlight": {
            "relief": "raised",
            "borderwidth": BORDERWIDTH__TINY
        },
        "unsaved": {
            "fg": COLOURS["yellow"]
        },
        "paragraph": {
            "font": SMALL_ITALICS_FONT,
            "fg": DEFAULT_STYLE_ARGS["fg"],
            "bg": DEFAULT_STYLE_ARGS["bg"]
        },
        "board_specific_colours": {
            "bg": DEFAULT_STYLE_ARGS["bg"],
            "highlight": COLOURS["cool_less_dark_grey"]
        }
    }
