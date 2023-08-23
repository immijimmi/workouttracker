from tkcomponents.basiccomponents import ButtonListBox

from ..constants import Constants as TrackerConstants


class SchedulePicker(ButtonListBox):
    def __init__(self, board, container, new_schedule_button=False):
        def get_data__button_list_box(list_box):
            button_style_1 = {"bg": board.theme.COLOURS["accent_4"]}
            button_style_2 = {"bg": board.theme.COLOURS["accent_3"]}

            result = [{
                "value": None,
                "text": TrackerConstants.META_LABEL_FORMAT.format(None)
            }]

            schedules = board.state.registered_get("workout_schedules")
            for schedule_id in schedules:
                result.append({
                    "value": schedule_id,
                    "text": schedules[schedule_id]["name"] or TrackerConstants.META_LABEL_FORMAT.format(schedule_id),
                    "style": button_style_2 if schedules[schedule_id]["name"] else button_style_1
                })

            if new_schedule_button:
                result.append({
                    "value": True,
                    "text": TrackerConstants.META_LABEL_FORMAT.format("New")
                })

            return result

        def on_change__button_list_box(list_box, new_value):
            if new_value is None:
                board.state.registered_set(None, "active_schedule_id")

            elif new_value is True:
                board.tracker.state__add_schedule()

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
