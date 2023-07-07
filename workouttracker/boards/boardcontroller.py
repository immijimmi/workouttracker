from tkcomponents.basiccomponents import ToggleButton

from tkinter import Label
from functools import partial

from ..constants import Constants as TrackerConstants
from .board import Board


class BoardController(Board):
    def __init__(self, tracker, container):
        super().__init__(tracker, container)

        self._full_view = True

    @property
    def display_name(self):
        return "Boards"

    def _render(self):
        def toggle_full_view(toggle_button):
            self._full_view = not self._full_view

            self.render()

        def toggle_board_visibility(board_class, toggle_button):
            if board_class in self.tracker.visible_boards:
                self.tracker.visible_boards.remove(board_class)
            else:
                self.tracker.visible_boards.add(board_class)

            self.tracker.render()

        self._apply_frame_stretch(rows=[0], columns=[0])

        config = self.tracker.config
        row_index = 0

        ToggleButton(
            self._frame,
            text_values={True: self.display_name, False: self.display_name},
            on_change=toggle_full_view,
            styles={
                "button": {
                    **self.theme.STANDARD_STYLES["button"],
                }
            }
        ).render().grid(row=row_index, column=0, columnspan=2, sticky="nswe")

        if self._full_view:
            other_boards = sorted(
                [board for board in self.tracker.boards if not issubclass(type(board), BoardController)],
                key=lambda board: config.BOARDS_LIST.index(type(board))
            )

            for other_board in other_boards:
                other_board_class = type(other_board)

                column_index = 0
                row_index += 1

                Label(
                    self._frame, text=other_board.display_name,
                    **self.theme.STANDARD_STYLES["label"]
                ).grid(row=row_index, column=column_index, sticky="nswe")
                column_index += 1

                board_style_args = self.theme.BOARD_STYLE_ARGS.get(
                    other_board_class.__name__,
                    self.theme.STANDARD_STYLES["board_args"]
                )
                ToggleButton(
                    self._frame,
                    get_data=partial(
                        lambda board_class, toggle_button: board_class in self.tracker.visible_boards,
                        other_board_class),
                    on_change=partial(toggle_board_visibility, other_board_class),
                    styles={
                        "button": {
                            **self.theme.STANDARD_STYLES["button"],
                            "bg": board_style_args["bg"]
                        }
                    }
                ).render().grid(row=row_index, column=column_index, sticky="nswe")
