from importlib import resources

from .boards import BoardsController, File, Actuals, Schedule, WorkoutsEditor, SchedulesEditor, Timer
from .boardhandlers import ResponsiveGrid
from .constants import Constants


class Config:
    # This method of resource access will locate the file relative to this project, regardless of what the cwd is
    with resources.path("workouttracker.res", "icon.ico") as path:
        ICON_FILE_PATH = path

    # All boards to be rendered. List order will be taken into account whenever displaying these boards in list form
    BOARDS_LIST = [BoardsController, File, Actuals, Schedule, WorkoutsEditor, SchedulesEditor, Timer]

    INITIAL_BOARDS_VISIBLE = {BoardsController}
    BOARD_HANDLER_CLS = ResponsiveGrid

    # Board handler-specific details
    BOARDS_GRID_LAYOUT = {  # Row and column must be provided. rowspan and columnspan are defaulted to 1 if not provided
        BoardsController: {"row": 0, "column": 0, "rowspan": 3},
        Actuals: {"row": 0, "column": 1, "rowspan": 2, "columnspan": 7},
        Schedule: {"row": 2, "column": 1, "rowspan": 2, "columnspan": 8},
        # Tips: {"row": 4, "column": 1, "columnspan": 5},  ##### TODO: Tips are disabled until further notice
        File: {"row": 0, "column": 8, "rowspan": 2, "columnspan": 4},
        SchedulesEditor: {"row": 2, "column": 9, "rowspan": 2, "columnspan": 6},
        WorkoutsEditor: {"row": 4, "column": 1, "rowspan": 3, "columnspan": 12},
        Timer: {"row": 4, "column": 13, "rowspan": 3, "columnspan": 4}
    }  # Note that boards can end up truncated if not given enough rows or columns

    class Theme:
        COLOURS = {
            # These colours should form a continuous gradation
            "light_0": "#F2F2F3",
            "light_1": "#EDEDEE",
            "light_2": "#E8E8E9",

            # These colours should form a continuous gradation
            "dark_0": "#353536",
            "dark_1": "#3C3C3D",
            "dark_2": "#49494A",

            # These colours use dark_0 as a base and add a tinted hue
            "dark_red": "#332B2B",
            "dark_orange": "#332D29",
            "dark_green": "#2F332C",
            "dark_blue": "#2D2C33",

            # These 5 colours should form a continuous scale from 'bad' -> 'good'
            "score_0": "#FF975A",
            "score_1": "#FEC278",
            "score_2": "#FED87D",
            "score_3": "#B6DE7B",
            "score_4": "#96E670",

            # These colours should form a continuous gradation
            "accent_0": "#999989",
            "accent_1": "#7C7C70",
            "accent_2": "#636359",
            "accent_3": "#4C4C47",
            "accent_4": "#35352F",

            # Status colours
            "disabled": "#E8E8E9",
            "pending": "#FED87D",
        }

        STANDARD_STYLE_ARGS = {
            "fg": COLOURS["light_0"],
            "bg": COLOURS["dark_0"],
            "font": Constants.FONT_NORMAL,
            "padx": Constants.PAD_SMALL,
            "pady": Constants.PAD_SMALL,
            "highlight": COLOURS["dark_2"],
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
                "bg": COLOURS["dark_1"],
                "padx": STANDARD_STYLE_ARGS["padx"],
                "activebackground": STANDARD_STYLE_ARGS["fg"],
                "activeforeground": STANDARD_STYLE_ARGS["bg"],
                "disabledforeground": COLOURS["dark_2"],
            },
            "symbol_button": {
                "font": STANDARD_STYLE_ARGS["font"],
                "fg": STANDARD_STYLE_ARGS["fg"],
                "bg": COLOURS["accent_2"],
                "padx": Constants.PAD_NORMAL,
                "activebackground": STANDARD_STYLE_ARGS["fg"],
                "activeforeground": STANDARD_STYLE_ARGS["bg"],
                "width": 1,
                "disabledforeground": COLOURS["accent_1"],
            },
            "padded": {
                "padx": STANDARD_STYLE_ARGS["padx"],
                "pady": STANDARD_STYLE_ARGS["pady"]
            },
            "highlighted": {
                "relief": "raised",
                "borderwidth": Constants.BORDERWIDTH_TINY
            },
            "tinted": {
                "bg": COLOURS["accent_4"]
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
            "board": {
                "bg": STANDARD_STYLE_ARGS["bg"],
                "button": {
                    "bg": COLOURS["dark_1"]
                }
            }
        }

        BOARD_STYLES = {  # The keys used here are the class names of each board
            # Meta boards
            "BoardsController": {
                "bg": COLOURS["accent_4"],
                "button": {
                    "bg": COLOURS["accent_3"]
                }
            },
            "File": {
                "bg": COLOURS["accent_4"],
                "button": {
                    "bg": COLOURS["accent_3"]
                }
            },

            # Daily usage boards
            "Actuals": {
                "bg": COLOURS["accent_3"],
                "button": {
                    "bg": COLOURS["accent_2"]
                }
            },
            "Timer": {
                "bg": COLOURS["accent_3"],
                "button": {
                    "bg": COLOURS["accent_2"]
                }
            },
        }
