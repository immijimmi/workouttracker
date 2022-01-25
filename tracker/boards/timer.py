from ..components import ToggleButton
from ..constants import Constants as TrackerConstants
from .board import Board


class Timer(Board):
    def __init__(self, tracker, container):
        super().__init__(tracker, container)

    @property
    def display_name(self):
        return "Timer"

    def _render(self):
        def get_data__start_button(button):
            return self.tracker.stopwatch.is_running

        def on_change__start_button(button):
            if button.is_on:
                self.tracker.stopwatch.start()
            else:
                self.tracker.stopwatch.stop()

            self.render()

        self.children["start_button"] = None

        start_button = ToggleButton(
            self._frame,
            text_values={True: "Stop", False: "Start"},
            get_data=get_data__start_button,
            on_change=on_change__start_button,
            styles={
                    "button": {
                        **TrackerConstants.DEFAULT_STYLES["button"]
                    }
                }
        )
        start_button.render().grid(row=0, column=0, sticky="nswe")
        self.children["start_button"] = start_button
