from importlib import resources

from .boards import BoardController, File, Actuals, Schedule, WorkoutsEditor, SchedulesEditor, Timer
from .boardhandlers import ResponsiveGrid
from .constants import Constants


class Config:
    STATE_FILE_PATH = "data.json"
    # This method of resource access will locate the file relative to this project, regardless of what the cwd is
    with resources.path("workouttracker.res", "icon.ico") as path:
        ICON_FILE_PATH = path

    # All boards to be rendered. List order will be taken into account whenever displaying these boards in list form
    BOARDS_LIST = [BoardController, File, Actuals, Schedule, WorkoutsEditor, SchedulesEditor, Timer]

    INITIAL_BOARDS_VISIBLE = {BoardController}
    BOARD_HANDLER_CLS = ResponsiveGrid

    # Board handler-specific details
    BOARDS_GRID_LAYOUT = {  # Row and column must be provided. rowspan and columnspan are defaulted to 1 if not provided
        BoardController: {"row": 0, "column": 0, "rowspan": 3},
        Actuals: {"row": 0, "column": 1, "rowspan": 2, "columnspan": 7},
        Schedule: {"row": 2, "column": 1, "rowspan": 2, "columnspan": 8},
        # Tips: {"row": 4, "column": 1, "columnspan": 5},  # Tips are disabled until further notice
        File: {"row": 0, "column": 8, "rowspan": 2, "columnspan": 4},
        SchedulesEditor: {"row": 2, "column": 9, "rowspan": 2, "columnspan": 6},
        WorkoutsEditor: {"row": 4, "column": 1, "rowspan": 3, "columnspan": 12},
        Timer: {"row": 4, "column": 13, "rowspan": 3, "columnspan": 4}
    }  # Note that boards can end up truncated if not given enough rows or columns

    class Theme:
        COLOURS = {
            "disabled": "#E5E5E5",
            "pending": "#FFC760",

            # These 5 colours should form a continuous scale from 'bad' -> 'good'
            "score_0": "#FF9A60",
            "score_1": "#FFBD78",
            "score_2": "#FFD482",
            "score_3": "#DCD482",
            "score_4": "#A5E178",
        }

        STANDARD_STYLE_ARGS = {
            "fg": Constants.COLOURS["cool_off_white"],
            "bg": Constants.COLOURS["cool_dark_grey"],
            "font": Constants.FONT_NORMAL,
            "padx": Constants.PAD_SMALL,
            "pady": Constants.PAD_SMALL,
            "highlight": Constants.COLOURS["cool_less_dark_grey"]
        }

        STANDARD_STYLES = {
            "label": {
                "font": STANDARD_STYLE_ARGS["font"],
                "fg": STANDARD_STYLE_ARGS["fg"],
                "bg": STANDARD_STYLE_ARGS["bg"],
                "padx": STANDARD_STYLE_ARGS["padx"],
                "pady": STANDARD_STYLE_ARGS["pady"]
            },
            "button": {
                "font": STANDARD_STYLE_ARGS["font"],
                "fg": STANDARD_STYLE_ARGS["fg"],
                "bg": STANDARD_STYLE_ARGS["bg"],
                "padx": STANDARD_STYLE_ARGS["padx"],
            },
            "symbol_button": {
                "font": STANDARD_STYLE_ARGS["font"],
                "fg": STANDARD_STYLE_ARGS["fg"],
                "bg": STANDARD_STYLE_ARGS["bg"],
                "padx": Constants.PAD_NORMAL,
                "width": 1
            },
            "padded": {
                "padx": STANDARD_STYLE_ARGS["padx"],
                "pady": STANDARD_STYLE_ARGS["pady"]
            },
            "highlighted": {
                "relief": "raised",
                "borderwidth": Constants.BORDERWIDTH_TINY
            },
            "paragraph": {
                "font": Constants.FONT_SMALL_ITALIC,
                "fg": STANDARD_STYLE_ARGS["fg"],
                "bg": STANDARD_STYLE_ARGS["bg"]
            },
            "text_unsaved": {
                "fg": COLOURS["pending"]
            },
            "text_saved": {
                "fg": STANDARD_STYLE_ARGS["fg"],
            },
            "board_args": {
                "bg": STANDARD_STYLE_ARGS["bg"],
                "highlight": STANDARD_STYLE_ARGS["highlight"]
            }
        }

        BOARD_STYLE_ARGS = {  # The keys used here are the class names of each board
            # Meta boards
            "BoardController": {
                "bg": Constants.COLOURS["cool_dark_grey_green_tint"],
                "highlight": Constants.COLOURS["cool_less_dark_grey_green_tint"]
            },
            "File": {
                "bg": Constants.COLOURS["cool_dark_grey_green_tint"],
                "highlight": Constants.COLOURS["cool_less_dark_grey_green_tint"]
            },

            # Editor boards
            "Schedule": {
                "bg": Constants.COLOURS["cool_dark_grey_yellow_tint"],
                "highlight": Constants.COLOURS["cool_less_dark_grey_yellow_tint"]
            },
            "SchedulesEditor": {
                "bg": Constants.COLOURS["cool_dark_grey_yellow_tint"],
                "highlight": Constants.COLOURS["cool_less_dark_grey_yellow_tint"]
            },
            "WorkoutsEditor": {
                "bg": Constants.COLOURS["cool_dark_grey_yellow_tint"],
                "highlight": Constants.COLOURS["cool_less_dark_grey_yellow_tint"]
            },

            # Tracking boards
            "Actuals": {
                "bg": Constants.COLOURS["cool_dark_grey_blue_tint"],
                "highlight": Constants.COLOURS["cool_less_dark_grey_blue_tint"]
            },
            "Timer": {
                "bg": Constants.COLOURS["cool_dark_grey_blue_tint"],
                "highlight": Constants.COLOURS["cool_less_dark_grey_blue_tint"]
            }
        }
