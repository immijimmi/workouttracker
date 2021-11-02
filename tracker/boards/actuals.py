from datetime import datetime, timedelta
from tkinter import Label
from functools import partial

from ..components import DateStepper, NumberStepper, ToggleButton, LabelWrapper
from ..constants import Constants as TrackerConstants
from .board import Board


class Actuals(Board):
    def __init__(self, tracker, container):
        super().__init__(tracker, container)

        self._date_offset = 0

        self._visible_workout_descriptions = set()

    @property
    def display_name(self):
        return "Daily Goals"

    def _render(self):
        def get_workout_stepper_label_format(_workout_sets_scheduled):
            return "{0}" + "/{0} sets".format(_workout_sets_scheduled)

        def determine_workout_status_color(_workout_sets_actual, _workout_sets_scheduled):
            if _workout_sets_actual > _workout_sets_scheduled:
                return TrackerConstants.COLOURS["green"]
            elif _workout_sets_actual == _workout_sets_scheduled and _workout_sets_actual > 0:
                return TrackerConstants.COLOURS["blue"]
            elif _workout_sets_actual == _workout_sets_scheduled:
                return TrackerConstants.DEFAULT_STYLE_ARGS["fg"]
            elif _workout_sets_actual > 0:
                return TrackerConstants.COLOURS["yellow"]
            else:
                return TrackerConstants.COLOURS["orange"]

        def on_change__date_stepper(_date_stepper, increment_amount):
            self._date_offset = _date_stepper.offset
            self.render()

        def get_data__number_stepper(_workout_type_id, _number_stepper):
            _working_date = (datetime.now() + timedelta(days=self._date_offset))
            _working_date_key = _working_date.strftime(TrackerConstants.DATE_KEY_FORMAT)
            _working_date_weekday = _working_date.strftime("%a")

            _workout_type_details = self.state.registered_get("workout_type_details", [_workout_type_id])
            _workout_reps = _workout_type_details["single_set_reps"]

            _workout_reps_actual = self.state.registered_get(
                "completed_reps_single_entry", [_working_date_key, _workout_type_id])
            _workout_sets_actual = int(_workout_reps_actual / _workout_reps)

            _active_schedule_id = self.state.registered_get("active_schedule_id")
            _workout_sets_scheduled = self.state.registered_get(
                "scheduled_sets_single_entry", [_active_schedule_id, _working_date_weekday, _workout_type_id])

            _number_stepper.text_format = get_workout_stepper_label_format(_workout_sets_scheduled)
            _status_colour = determine_workout_status_color(_workout_sets_actual, _workout_sets_scheduled)

            if "label" in _number_stepper.children:  # The first time this is run, the label will not yet be rendered
                _number_stepper.children["label"].config(bg=_status_colour)

            return _workout_sets_actual

        def on_change__number_stepper(_workout_type_id, _number_stepper, increment_amount):
            _working_date = (datetime.now() + timedelta(days=self._date_offset))
            _working_date_key = _working_date.strftime(TrackerConstants.DATE_KEY_FORMAT)

            _workout_type_details = self.state.registered_get("workout_type_details", [_workout_type_id])
            _workout_reps = _workout_type_details["single_set_reps"]

            _workout_reps_actual = self.state.registered_get(
                "completed_reps_single_entry", [_working_date_key, _workout_type_id])
            _workout_sets_actual = int(_workout_reps_actual / _workout_reps)

            sets_actual_difference = _number_stepper.value - _workout_sets_actual
            reps_actual_difference = sets_actual_difference * _workout_reps
            new_workout_reps_actual = _workout_reps_actual + reps_actual_difference

            self.state.registered_set(
                new_workout_reps_actual, "completed_reps_single_entry", [_working_date_key, _workout_type_id])

        def get_data__label_wrapper(_workout_type_id, label_wrapper):
            _workout_type_details = self.state.registered_get("workout_type_details", [_workout_type_id])
            _workout_reps = _workout_type_details["single_set_reps"]

            return "x{0}".format(_workout_reps)

        def toggle_workout_desc(_workout_type_id, toggle_button):
            if _workout_type_id in self._visible_workout_descriptions:
                self._visible_workout_descriptions.remove(_workout_type_id)
            else:
                self._visible_workout_descriptions.add(_workout_type_id)

            self.render()

        self._apply_frame_stretch(rows=[1], columns=[4])

        row_index = 0

        date_stepper = DateStepper(
            self._frame,
            date_text_format="%a %Y/%m/%d",
            get_data=lambda stepper: self._date_offset,
            on_change=on_change__date_stepper,
            update_interval=TrackerConstants.INTERVAL__SHORT_DELAY,
            styles={
                "label": {
                    **TrackerConstants.DEFAULT_STYLES["label"],
                    **TrackerConstants.DEFAULT_STYLES["highlight"],
                    "width": 30  # Extra room left to keep the size somewhat constant between dates
                },
                "button": {
                    **TrackerConstants.DEFAULT_STYLES["symbol_button"]
                }
            }
        )
        date_stepper.render().grid(row=row_index, column=0, columnspan=4, sticky="nswe")
        row_index += 1

        date_stepper_back_button_width = date_stepper.children["back_button"].winfo_reqwidth()
        date_stepper_forward_button_width = date_stepper.children["forward_button"].winfo_reqwidth()
        self._frame.grid_columnconfigure(0, minsize=date_stepper_back_button_width)
        self._frame.grid_columnconfigure(3, minsize=date_stepper_forward_button_width)

        working_date = datetime.now().date() + timedelta(days=self._date_offset)
        working_date_key = working_date.strftime(TrackerConstants.DATE_KEY_FORMAT)

        active_schedule_id = self.state.registered_get("active_schedule_id")
        workout_types = self.state.registered_get("workout_types")

        is_date_empty = True
        for workout_type_id in workout_types:
            workout_type_details = self.state.registered_get("workout_type_details", [workout_type_id])
            workout_reps_actual = self.state.registered_get("completed_reps_single_entry",
                                                            [working_date_key, workout_type_id])
            workout_sets_scheduled = self.state.registered_get(
                "scheduled_sets_single_entry", [active_schedule_id, working_date.strftime("%a"), workout_type_id])

            if self._date_offset != 0:  # Rendering a previous date
                if workout_sets_scheduled == 0 and workout_reps_actual == 0:
                    continue  # Ignore workout types that were not scheduled nor performed on this date
            is_date_empty = False

            workout_name = workout_type_details["name"] or TrackerConstants.META_LABEL_FORMAT.format(workout_type_id)
            workout_desc = workout_type_details["desc"]
            workout_reps = workout_type_details["single_set_reps"]

            workout_sets_actual = int(workout_reps_actual / workout_reps)
            status_colour = determine_workout_status_color(workout_sets_actual, workout_sets_scheduled)

            column_index = 1
            row_index += 1
            Label(self._frame, text=workout_name, width=24,
                  **{
                      **TrackerConstants.DEFAULT_STYLES["label"],
                      "bg": self.styles["board_specific"]["bg"]
                  }).grid(row=row_index, column=column_index, sticky="nswe")

            column_index += 1

            workout_reps_text = "x{0}".format(workout_reps)
            label_wrapper = LabelWrapper(
                self._frame,
                get_data=partial(get_data__label_wrapper, workout_type_id),
                update_interval=TrackerConstants.INTERVAL__SHORT_DELAY,
                styles={
                    "label": {
                        "width": 4,
                        **TrackerConstants.DEFAULT_STYLES["label"],
                        "bg": self.styles["board_specific"]["bg"]
                    },
                }
            )
            label_wrapper.render().grid(row=row_index, column=column_index, sticky="nsw")

            column_index += 3 if self._date_offset == 0 else 4
            sets_actual_text_format = get_workout_stepper_label_format(workout_sets_scheduled)
            number_stepper = NumberStepper(
                self._frame,
                get_data=partial(get_data__number_stepper, workout_type_id),
                on_change=partial(on_change__number_stepper, workout_type_id),
                update_interval=TrackerConstants.INTERVAL__SHORT_DELAY,
                text_format=sets_actual_text_format,
                step_amounts=(1,) if self._date_offset == 0 else (),
                limits=(0, None),
                styles={
                    "label": {
                        **TrackerConstants.DEFAULT_STYLES["label"],
                        **TrackerConstants.DEFAULT_STYLES["highlight"],
                        "width": 10,
                        "bg": status_colour,
                        "fg": TrackerConstants.COLOURS["cool_dark_grey"]
                    },
                    "button": {
                        **TrackerConstants.DEFAULT_STYLES["symbol_button"]
                    }
                }
            )
            number_stepper.render().grid(row=row_index, column=column_index,
                                         columnspan=3 if self._date_offset == 0 else 1, sticky="nswe")

            column_index += 3 if self._date_offset == 0 else 2
            ToggleButton(
                self._frame,
                text_values={True: "Desc", False: "Desc"},
                on_change=partial(toggle_workout_desc, workout_type_id),
                styles={
                    "button": {
                        **TrackerConstants.DEFAULT_STYLES["button"],
                        "state": ("disabled" if workout_desc == "" else "normal")
                    }
                }
            ).render().grid(row=row_index, column=column_index, sticky="nswe")

            if workout_type_id in self._visible_workout_descriptions:
                row_index += 1
                Label(self._frame,
                      text=workout_desc,
                      **TrackerConstants.DEFAULT_STYLES["paragraph"], **TrackerConstants.DEFAULT_STYLES["highlight"],
                      ).grid(row=row_index, column=0, columnspan=9, sticky="nswe")

        row_index += 1

        if not is_date_empty:
            self._apply_dividers(TrackerConstants.DIVIDER_SIZE, rows=[1], columns=[4])

            # Prevents description box rendering from making the NumberStepper labels too thin
            number_stepper_label_width = number_stepper.children["label"].winfo_reqwidth()
            self._frame.grid_columnconfigure(6, minsize=number_stepper_label_width)

            if self._date_offset == 0:
                number_stepper_minus_button_width = number_stepper.children["minus_buttons"][0].winfo_reqwidth()
                number_stepper_plus_button_width = number_stepper.children["plus_buttons"][0].winfo_reqwidth()
                self._frame.grid_columnconfigure(5, minsize=number_stepper_minus_button_width)
                self._frame.grid_columnconfigure(7, minsize=number_stepper_plus_button_width)
