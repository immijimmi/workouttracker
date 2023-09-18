from tkcomponents.basiccomponents import StringEditor, NumberStepper

from tkinter import Frame, Label, Button
from functools import partial
from datetime import datetime
from math import ceil

from .board import Board
from ..constants import Constants as TrackerConstants


class WorkoutsEditor(Board):
    def __init__(self, tracker, container):
        super().__init__(tracker, container)

        self._visible_workouts = set()
        self._unsaved_components = set()

    @property
    def display_name(self):
        return "Edit Exercises"

    def _render(self):
        def save_all_workout_types_changes():
            for workout_type_id in self._visible_workouts:
                workout_id_components = self.children[workout_type_id]

                workout_type_details = self.state.registered_get("workout_type_details", [workout_type_id])

                workout_type_details["name"] = workout_id_components["name"].value
                workout_type_details["desc"] = workout_id_components["desc"].value
                workout_type_details["single_set_reps"] = workout_id_components["single_set_reps"].value

                self.state.registered_set(workout_type_details, "workout_type_details", [workout_type_id])

                if workout_id_components["current_difficulty"].is_unsaved:
                    workout_type_difficulty_log = self.state.registered_get(
                        "workout_type_difficulty_log",
                        [workout_type_id]
                    )

                    datetime_key = datetime.utcnow().strftime(TrackerConstants.DATETIME_KEY_FORMAT)
                    workout_type_difficulty_log[datetime_key] = workout_id_components["current_difficulty"].value

                    self.state.registered_set(workout_type_difficulty_log, "workout_type_difficulty_log", [workout_type_id])

            self.tracker.render()

        def new_workout_type():
            self.tracker.state__add_workout_type()
            self.tracker.render()

        def on_change_string_editor(editor, old_value):
            if editor.is_unsaved:
                self._unsaved_components.add(editor)
            else:
                if editor in self._unsaved_components:
                    self._unsaved_components.remove(editor)

            self.children["save_button"].configure(
                state="normal" if self._unsaved_components else "disabled")

        def on_change_reps_stepper(workout_type_id, stepper, increment_amount):
            workout_type_details = self.state.registered_get("workout_type_details", [workout_type_id])
            workout_type_details["single_set_reps"] = stepper.value

            self.state.registered_set(workout_type_details, "workout_type_details", [workout_type_id])

        def get_data_name(workout_type_id, editor):
            return self.state.registered_get("workout_type_details", [workout_type_id])["name"]

        def get_data_current_difficulty(workout_type_id, editor):
            result = self.state.registered_get("workout_type_current_difficulty", [workout_type_id])
            return "" if result is None else result

        def get_data_desc(workout_type_id, editor):
            return self.state.registered_get("workout_type_details", [workout_type_id])["desc"]

        def get_data_reps(workout_type_id, stepper):
            return self.state.registered_get("workout_type_details", [workout_type_id])["single_set_reps"]

        def on_click_show_workout(workout_id):
            self._visible_workouts.add(workout_id)
            self.render()

        """
        .children is reset generically rather than via individual keys,
        since this component creates children using dynamic keys
        """
        self.children.clear()

        all_workout_types = self.state.registered_get("workout_types")
        hidden_workouts = set(all_workout_types.keys()) - self._visible_workouts

        hidden_workout_button_rows = 5
        hidden_workout_button_columnspan = 2
        workout_segments = 5
        workout_columnspan = 4
        workout_title_column_width = 12
        entry_width = 14

        hidden_workouts_columns = ceil(len(hidden_workouts)/hidden_workout_button_rows)
        hidden_workouts_columnspan = hidden_workouts_columns * hidden_workout_button_columnspan
        hidden_workouts_rowspan = (workout_segments * 2) - 1
        workout_row_dividers = [x for x in range(1, workout_segments + 3, 2)]

        column_dividers = (
                ([hidden_workouts_columnspan] if hidden_workouts else []) +
                [
                    (
                            (x * (workout_columnspan + 1)) +
                            (hidden_workouts_columnspan + bool(hidden_workouts) + workout_columnspan)
                    )
                    for x in range(len(self._visible_workouts))
                ]
        )
        row_dividers = workout_row_dividers if self._visible_workouts else [1]
        frame_stretch_column_index = max(column_dividers, default=1)
        frame_stretch_row_index = [hidden_workouts_rowspan] if all_workout_types else [3]

        self._apply_frame_stretch(rows=[frame_stretch_row_index], columns=[frame_stretch_column_index])
        self._apply_dividers(TrackerConstants.DIVIDER_SIZE, rows=row_dividers, columns=column_dividers)

        if hidden_workouts:
            hidden_workouts_frame = Frame(
                self._frame,
                **{
                    "bg": self.theme.STANDARD_STYLE_ARGS["bg"],
                    **self.theme.STANDARD_STYLES["padded"],
                    **self.theme.STANDARD_STYLES["highlighted"],
                }
            )

            # Dividers for `hidden_workouts_frame`
            for divider_row_index in range(1, (min(hidden_workout_button_rows, len(hidden_workouts))*2)-2, 2):
                hidden_workouts_frame.grid_rowconfigure(divider_row_index, minsize=TrackerConstants.DIVIDER_SIZE)
            for divider_column_index in range(1, int((len(hidden_workouts)-1)/hidden_workout_button_rows)*2, 2):
                hidden_workouts_frame.grid_columnconfigure(divider_column_index, minsize=TrackerConstants.DIVIDER_SIZE)

            # Render buttons for hidden workouts
            for button_index, current_workout_type_id in enumerate(hidden_workouts):
                button_row = (button_index*2) % (hidden_workout_button_rows*2)
                button_column = int(button_index/hidden_workout_button_rows)*2

                show_workout_button = Button(
                    hidden_workouts_frame,
                    text=(
                            all_workout_types[current_workout_type_id]["name"] or
                            TrackerConstants.METALABEL_FORMAT.format(current_workout_type_id)
                    ),
                    command=partial(on_click_show_workout, current_workout_type_id),
                    **self.theme.STANDARD_STYLES["button"]
                )
                show_workout_button.grid(row=button_row, column=button_column, sticky="nswe")

            hidden_workouts_frame.grid(
                row=0, column=0,
                rowspan=hidden_workouts_rowspan, columnspan=hidden_workouts_columnspan,
                sticky="nswe"
            )

        column_index = (hidden_workouts_columnspan + 1) * bool(hidden_workouts)
        for current_workout_type_id in self._visible_workouts:
            row_index = 0

            # ID Row
            id_frame = Frame(
                self._frame,
                **{
                    "bg": self.theme.STANDARD_STYLE_ARGS["bg"],
                    **self.theme.STANDARD_STYLES["highlighted"],
                }
            )
            id_title_label = Label(
                id_frame, text="id", width=workout_title_column_width, anchor="w",
                **self.theme.STANDARD_STYLES["label"]
            )
            id_value_label = Label(
                id_frame, text=current_workout_type_id, anchor="w",
                **{
                    **self.theme.STANDARD_STYLES["label"],
                    **self.theme.STANDARD_STYLES["padded"]
                }
            )

            id_title_label.grid(row=0, column=0, sticky="nswe")
            id_value_label.grid(row=0, column=1, sticky="nswe")
            id_frame.grid(row=row_index, column=column_index, columnspan=workout_columnspan, sticky="nswe")

            row_index += 2

            # Name Row
            name_frame = Frame(
                self._frame,
                **{
                    "bg": self.theme.STANDARD_STYLE_ARGS["bg"],
                    **self.theme.STANDARD_STYLES["highlighted"]
                }
            )
            name_title_label = Label(
                name_frame, text="name", width=workout_title_column_width, anchor="w",
                **self.theme.STANDARD_STYLES["label"]
            )
            name_string_editor = StringEditor(
                name_frame,
                get_data=partial(get_data_name, current_workout_type_id),
                on_change=on_change_string_editor,
                update_interval_ms=TrackerConstants.INTERVAL_SHORT,
                styles={
                    "frame": {
                        "bg": self.theme.STANDARD_STYLE_ARGS["bg"],
                        **self.theme.STANDARD_STYLES["padded"]
                    },
                    "entry": {
                        "bg": self.theme.STANDARD_STYLE_ARGS["highlight"],
                        "font": self.theme.STANDARD_STYLE_ARGS["font"],
                        "insertbackground": self.theme.STANDARD_STYLE_ARGS["fg"],
                        "width": entry_width,
                    },
                    "entry_unsaved": {
                        **self.theme.STANDARD_STYLES["text_unsaved"]
                    },
                    "entry_saved": {
                        **self.theme.STANDARD_STYLES["text_saved"]
                    }
                }
            )
            name_title_label.grid(row=0, column=0, sticky="nswe")
            name_string_editor.render().grid(row=0, column=1, sticky="nswe")
            name_frame.grid(row=row_index, column=column_index, columnspan=workout_columnspan, sticky="nswe")

            row_index += 2

            # Current Difficulty Row
            current_difficulty_frame = Frame(
                self._frame,
                **{
                    "bg": self.theme.STANDARD_STYLE_ARGS["bg"],
                    **self.theme.STANDARD_STYLES["highlighted"]
                }
            )
            current_difficulty_title_label = Label(
                current_difficulty_frame, text="curr. wgt./diff.", width=workout_title_column_width, anchor="w",
                **self.theme.STANDARD_STYLES["label"]
            )
            current_difficulty_string_editor = StringEditor(
                current_difficulty_frame,
                get_data=partial(get_data_current_difficulty, current_workout_type_id),
                on_change=on_change_string_editor,
                update_interval_ms=TrackerConstants.INTERVAL_SHORT,
                styles={
                    "frame": {
                        "bg": self.theme.STANDARD_STYLE_ARGS["bg"],
                        **self.theme.STANDARD_STYLES["padded"]
                    },
                    "entry": {
                        "bg": self.theme.STANDARD_STYLE_ARGS["highlight"],
                        "font": self.theme.STANDARD_STYLE_ARGS["font"],
                        "insertbackground": self.theme.STANDARD_STYLE_ARGS["fg"],
                        "width": entry_width,
                    },
                    "entry_unsaved": {
                        **self.theme.STANDARD_STYLES["text_unsaved"]
                    },
                    "entry_saved": {
                        **self.theme.STANDARD_STYLES["text_saved"]
                    }
                }
            )
            current_difficulty_title_label.grid(row=0, column=0, sticky="nswe")
            current_difficulty_string_editor.render().grid(row=0, column=1, sticky="nswe")
            current_difficulty_frame.grid(row=row_index, column=column_index, columnspan=workout_columnspan, sticky="nswe")

            row_index += 2

            # Desc Row
            desc_frame = Frame(
                self._frame,
                **{
                    "bg": self.theme.STANDARD_STYLE_ARGS["bg"],
                    **self.theme.STANDARD_STYLES["highlighted"]
                }
            )
            desc_title_label = Label(
                desc_frame, text="desc.", width=workout_title_column_width, anchor="w",
                **self.theme.STANDARD_STYLES["label"]
            )
            desc_string_editor = StringEditor(
                desc_frame,
                get_data=partial(get_data_desc, current_workout_type_id),
                on_change=on_change_string_editor,
                update_interval_ms=TrackerConstants.INTERVAL_SHORT,
                styles={
                    "frame": {
                        "bg": self.theme.STANDARD_STYLE_ARGS["bg"],
                        **self.theme.STANDARD_STYLES["padded"]
                    },
                    "entry": {
                        "bg": self.theme.STANDARD_STYLE_ARGS["highlight"],
                        "font": self.theme.STANDARD_STYLE_ARGS["font"],
                        "insertbackground": self.theme.STANDARD_STYLE_ARGS["fg"],
                        "width": entry_width,
                    },
                    "entry_unsaved": {
                        **self.theme.STANDARD_STYLES["text_unsaved"]
                    },
                    "entry_saved": {
                        **self.theme.STANDARD_STYLES["text_saved"]
                    }
                }
            )
            desc_title_label.grid(row=0, column=0, sticky="nswe")
            desc_string_editor.render().grid(row=0, column=1, sticky="nswe")
            desc_frame.grid(row=row_index, column=column_index, columnspan=workout_columnspan, sticky="nswe")

            row_index += 2

            # Single Set Reps Row
            ssr_frame = Frame(
                self._frame,
                **{
                    "bg": self.theme.STANDARD_STYLE_ARGS["bg"],
                    **self.theme.STANDARD_STYLES["highlighted"]
                }
            )
            ssr_title_label = Label(
                ssr_frame, text="reps/set", width=workout_title_column_width, anchor="w",
                **self.theme.STANDARD_STYLES["label"])
            ssr_number_stepper = NumberStepper(
                ssr_frame,
                get_data=partial(get_data_reps, current_workout_type_id),
                on_change=partial(on_change_reps_stepper, current_workout_type_id),
                update_interval_ms=TrackerConstants.INTERVAL_SHORT,
                step_amounts=(1,),
                limits=(1, None),
                styles={
                    "frame": {
                        "bg": self.theme.STANDARD_STYLE_ARGS["bg"],
                        **self.theme.STANDARD_STYLES["padded"]
                    },
                    "label": {
                        **self.theme.STANDARD_STYLES["label"],
                        **self.theme.STANDARD_STYLES["highlighted"],
                        **self.theme.STANDARD_STYLES["tinted"],
                        "width": 3
                    },
                    "button": {
                        **self.theme.STANDARD_STYLES["symbol_button"]
                    }
                }
            )
            ssr_title_label.grid(row=0, column=0, sticky="nswe")
            ssr_number_stepper.render().grid(row=0, column=1, sticky="nswe")
            ssr_frame.grid(row=row_index, column=column_index, columnspan=workout_columnspan, sticky="nswe")

            self.children[current_workout_type_id] = {}
            self.children[current_workout_type_id]["name"] = name_string_editor
            self.children[current_workout_type_id]["current_difficulty"] = current_difficulty_string_editor
            self.children[current_workout_type_id]["desc"] = desc_string_editor
            self.children[current_workout_type_id]["single_set_reps"] = ssr_number_stepper

            column_index += (workout_columnspan + 1)

        new_button = Button(
            self._frame, text="New",
            command=new_workout_type, **self.theme.STANDARD_STYLES["button"])
        self.children["new_button"] = new_button
        new_button.grid(row=0, column=column_index, sticky="nswe")

        save_button_row = (hidden_workouts_rowspan-1) if all_workout_types else 2
        save_button = Button(
            self._frame, text="Save",
            command=save_all_workout_types_changes, **self.theme.STANDARD_STYLES["button"])
        self.children["save_button"] = save_button
        save_button.grid(row=save_button_row, column=column_index, sticky="nswe")
        save_button.configure(state="disabled")
