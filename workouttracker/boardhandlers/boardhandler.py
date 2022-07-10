from typing import Set, Dict
from abc import ABC


class BoardHandler(ABC):
    def __init__(self, tracker):
        self.tracker = tracker

    def arrange_boards(self) -> Dict[str, Set[int]]:
        """
        This function is responsible for rendering all of the boards present in self.tracker.boards,
        and may use any data exposed by self.tracker as needed to do so.
        It should then return a dict of kwargs that will be used in the Tracker object's ._apply_frame_stretch()
        """

        raise NotImplementedError
