from tkcomponents.basiccomponents import ToggleButton, LabelWrapper, StringEditor

from tkinter import Button
from datetime import datetime, timezone

from ..constants import Constants as TrackerConstants
from .board import Board


class Timer(Board):
    def __init__(self, tracker, container):
        super().__init__(tracker, container)

    @property
    def display_name(self):
        return "Timer"

    def _render(self):
        def get_data__stopwatch_start_button(button):
            return self.tracker.stopwatch.is_running

        def on_change__stopwatch_start_button(button):
            if button.is_on:
                self.tracker.stopwatch.start()
            else:
                self.tracker.stopwatch.stop()

            self.render()

        def on_change__stopwatch_reset_button():
            self.tracker.stopwatch.reset()

            self.render()

        def get_data__stopwatch_label(label):
            return str(self.tracker.stopwatch.elapsed)

        def on_change__stopwatch_note_editor(editor, old_value):
            self.tracker.stopwatch_note = editor.value

        def on_change__stopwatch_save_button():
            stopwatch_entry = {
                "inserted_at": datetime.now(timezone.utc).isoformat(),
                "duration_s": self.tracker.stopwatch.elapsed.total_seconds(),
                "note": self.tracker.stopwatch_note
            }

            stopwatch_saved = self.state.registered_get("stopwatch_saved")
            stopwatch_saved.append(stopwatch_entry)
            self.state.registered_set(stopwatch_saved, "stopwatch_saved")

            self.tracker.stopwatch.reset()

            self.render()

        self._apply_frame_stretch(rows=[0, 5], columns=[0, 3])

        self.children["stopwatch_start_button"] = None
        self.children["stopwatch_reset_button"] = None
        self.children["stopwatch_label"] = None
        self.children["stopwatch_note_editor"] = None
        self.children["stopwatch_save_button"] = None

        stopwatch_start_button = ToggleButton(
            self._frame,
            text_values={True: "Stop", False: "Start"},
            get_data=get_data__stopwatch_start_button,
            on_change=on_change__stopwatch_start_button,
            styles={
                    "button": {
                        **self.theme.DEFAULT_STYLES["button"],
                        "width": 6
                    }
                }
        )
        stopwatch_start_button.render().grid(row=1, column=1, sticky="nswe")
        self.children["stopwatch_start_button"] = stopwatch_start_button

        stopwatch_reset_button = Button(
            self._frame,
            text="Reset",
            width=6,
            command=on_change__stopwatch_reset_button,
            state=("disabled" if self.tracker.stopwatch.is_running else "normal"),
            **self.theme.DEFAULT_STYLES["button"]
        )
        stopwatch_reset_button.grid(row=1, column=2, sticky="nswe")
        self.children["stopwatch_reset_button"] = stopwatch_reset_button

        stopwatch_label = LabelWrapper(
            self._frame,
            get_data=get_data__stopwatch_label,
            update_interval_ms=TrackerConstants.INTERVAL__TINY_DELAY,
            styles={
                "label": {
                    **self.theme.DEFAULT_STYLES["label"],
                    **self.theme.DEFAULT_STYLES["highlight"],
                    "anchor": "w"
                }
            }
        )
        stopwatch_label.render().grid(row=2, column=1, columnspan=2, sticky="nswe")
        self.children["stopwatch_label"] = stopwatch_label

        stopwatch_note_editor = StringEditor(
            self._frame,
            get_data=lambda editor: self.tracker.stopwatch_note,
            on_change=on_change__stopwatch_note_editor,
            styles={
                "frame": {
                    "bg": self.theme.DEFAULT_STYLE_ARGS["bg"],
                    "padx": self.theme.DEFAULT_STYLE_ARGS["padx"],
                    "pady": self.theme.DEFAULT_STYLE_ARGS["pady"],
                    **self.theme.DEFAULT_STYLES["highlight"]
                },
                "entry": {
                    "bg": TrackerConstants.COLOURS["cool_less_dark_grey"],
                    "font": self.theme.DEFAULT_STYLE_ARGS["font"],
                    "insertbackground": self.theme.DEFAULT_STYLE_ARGS["fg"],
                    "width": 5,
                    "fg": self.theme.DEFAULT_STYLE_ARGS["fg"]
                }
            }
        )
        stopwatch_note_editor.render().grid(row=3, column=1, sticky="nswe")
        self.children["stopwatch_note_editor"] = stopwatch_note_editor

        stopwatch_save_button = Button(
            self._frame,
            text="Save",
            width=6,
            command=on_change__stopwatch_save_button,
            state="disabled" if self.tracker.stopwatch.is_running else "normal",
            **self.theme.DEFAULT_STYLES["button"]
        )
        stopwatch_save_button.grid(row=3, column=2, sticky="nswe")
        self.children["stopwatch_save_button"] = stopwatch_save_button
