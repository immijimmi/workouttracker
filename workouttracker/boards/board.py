from tkcomponents import Component
from tkcomponents.extensions import GridHelper

from abc import ABC

from ..constants import Constants as TrackerConstants


class Board(Component.with_extensions(GridHelper), ABC):
    def __init__(self, tracker, container, update_interval_ms=None):
        board_specific_colours = TrackerConstants.BOARD_SPECIFIC_COLOURS.get(
            type(self).__name__,
            TrackerConstants.DEFAULT_STYLES["board_specific_colours"]
        )

        super().__init__(container, update_interval_ms=update_interval_ms, styles={
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
