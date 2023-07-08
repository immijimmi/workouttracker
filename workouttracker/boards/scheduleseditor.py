from tkcomponents.basiccomponents import StringEditor

from tkinter import Frame, Label, Button

from ..components import SchedulePicker
from ..constants import Constants as TrackerConstants
from .board import Board


class SchedulesEditor(Board):
    def __init__(self, tracker, container):
        super().__init__(tracker, container)

    @property
    def display_name(self):
        return "All Schedules"

    def _render(self):
        def get_data__string_editor(editor):
            if active_schedule_id is None:
                return ""

            return self.state.registered_get("workout_schedule", [active_schedule_id])["name"]

        def on_change__string_editor(editor, old_value):
            self.children["save_button"].configure(state="normal" if editor.is_unsaved else "disabled")

        def save_schedule_name():
            if active_schedule_id is None:
                return

            new_name = string_editor.value

            schedules = self.state.registered_get("workout_schedules")
            schedules[active_schedule_id]["name"] = new_name

            self.state.registered_set(schedules, "workout_schedules")

            self.tracker.render()

        def delete_schedule():
            if active_schedule_id is None:
                return

            self.tracker.state__del_schedule(active_schedule_id)

            self.tracker.render()

        self._apply_frame_stretch(rows=[3], columns=[1])
        self._apply_dividers(TrackerConstants.DIVIDER_SIZE, rows=[1, 3], columns=[1])

        schedule_picker = SchedulePicker(self, self._frame, new_schedule_button=True)
        schedule_picker.render().grid(row=0, column=0, rowspan=5, sticky="nswe")

        active_schedule_id = schedule_picker.current_value

        title_column_char_width = 5

        # ID Row
        id_frame = Frame(
            self._frame,
            bg=self.theme.STANDARD_STYLE_ARGS["bg"],
            **self.theme.STANDARD_STYLES["highlighted"]
        )
        id_title_label = Label(
            id_frame, text="id", width=title_column_char_width, anchor="w",
            **self.theme.STANDARD_STYLES["label"]
        )
        id_value_label = Label(
            id_frame, text=str(active_schedule_id), anchor="w", **self.theme.STANDARD_STYLES["label"]
        )

        id_title_label.grid(row=0, column=0, sticky="nswe")
        id_value_label.grid(row=0, column=1,  sticky="nswe")
        id_frame.grid(row=0, column=2, columnspan=3, sticky="nswe")

        # Name Row
        name_frame = Frame(
            self._frame,
            bg=self.theme.STANDARD_STYLE_ARGS["bg"],
            **self.theme.STANDARD_STYLES["highlighted"]
        )
        name_title_label = Label(
            name_frame, text="name", width=title_column_char_width, anchor="w",
            **self.theme.STANDARD_STYLES["label"]
        )
        string_editor = StringEditor(
            name_frame,
            get_data=get_data__string_editor,
            on_change=on_change__string_editor,
            update_interval_ms=TrackerConstants.INTERVAL__SHORT_DELAY,
            styles={
                "frame": {
                    "bg": self.theme.STANDARD_STYLE_ARGS["bg"],
                    "padx": self.theme.STANDARD_STYLE_ARGS["padx"],
                    "pady": self.theme.STANDARD_STYLE_ARGS["pady"],
                },
                "entry": {
                    "bg": TrackerConstants.COLOURS["cool_less_dark_grey"],
                    "font": self.theme.STANDARD_STYLE_ARGS["font"],
                    "insertbackground": self.theme.STANDARD_STYLE_ARGS["fg"],
                },
                "entry_unsaved": {
                    **self.theme.STANDARD_STYLES["text_unsaved"]
                },
                "entry_saved": {
                    **self.theme.STANDARD_STYLES["text_saved"]
                }
            }
        )
        self.children["string_editor"] = string_editor

        name_title_label.grid(row=0, column=0, sticky="nswe")
        string_editor.render().grid(row=0, column=1, sticky="nswe")
        name_frame.grid(row=2, column=2, columnspan=3, sticky="nswe")

        # Buttons
        save_button = Button(
            self._frame, text="Save", width=6, command=save_schedule_name,
            **self.theme.STANDARD_STYLES["button"]
        )
        self.children["save_button"] = save_button
        delete_button = Button(
            self._frame, text="Delete", width=6, command=delete_schedule,
            **self.theme.STANDARD_STYLES["button"]
        )

        save_button.grid(row=4, column=3, sticky="nswe")
        delete_button.grid(row=4, column=4, sticky="nswe")

        save_button.configure(state="disabled")
        if active_schedule_id is None:
            string_editor.children["entry"].configure(state="disabled")
            delete_button.configure(state="disabled")

        max_title_column_width = name_title_label.winfo_reqwidth()
        self._frame.grid_columnconfigure(2, minsize=max_title_column_width)
