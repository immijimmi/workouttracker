from tkcomponents.basiccomponents import Alert

from datetime import datetime
from functools import partial
from os import path
from tkinter import Label, Button, StringVar
from tkinter.filedialog import askopenfilename, asksaveasfilename

from ..constants import Constants as TrackerConstants
from .board import Board


class File(Board):
    def __init__(self, tracker, container):
        super().__init__(tracker, container, update_interval_ms=TrackerConstants.INTERVAL_SHORT)

        self.active_alerts = {}

        self._file_path__var = StringVar()
        self._file_path__var.set(self.tracker.state_file_path)

    @property
    def display_name(self):
        return "File"

    def _update(self):
        self._file_path__var.set(self.tracker.state_file_path)
        self._set_path_label_style()

    def _render(self):
        def get_data__alert(message, alert):
            alert.started = self.active_alerts[message]
            return message

        def on_expire__alert(alert):
            del self.active_alerts[alert.value]
            self.render()

        def set_file_config(operation: str):
            valid_ops = op_open, op_import, op_saveas = ("Open", "Import", "Save As")

            if operation not in valid_ops:
                raise ValueError(operation)

            filetypes = (("JSON Files", "*.json"), ("All Files", "*.*"))
            if operation in (op_open, op_import):
                selected_file_path = askopenfilename(title=operation, filetypes=filetypes)
            else:
                selected_file_path = asksaveasfilename(title="Save As", filetypes=filetypes, defaultextension=".json")

            if selected_file_path == "":
                return

            selected_file_path = path.relpath(selected_file_path)
            if selected_file_path == self.tracker.state_file_path:
                return self._add_alert("Selected file is already open.")

            if operation in (op_open, op_import):
                is_success, error_msg = self.tracker.try_load_state(selected_file_path)
                if not is_success:
                    return self._add_alert(error_msg)
            else:
                is_success, error_msg = self.tracker.try_save_state(selected_file_path)
                if not is_success:
                    return self._add_alert(error_msg)

            if operation in (op_open, op_saveas):
                self.tracker.state_file_path = selected_file_path

            if operation == op_import:
                self.tracker.is_state_unsaved = True

            self.tracker.render()

        self._expire_alerts()

        self.children["file_path_label"] = None
        self.children["alerts"] = []

        self._apply_frame_stretch(
            rows=[3+len(self.active_alerts)] + ([len(self.active_alerts)] if self.active_alerts else []),
            columns=[0, 4]
        )

        row_index = -1

        for alert_message in self.active_alerts:
            row_index += 1
            alert_component = Alert(
                self._frame,
                TrackerConstants.ALERT_DURATION,
                get_data=partial(get_data__alert, alert_message),
                on_expire=on_expire__alert,
                styles={
                    "frame": {
                        "bg": self.theme.STANDARD_STYLE_ARGS["bg"],
                        **self.theme.STANDARD_STYLES["highlighted"],
                        **self.theme.STANDARD_STYLES["tinted"],
                    },
                    "inner_frame": {
                        "bg": self.theme.STANDARD_STYLE_ARGS["bg"],
                        "padx": TrackerConstants.PAD_VERY_SMALL,
                        "pady": TrackerConstants.PAD_VERY_SMALL
                    },
                    "label": {
                        **self.theme.STANDARD_STYLES["label"],
                        "font": TrackerConstants.FONT_SMALL_ITALIC,
                    },
                    "button": {
                        **self.theme.STANDARD_STYLES["symbol_button"],
                    },
                    "progress_bar": {
                        "filled_bar_frame": {"bg": self.theme.COLOURS["accent_0"]},
                        "empty_bar_frame": {"bg": self.theme.STANDARD_STYLE_ARGS["bg"]}
                    }
                }
            )
            self.children["alerts"].append(alert_component)
            alert_component.render().grid(row=row_index, column=0, columnspan=5, sticky="nswe")

        row_index += 2
        Label(
            self._frame, text="Save Location",
            **{
                **self.theme.STANDARD_STYLES["label"],
                "bg": self.styles["board"]["bg"]
            }
        ).grid(row=row_index, column=0, columnspan=5, sticky="nswe")

        row_index += 1
        path_label = Label(
            self._frame, textvariable=self._file_path__var,
            **{**self.theme.STANDARD_STYLES["label"], **self.theme.STANDARD_STYLES["highlighted"]}
        )
        self.children["file_path_label"] = path_label
        self._set_path_label_style()
        path_label.grid(row=row_index, column=0, columnspan=5, sticky="nswe")

        row_index += 2
        Button(
            self._frame, text="Open...", width=8, command=lambda: set_file_config("Open"),
            **self.theme.STANDARD_STYLES["button"]
        ).grid(row=row_index, column=1, sticky="nswe")

        Button(
            self._frame, text="Import...", width=8, command=lambda: set_file_config("Import"),
            **self.theme.STANDARD_STYLES["button"]
        ).grid(row=row_index, column=2, sticky="nswe")

        Button(
            self._frame, text="Save As...", width=8, command=lambda: set_file_config("Save As"),
            **self.theme.STANDARD_STYLES["button"]
        ).grid(row=row_index, column=3, sticky="nswe")

    def _set_path_label_style(self):
        style = self.theme.STANDARD_STYLES[
            "text_unsaved" if self.tracker.is_state_unsaved else "text_saved"
        ]

        self.children["file_path_label"].config(**style)

    def _add_alert(self, msg):
        self.active_alerts[msg] = datetime.now()
        self.render()

    def _expire_alerts(self):
        now = datetime.now()

        for alert_message, alert_start in tuple(self.active_alerts.items()):
            if (now - alert_start).total_seconds()*1000 > TrackerConstants.ALERT_DURATION:
                del self.active_alerts[alert_message]
