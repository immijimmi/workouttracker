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
        self._is_only_today_editable = True

        self._visible_workout_descriptions = set()

    @property
    def display_name(self):
        return "Diary"

    def _render(self):
        def truncate_actual_sets(sets: float):
            """
            Formats actual sets values to the correct amount of decimal places, without rounding up.

            Should be used anywhere that a value for actual sets completed is calculated, to ensure that
            all actuals values used in this board are to the same precision
            """

            return float(f"{sets:.1f}")

        def get_workout_stepper_label_format(scheduled_sets):
            return "{0:g}" + "/{0} sets".format(scheduled_sets)

        def determine_workout_status_color(actual_sets, scheduled_sets):
            if actual_sets > scheduled_sets:  # Sets over-completed
                return self.theme.COLOURS["score_4"]
            elif actual_sets == scheduled_sets and actual_sets > 0:  # Sets completed
                return self.theme.COLOURS["score_3"]
            elif actual_sets == scheduled_sets:  # Sets empty
                return self.theme.COLOURS["disabled"]
            elif actual_sets > 0:  # Sets partially completed
                if actual_sets >= (scheduled_sets - 1):  # Sets partially completed, and close to completion
                    return self.theme.COLOURS["score_2"]
                else:  # Sets partially completed, but not close to completion
                    return self.theme.COLOURS["score_1"]
            else:  # Sets not completed at all
                return self.theme.COLOURS["score_0"]

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
            workout_sets_actual = truncate_actual_sets(workout_reps_actual / workout_reps)

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
                "completed_reps_single_entry", [working_date_key, workout_type_id]
            )

            increment_amount_reps = increment_amount * workout_reps
            new_workout_reps_actual = workout_reps_actual + increment_amount_reps

            self.state.registered_set(
                new_workout_reps_actual,
                "completed_reps_single_entry", [working_date_key, workout_type_id]
            )

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

        def toggle_minimal(toggle_button):
            self.tracker.is_actuals_minimal = not self.tracker.is_actuals_minimal
            self.render()

        def toggle_editing_other_dates(toggle_button):
            self._is_only_today_editable = not self._is_only_today_editable
            self.render()

        self._apply_frame_stretch(rows=[1], columns=[4])

        is_rendering_today = (self._date_offset == 0)
        is_rendering_empty_workouts = (
                (is_rendering_today and (not self.tracker.is_actuals_minimal)) or
                ((not is_rendering_today) and (not self._is_only_today_editable))
        )
        is_editable = (
            is_rendering_today or
            ((not is_rendering_today) and (not self._is_only_today_editable))
        )

        row_index = 0  # Working value to be incremented as widgets are placed

        date_stepper = DateStepper(
            self._frame,
            date_text_format="%a %Y/%m/%d",
            get_data=lambda stepper: self._date_offset,
            on_change=on_change__date_stepper,
            update_interval_ms=TrackerConstants.INTERVAL_SHORT,
            styles={
                "label": {
                    **self.theme.STANDARD_STYLES["label"],
                    **self.theme.STANDARD_STYLES["highlighted"],
                    **self.theme.STANDARD_STYLES["tinted"],
                    "width": 42  # Extra room left to keep the size somewhat constant between dates
                },
                "button": {
                    **self.theme.STANDARD_STYLES["symbol_button"]
                }
            }
        )
        date_stepper.render().grid(row=row_index, column=0, columnspan=4, sticky="nswe")

        date_stepper_back_button_width = date_stepper.children["back_button"].winfo_reqwidth()
        date_stepper_forward_button_width = date_stepper.children["forward_button"].winfo_reqwidth()
        self._frame.grid_columnconfigure(0, minsize=date_stepper_back_button_width)
        self._frame.grid_columnconfigure(3, minsize=date_stepper_forward_button_width)

        row_index += 1

        actuals_working_date = datetime.now().date() + timedelta(days=self._date_offset)
        actuals_working_date_key = actuals_working_date.strftime(TrackerConstants.DATE_KEY_FORMAT)

        active_schedule_id = self.state.registered_get("active_schedule_id")
        workout_types = self.state.registered_get("workout_types")

        rendered_workouts = 0
        empty_workouts = 0
        for current_workout_type_id in workout_types:
            workout_details = self.state.registered_get("workout_type_details", [current_workout_type_id])
            current_difficulty = self.state.registered_get("workout_type_current_difficulty", [current_workout_type_id])

            actual_reps_completed = self.state.registered_get(
                "completed_reps_single_entry",
                [actuals_working_date_key, current_workout_type_id]
            )
            scheduled_workout_sets = self.state.registered_get(
                "scheduled_sets_single_entry",
                [active_schedule_id, actuals_working_date.strftime("%a"), current_workout_type_id]
            )

            # If this workout is empty and not on today's quota
            if (scheduled_workout_sets == 0) and (actual_reps_completed == 0):
                empty_workouts += 1

                if not is_rendering_empty_workouts:
                    continue  # Do not render
            rendered_workouts += 1

            current_workout_name = (
                    workout_details["name"] or
                    TrackerConstants.METALABEL_FORMAT.format(current_workout_type_id)
            ) + (
                f" ({current_difficulty})" if current_difficulty else ""
            )
            current_workout_desc = workout_details["desc"]
            current_workout_reps_per_set = workout_details["single_set_reps"]

            actual_sets_completed = truncate_actual_sets(actual_reps_completed / current_workout_reps_per_set)
            workout_status_color = determine_workout_status_color(actual_sets_completed, scheduled_workout_sets)

            column_index = 1  # Working value to be incremented as widgets are placed
            row_index += 1

            # Workout name label
            Label(self._frame, text=current_workout_name, anchor="w", width=35,
                  **{
                      **self.theme.STANDARD_STYLES["label"],
                      "bg": self.styles["board"]["bg"]
                  }).grid(row=row_index, column=column_index, sticky="nswe")

            # Workout reps label
            column_index += 1
            label_wrapper = LabelWrapper(
                self._frame,
                get_data=partial(get_data__label_wrapper, current_workout_type_id),
                update_interval_ms=TrackerConstants.INTERVAL_SHORT,
                styles={
                    "label": {
                        "anchor": "e",
                        "width": 5,
                        **self.theme.STANDARD_STYLES["label"],
                        "bg": self.styles["board"]["bg"]
                    },
                }
            )
            label_wrapper.render().grid(row=row_index, column=column_index, sticky="nsw")

            # Workout stepper
            column_index += (3 if is_editable else 4)
            stepper_text_format = get_workout_stepper_label_format(scheduled_workout_sets)
            number_stepper = NumberStepper(
                self._frame,
                get_data=partial(get_data__number_stepper, current_workout_type_id),
                on_change=partial(on_change__number_stepper, current_workout_type_id),
                update_interval_ms=TrackerConstants.INTERVAL_SHORT,
                text_format=stepper_text_format,
                step_amounts=(1,) if is_editable else (),
                limits=(0, None),
                styles={
                    "label": {
                        **self.theme.STANDARD_STYLES["label"],
                        **self.theme.STANDARD_STYLES["highlighted"],
                        "width": 10,
                        "bg": workout_status_color,
                        "fg": self.theme.STANDARD_STYLE_ARGS["bg"]
                    },
                    "button": {
                        **self.theme.STANDARD_STYLES["symbol_button"]
                    }
                }
            )
            number_stepper.render().grid(
                row=row_index, column=column_index,
                columnspan=(3 if is_editable else 1),
                sticky="nswe"
            )

            # Description button
            column_index += (3 if is_editable else 2)
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

            # Description box
            if current_workout_type_id in self._visible_workout_descriptions:
                row_index += 1
                Label(
                    self._frame, text=current_workout_desc,
                    **self.theme.STANDARD_STYLES["paragraph"], **self.theme.STANDARD_STYLES["highlighted"],
                ).grid(row=row_index, column=0, columnspan=9, sticky="nswe")

        # Top-right button
        if is_rendering_today and empty_workouts:
            ToggleButton(
                self._frame,
                text_values={
                    True: "Show Empty Entries",
                    False: "Hide Empty Entries"
                },
                get_data=(lambda component: self.tracker.is_actuals_minimal),
                on_change=toggle_minimal,
                styles={
                    "button": {
                        **self.theme.STANDARD_STYLES["button"]
                    }
                }
            ).render().grid(row=0, column=5, columnspan=4, sticky="nswe")
        elif (not is_rendering_today) and len(workout_types):
            ToggleButton(
                self._frame,
                text_values={
                    True: "Unlock Editing",
                    False: "Lock Editing"
                },
                get_data=(lambda component: self._is_only_today_editable),
                on_change=toggle_editing_other_dates,
                styles={
                    "button": {
                        **self.theme.STANDARD_STYLES["button"]
                    }
                }
            ).render().grid(row=0, column=5, columnspan=4, sticky="nswe")

        # Final adjustments
        if rendered_workouts > 0:
            self._apply_dividers(TrackerConstants.DIVIDER_SIZE, rows=[1], columns=[4])

            # Prevents columns shrinking below the necessary width for the buttons and labels in the workouts' steppers
            # Necessary due to the way the description box Label widgets impact spacing of some columns they occupy
            number_stepper_label_width = number_stepper.children["label"].winfo_reqwidth()
            self._frame.grid_columnconfigure(6, minsize=number_stepper_label_width)
            if is_rendering_today:
                number_stepper_minus_button_width = number_stepper.children["minus_buttons"][0].winfo_reqwidth()
                number_stepper_plus_button_width = number_stepper.children["plus_buttons"][0].winfo_reqwidth()
                self._frame.grid_columnconfigure(5, minsize=number_stepper_minus_button_width)
                self._frame.grid_columnconfigure(7, minsize=number_stepper_plus_button_width)
