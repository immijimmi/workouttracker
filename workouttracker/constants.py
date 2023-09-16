from managedstate import KeyQuery


class Constants:
    DATA_VERSION_KEY = "version"
    DATA_VERSION = "0.1.0"

    WEEKDAY_KEY_STRINGS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

    # managedstate queries
    MAX_DICT_KEY = KeyQuery(
        lambda substate: max(substate.keys())
    )

    WINDOW_MINSIZE = (255, 33)
    WINDOW_TITLE_FORMAT = "{0} - Workout Tracker"

    DATE_KEY_FORMAT = "%Y/%m/%d"
    DATETIME_KEY_FORMAT = f"{DATE_KEY_FORMAT}T%H:%M:%SZ"  # Expects a UTC datetime

    # Should be used whenever a label does not contain the same kind of information as is standard for its section
    METALABEL_FORMAT = "({0})"

    TIP_PLACEHOLDER = "You have not added any tips."

    ALERT_DURATION = 5000
    PROGRESS_BAR_WIDTH = 60

    # Padding
    PAD_TINY = 2
    PAD_VERY_SMALL = 3
    PAD_SMALL = 4
    PAD_SMALL_NORMAL = 5
    PAD_NORMAL = 6

    # Min Sizes
    DIVIDER_SIZE = 4
    WORKOUT_TYPES_SIZE = 180
    WORKOUT_SETS_ACTUALS_SIZE = 80

    # Border Sizes
    BORDERWIDTH_TINY = 1
    BORDERWIDTH_SMALL = 2
    BORDERWIDTH_NORMAL = 3

    # Font Sizes
    FONTSIZE_TINY = 9
    FONTSIZE_SMALL = 10
    FONTSIZE_NORMAL = 11

    # Fonts
    FONT_TINY = ("Bahnschrift", FONTSIZE_TINY)
    FONT_SMALL = ("Bahnschrift", FONTSIZE_SMALL)
    FONT_SMALL_ITALIC = ("Bahnschrift", FONTSIZE_SMALL, "italic")
    FONT_NORMAL = ("Bahnschrift", FONTSIZE_NORMAL)
    FONT_NORMAL_ITALIC = ("Bahnschrift", FONTSIZE_NORMAL, "italic")
    FONT_NORMAL_BOLD = ("Bahnschrift", FONTSIZE_NORMAL, "bold")

    SYMBOL_FONT = ("Bahnschrift", FONTSIZE_NORMAL)

    # Update Intervals
    INTERVAL_TINY = 20
    INTERVAL_SHORT = 500
