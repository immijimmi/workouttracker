from tkcomponents.basiccomponents import StringEditor, NumberStepper

from tkinter import Frame, Label, Button
from functools import partial

from .board import Board
from ..constants import Constants as TrackerConstants


class WorkoutsEditor(Board):
    def __init__(self, tracker, container):
        super().__init__(tracker, container)

        self._unsaved_components = set()

    @property
    def display_name(self):
        return "Edit Exercises"

    def _render(self):
        def save_all_workout_types_changes():
            workout_types = self.tracker.state.registered_get("workout_types")

            for workout_type_id in workout_types:
                workout_id_components = self.children[workout_type_id]

                workout_type_details = self.state.registered_get("workout_type_details", [workout_type_id])

                workout_type_details["name"] = workout_id_components["name"].value
                workout_type_details["desc"] = workout_id_components["desc"].value
                workout_type_details["single_set_reps"] = workout_id_components["single_set_reps"].value

                self.state.registered_set(workout_type_details, "workout_type_details", [workout_type_id])

            self.tracker.render()

        def new_workout_type():
            self.tracker.state__add_workout_type()

            self.tracker.render()

        def on_change__string_editor(editor, old_value):
            if editor.is_unsaved:
                self._unsaved_components.add(editor)
            else:
                if editor in self._unsaved_components:
                    self._unsaved_components.remove(editor)

            self.children["save_all_workout_types_button"].configure(
                state="normal" if self._unsaved_components else "disabled")

        def on_change__number_stepper(workout_type_id, stepper, increment_amount):
            workout_type_details = self.state.registered_get("workout_type_details", [workout_type_id])
            workout_type_details["single_set_reps"] = stepper.value

            self.state.registered_set(workout_type_details, "workout_type_details", [workout_type_id])

        def get_data__name(workout_type_id, editor):
            return self.state.registered_get("workout_type_details", [workout_type_id])["name"]

        def get_data__desc(workout_type_id, editor):
            return self.state.registered_get("workout_type_details", [workout_type_id])["desc"]

        def get_data__single_set_reps(workout_type_id, stepper):
            return self.state.registered_get("workout_type_details", [workout_type_id])["single_set_reps"]

        """
        .children is reset generically rather than via individual keys,
        since this component creates children using dynamic keys
        """
        self.children.clear()

        all_workout_types = self.tracker.state.registered_get("workout_types")

        column_dividers = [(x*4)+3 for x in range(len(all_workout_types))]
        last_divider_column_index = max(column_dividers, default=1)  # If there are none, it takes the end of the board

        self._apply_frame_stretch(rows=[7], columns=[last_divider_column_index])
        self._apply_dividers(TrackerConstants.DIVIDER_SIZE, rows=[1, 3, 5], columns=[*column_dividers])

        title_column_char_width = 8
        entry_width = 13

        value_column_styles = {
            "padx": self.theme.STANDARD_STYLE_ARGS["padx"],
            "pady": self.theme.STANDARD_STYLE_ARGS["pady"]
        }

        column_index = 0
        for current_workout_type_id in all_workout_types:
            row_index = 0

            # ID Row
            id_frame = Frame(
                self._frame,
                **{
                    "bg": self.theme.STANDARD_STYLE_ARGS["bg"],
                    **self.theme.STANDARD_STYLES["highlighted"]
                }
            )
            id_title_label = Label(
                id_frame, text="id", width=title_column_char_width, anchor="w",
                **self.theme.STANDARD_STYLES["label"]
            )
            id_value_label = Label(
                id_frame, text=current_workout_type_id, anchor="w",
                **{
                    **self.theme.STANDARD_STYLES["label"],
                    **value_column_styles
                }
            )

            id_title_label.grid(row=0, column=0, sticky="nswe")
            id_value_label.grid(row=0, column=1, sticky="nswe")
            id_frame.grid(row=row_index, column=column_index, columnspan=3, sticky="nswe")

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
                name_frame, text="name", width=title_column_char_width, anchor="w",
                **self.theme.STANDARD_STYLES["label"]
            )
            name_string_editor = StringEditor(
                name_frame,
                get_data=partial(get_data__name, current_workout_type_id),
                on_change=on_change__string_editor,
                update_interval_ms=TrackerConstants.INTERVAL__SHORT_DELAY,
                styles={
                    "frame": {
                        "bg": self.theme.STANDARD_STYLE_ARGS["bg"],
                        **value_column_styles
                    },
                    "entry": {
                        "bg": TrackerConstants.COLOURS["cool_less_dark_grey"],
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
            name_frame.grid(row=row_index, column=column_index, columnspan=3, sticky="nswe")

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
                desc_frame, text="desc", width=title_column_char_width, anchor="w",
                **self.theme.STANDARD_STYLES["label"]
            )
            desc_string_editor = StringEditor(
                desc_frame,
                get_data=partial(get_data__desc, current_workout_type_id),
                on_change=on_change__string_editor,
                update_interval_ms=TrackerConstants.INTERVAL__SHORT_DELAY,
                styles={
                    "frame": {
                        "bg": self.theme.STANDARD_STYLE_ARGS["bg"],
                        **value_column_styles
                    },
                    "entry": {
                        "bg": TrackerConstants.COLOURS["cool_less_dark_grey"],
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
            desc_frame.grid(row=row_index, column=column_index, columnspan=3, sticky="nswe")

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
                ssr_frame, text="reps/set", width=title_column_char_width, anchor="w",
                **self.theme.STANDARD_STYLES["label"])
            ssr_number_stepper = NumberStepper(
                ssr_frame,
                get_data=partial(get_data__single_set_reps, current_workout_type_id),
                on_change=partial(on_change__number_stepper, current_workout_type_id),
                update_interval_ms=TrackerConstants.INTERVAL__SHORT_DELAY,
                step_amounts=(1,),
                limits=(1, None),
                styles={
                    "frame": {
                        "bg": self.theme.STANDARD_STYLE_ARGS["bg"],
                        **value_column_styles
                    },
                    "label": {
                        **self.theme.STANDARD_STYLES["label"],
                        **self.theme.STANDARD_STYLES["highlighted"],
                        "width": 3
                    },
                    "button": {
                        **self.theme.STANDARD_STYLES["symbol_button"]
                    }
                }
            )
            ssr_title_label.grid(row=0, column=0, sticky="nswe")
            ssr_number_stepper.render().grid(row=0, column=1, sticky="nswe")
            ssr_frame.grid(row=row_index, column=column_index, columnspan=3, sticky="nswe")

            self.children[current_workout_type_id] = {}
            self.children[current_workout_type_id]["name"] = name_string_editor
            self.children[current_workout_type_id]["desc"] = desc_string_editor
            self.children[current_workout_type_id]["single_set_reps"] = ssr_number_stepper

            column_index += 4

        new_workout_type_button = Button(
            self._frame, text="New",
            command=new_workout_type, **self.theme.STANDARD_STYLES["button"])
        self.children["new_workout_type_button"] = new_workout_type_button
        new_workout_type_button.grid(row=0, column=column_index, rowspan=3, sticky="nswe")

        save_all_workout_types_button = Button(
            self._frame, text="Save",
            command=save_all_workout_types_changes, **self.theme.STANDARD_STYLES["button"])
        self.children["save_all_workout_types_button"] = save_all_workout_types_button
        save_all_workout_types_button.grid(row=4, column=column_index, rowspan=3, sticky="nswe")
        save_all_workout_types_button.configure(state="disabled")
