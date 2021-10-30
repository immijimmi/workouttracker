from abc import ABC

from ..components import Component, GridHelper
from ..constants import Constants as TrackerConstants


class Board(Component.with_extensions(GridHelper), ABC):
    def __init__(self, tracker, container, update_interval=None):
        board_specific_colours = TrackerConstants.BOARD_SPECIFIC_COLOURS.get(
            type(self).__name__,
            TrackerConstants.DEFAULT_STYLES["board_specific_colours"]
        )

        super().__init__(container, update_interval=update_interval, styles={
            "frame": {
                "borderwidth": TrackerConstants.BORDERWIDTH__TINY,
                "relief": "sunken",
                "bg": board_specific_colours["bg"],
                "padx": TrackerConstants.PAD__SMALL,
                "pady": TrackerConstants.PAD__SMALL
            }
        })

        self.styles["board_specific"] = {
            **board_specific_colours
        }

        self.tracker = tracker

        self.state = self.tracker.state

    @property
    def display_name(self) -> str:
        raise NotImplementedError

    def _apply_dividers(self, rows=(), columns=()) -> None:
        for row_index in rows:
            self._frame.grid_rowconfigure(row_index, minsize=TrackerConstants.DIVIDER_SIZE)
        for column_index in columns:
            self._frame.grid_columnconfigure(column_index, minsize=TrackerConstants.DIVIDER_SIZE)
