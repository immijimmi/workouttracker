from tkcomponents import Component
from tkcomponents.extensions import GridHelper

from abc import ABC

from ..constants import Constants as TrackerConstants


class Board(Component.with_extensions(GridHelper), ABC):
    def __init__(self, tracker, container, update_interval_ms=None):
        self._tracker = tracker
        self._state = self.tracker.state
        self._theme = self.tracker.config.Theme

        board_style_args = self.theme.BOARD_STYLE_ARGS.get(
            type(self).__name__,
            self.theme.STANDARD_STYLES["board_args"]
        )

        super().__init__(container, update_interval_ms=update_interval_ms, styles={
            "frame": {
                "borderwidth": TrackerConstants.BORDERWIDTH_TINY,
                "relief": "sunken",
                "bg": board_style_args["bg"],
                "padx": TrackerConstants.PAD_SMALL,
                "pady": TrackerConstants.PAD_SMALL
            }
        })

        self.styles["board_args"] = {
            **board_style_args
        }

    @property
    def tracker(self):
        return self._tracker

    @property
    def state(self):
        return self._state

    @property
    def theme(self):
        return self._theme

    @property
    def display_name(self) -> str:
        raise NotImplementedError
