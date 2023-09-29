from tkcomponents.basiccomponents import ButtonListBox

from ..constants import Constants as TrackerConstants


class SchedulePicker(ButtonListBox):
    def __init__(self, board, container, new_schedule_button=False):
        def get_data__button_list_box(list_box):
            meta_button_style = {"bg": board.theme.COLOURS["accent_4"]}

            result = [{
                "value": None,
                "text": TrackerConstants.METALABEL_FORMAT.format(None),
                "style": meta_button_style
            }]

            schedules = board.state.registered_get("workout_schedules")
            for schedule_id in schedules:
                schedule_name = board.state.registered_get("workout_schedule_name", [schedule_id])
                result.append({
                    "value": schedule_id,
                    "text": (schedule_name or TrackerConstants.METALABEL_FORMAT.format(schedule_id))
                })

            if new_schedule_button:
                result.append({
                    "value": True,
                    "text": TrackerConstants.METALABEL_FORMAT.format("New"),
                    "style": meta_button_style
                })

            return result

        def on_change__button_list_box(list_box, new_value):
            if new_value is None:
                board.state.registered_set(None, "active_schedule_id")

            elif new_value is True:
                board.state.registered_set({}, "new_workout_schedule")

            else:
                schedules = board.state.registered_get("workout_schedules")
                if new_value not in schedules:
                    raise ValueError

                board.state.registered_set(new_value, "active_schedule_id")

            board.tracker.render()

        super().__init__(
            container,
            board.state.registered_get("active_schedule_id"),
            lambda: board.height_clearance,
            get_data=get_data__button_list_box,
            on_change=on_change__button_list_box,
            styles={
                "canvas": {
                    "bg": board.theme.STANDARD_STYLE_ARGS["bg"]
                },
                "button": {
                    **board.theme.STANDARD_STYLES["button"],
                    "relief": "raised"
                },
                "button_selected": {
                    "bg": board.theme.STANDARD_STYLE_ARGS["fg"],
                    "fg": board.theme.STANDARD_STYLE_ARGS["bg"],
                    "relief": "sunken"
                },
                "scrollbar": {
                    "width": 14  # <14 Will not look symmetrical
                }
            }
        )
