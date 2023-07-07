from importlib import resources

from .boards import BoardController, File, Actuals, Schedule, WorkoutsEditor, SchedulesEditor, Timer
from .boardhandlers import ResponsiveGrid


class Config:
    STATE_FILE_PATH = "data.json"
    # This method of resource access will locate the file relative to this project, regardless of what the cwd is
    with resources.path("workouttracker.res", "icon.ico") as path:
        ICON_FILE_PATH = path

    # All boards to be rendered. List order will be taken into account whenever displaying these boards in list form
    BOARDS_LIST = [BoardController, File, Actuals, Schedule, WorkoutsEditor, SchedulesEditor, Timer]

    INITIAL_BOARDS_VISIBLE = {BoardController}
    BOARD_HANDLER_CLS = ResponsiveGrid

    # Board Handler-Specific Details
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
