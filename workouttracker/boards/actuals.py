from tkcomponents.basiccomponents import DateStepper, NumberStepper, ToggleButton, LabelWrapper

from datetime import datetime, timedelta
from tkinter import Label
from functools import partial

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
        def get_workout_stepper_label_format(scheduled_sets):
            return "{0}" + "/{0} sets".format(scheduled_sets)

        def determine_workout_status_color(actual_sets, scheduled_sets):
            if actual_sets > scheduled_sets:
                return TrackerConstants.COLOURS["green"]
            elif actual_sets == scheduled_sets and actual_sets > 0:
                return TrackerConstants.COLOURS["blue"]
            elif actual_sets == scheduled_sets:
                return self.theme.STANDARD_STYLE_ARGS["fg"]
            elif actual_sets > 0:
                return TrackerConstants.COLOURS["yellow"]
            else:
                return TrackerConstants.COLOURS["orange"]

        def on_change__date_stepper(stepper, increment_amount):
            self._date_offset = stepper.offset
            self.render()

        def get_data__number_stepper(workout_type_id, stepper):
            working_date = (datetime.now() + timedelta(days=self._date_offset))
            working_date_key = working_date.strftime(TrackerConstants.DATE_KEY_FORMAT)
            working_date_weekday = working_date.strftime("%a")

            workout_type_details = self.state.registered_get("workout_type_details", [workout_type_id])
            workout_reps = workout_type_details["single_set_reps"]

            workout_reps_actual = self.state.registered_get(
                "completed_reps_single_entry", [working_date_key, workout_type_id])
            workout_sets_actual = int(workout_reps_actual / workout_reps)

            schedule_id = self.state.registered_get("active_schedule_id")
            workout_sets_scheduled = self.state.registered_get(
                "scheduled_sets_single_entry", [schedule_id, working_date_weekday, workout_type_id])

            stepper.text_format = get_workout_stepper_label_format(workout_sets_scheduled)
            status_color = determine_workout_status_color(workout_sets_actual, workout_sets_scheduled)

            if "label" in stepper.children:  # The first time this is run, the label will not yet be rendered
                stepper.children["label"].config(bg=status_color)

            return workout_sets_actual

        def on_change__number_stepper(workout_type_id, stepper, increment_amount):
            working_date = (datetime.now() + timedelta(days=self._date_offset))
            working_date_key = working_date.strftime(TrackerConstants.DATE_KEY_FORMAT)

            workout_type_details = self.state.registered_get("workout_type_details", [workout_type_id])
            workout_reps = workout_type_details["single_set_reps"]

            workout_reps_actual = self.state.registered_get(
                "completed_reps_single_entry", [working_date_key, workout_type_id])
            workout_sets_actual = int(workout_reps_actual / workout_reps)

            sets_actual_difference = stepper.value - workout_sets_actual
            reps_actual_difference = sets_actual_difference * workout_reps
            new_workout_reps_actual = workout_reps_actual + reps_actual_difference

            self.state.registered_set(
                new_workout_reps_actual, "completed_reps_single_entry", [working_date_key, workout_type_id])

        def get_data__label_wrapper(workout_type_id, wrapper):
            workout_type_details = self.state.registered_get("workout_type_details", [workout_type_id])
            workout_reps = workout_type_details["single_set_reps"]

            return "x{0}".format(workout_reps)

        def toggle_workout_desc(workout_type_id, toggle_button):
            if workout_type_id in self._visible_workout_descriptions:
                self._visible_workout_descriptions.remove(workout_type_id)
            else:
                self._visible_workout_descriptions.add(workout_type_id)

            self.render()

        self._apply_frame_stretch(rows=[1], columns=[4])

        row_index = 0

        date_stepper = DateStepper(
            self._frame,
            date_text_format="%a %Y/%m/%d",
            get_data=lambda stepper: self._date_offset,
            on_change=on_change__date_stepper,
            update_interval_ms=TrackerConstants.INTERVAL__SHORT_DELAY,
            styles={
                "label": {
                    **self.theme.STANDARD_STYLES["label"],
                    **self.theme.STANDARD_STYLES["highlight"],
                    "width": 36  # Extra room left to keep the size somewhat constant between dates
                },
                "button": {
                    **self.theme.STANDARD_STYLES["symbol_button"]
                }
            }
        )
        date_stepper.render().grid(row=row_index, column=0, columnspan=4, sticky="nswe")
        row_index += 1

        date_stepper_back_button_width = date_stepper.children["back_button"].winfo_reqwidth()
        date_stepper_forward_button_width = date_stepper.children["forward_button"].winfo_reqwidth()
        self._frame.grid_columnconfigure(0, minsize=date_stepper_back_button_width)
        self._frame.grid_columnconfigure(3, minsize=date_stepper_forward_button_width)

        actuals_working_date = datetime.now().date() + timedelta(days=self._date_offset)
        actuals_working_date_key = actuals_working_date.strftime(TrackerConstants.DATE_KEY_FORMAT)

        active_schedule_id = self.state.registered_get("active_schedule_id")
        workout_types = self.state.registered_get("workout_types")

        is_date_empty = True
        for current_workout_type_id in workout_types:
            workout_details = self.state.registered_get("workout_type_details", [current_workout_type_id])
            actual_reps_completed = self.state.registered_get(
                "completed_reps_single_entry",
                [actuals_working_date_key, current_workout_type_id]
            )
            scheduled_workout_sets = self.state.registered_get(
                "scheduled_sets_single_entry",
                [active_schedule_id, actuals_working_date.strftime("%a"), current_workout_type_id]
            )

            if self._date_offset != 0:  # Rendering a previous date
                if scheduled_workout_sets == 0 and actual_reps_completed == 0:
                    continue  # Ignore workout types that were not scheduled nor performed on this date
            is_date_empty = False

            current_workout_name = (
                    workout_details["name"] or
                    TrackerConstants.META_LABEL_FORMAT.format(current_workout_type_id)
            )
            current_workout_desc = workout_details["desc"]
            current_workout_reps_per_set = workout_details["single_set_reps"]

            actual_sets_completed = int(actual_reps_completed / current_workout_reps_per_set)
            workout_status_color = determine_workout_status_color(actual_sets_completed, scheduled_workout_sets)

            column_index = 1
            row_index += 1
            Label(self._frame, text=current_workout_name, anchor="w", width=30,
                  **{
                      **self.theme.STANDARD_STYLES["label"],
                      "bg": self.styles["board_args"]["bg"]
                  }).grid(row=row_index, column=column_index, sticky="nswe")

            column_index += 1

            label_wrapper = LabelWrapper(
                self._frame,
                get_data=partial(get_data__label_wrapper, current_workout_type_id),
                update_interval_ms=TrackerConstants.INTERVAL__SHORT_DELAY,
                styles={
                    "label": {
                        "anchor": "e",
                        "width": 4,
                        **self.theme.STANDARD_STYLES["label"],
                        "bg": self.styles["board_args"]["bg"]
                    },
                }
            )
            label_wrapper.render().grid(row=row_index, column=column_index, sticky="nsw")

            column_index += 3 if self._date_offset == 0 else 4
            stepper_text_format = get_workout_stepper_label_format(scheduled_workout_sets)
            number_stepper = NumberStepper(
                self._frame,
                get_data=partial(get_data__number_stepper, current_workout_type_id),
                on_change=partial(on_change__number_stepper, current_workout_type_id),
                update_interval_ms=TrackerConstants.INTERVAL__SHORT_DELAY,
                text_format=stepper_text_format,
                step_amounts=(1,) if self._date_offset == 0 else (),
                limits=(0, None),
                styles={
                    "label": {
                        **self.theme.STANDARD_STYLES["label"],
                        **self.theme.STANDARD_STYLES["highlight"],
                        "width": 10,
                        "bg": workout_status_color,
                        "fg": TrackerConstants.COLOURS["cool_dark_grey"]
                    },
                    "button": {
                        **self.theme.STANDARD_STYLES["symbol_button"]
                    }
                }
            )
            number_stepper.render().grid(row=row_index, column=column_index,
                                         columnspan=3 if self._date_offset == 0 else 1, sticky="nswe")

            column_index += 3 if self._date_offset == 0 else 2
            ToggleButton(
                self._frame,
                text_values={True: "Desc", False: "Desc"},
                on_change=partial(toggle_workout_desc, current_workout_type_id),
                styles={
                    "button": {
                        **self.theme.STANDARD_STYLES["button"],
                        "state": ("disabled" if current_workout_desc == "" else "normal")
                    }
                }
            ).render().grid(row=row_index, column=column_index, sticky="nswe")

            if current_workout_type_id in self._visible_workout_descriptions:
                row_index += 1
                Label(
                    self._frame, text=current_workout_desc,
                    **self.theme.STANDARD_STYLES["paragraph"], **self.theme.STANDARD_STYLES["highlight"],
                ).grid(row=row_index, column=0, columnspan=9, sticky="nswe")

        row_index += 1

        if not is_date_empty:
            self._apply_dividers(TrackerConstants.DIVIDER_SIZE, rows=[1], columns=[4])

            # Prevents NumberStepper labels being too thin if any description boxes are rendered
            number_stepper_label_width = number_stepper.children["label"].winfo_reqwidth()
            self._frame.grid_columnconfigure(6, minsize=number_stepper_label_width)

            if self._date_offset == 0:
                number_stepper_minus_button_width = number_stepper.children["minus_buttons"][0].winfo_reqwidth()
                number_stepper_plus_button_width = number_stepper.children["plus_buttons"][0].winfo_reqwidth()
                self._frame.grid_columnconfigure(5, minsize=number_stepper_minus_button_width)
                self._frame.grid_columnconfigure(7, minsize=number_stepper_plus_button_width)
