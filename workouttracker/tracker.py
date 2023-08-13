from managedstate import State
from managedstate.extensions import Registrar, Listeners
from tkcomponents import Component
from tkcomponents.extensions import GridHelper

import json
from random import shuffle
from logging import warning
from os import path
from typing import Optional

from .constants import Constants
from .stopwatch import Stopwatch
from .config import Config


class Tracker(Component.with_extensions(GridHelper)):
    def __init__(self, container, config=Config):
        super().__init__(container, styles={
            "frame": {"bg": config.Theme.STANDARD_STYLE_ARGS["bg"]}
        })

        self._config = config

        self._board_handler = self._config.BOARD_HANDLER_CLS(self)

        # State Initialisation
        self.state = State.with_extensions(Registrar, Listeners)()
        self._register_paths()
        self.state.add_listener(
            "set",
            lambda result, state_obj, *args, **kwargs: (
                None if state_obj.extension_data.get("registered_path_label", None) == "load_file"
                else self.try_save_state(self.state_file_path)
            )
        )  # Only save if this was not a load operation

        # Tracker temporary variables
        self.state_file_path = path.relpath(self._config.STATE_FILE_PATH)
        self.is_state_unsaved = True
        self.visible_boards = set(self._config.INITIAL_BOARDS_VISIBLE)

        is_loaded, error_msg = self.try_load_state(self.state_file_path)
        if is_loaded:
            self.is_state_unsaved = False

        # Board-specific temporary variables
        self.is_actuals_minimal = False  # Will be toggled to hide extra detail in Actuals

        self.tips = self.state.registered_get("workout_tips")
        shuffle(self.tips)
        self.tips_index = 0

        self.stopwatch = Stopwatch()
        self.stopwatch_note = ""

    @property
    def config(self):
        return self._config

    def _render(self):
        # Initialise all boards
        self.boards = {board_class(self, self._frame) for board_class in self._config.BOARDS_LIST}

        frame_stretch = self._board_handler.arrange_boards()
        self._apply_frame_stretch(**frame_stretch)

    def try_load_state(self, file_path: str) -> tuple[bool, Optional[str]]:
        """
        Attempts to load data into the application state using the provided file path.
        Returns a tuple containing first a bool indicating if the operation was successful, and second
        (if unsuccessful) a relevant string error message
        """

        error_msg_template = "Unable to load data from file: {}"

        try:
            with open(file_path, "r") as data_file:
                data = json.loads(data_file.read())

            # Version checking
            try:
                data_version = data["version"]
            except KeyError:
                error_msg = error_msg_template.format("no version number found in file data")

                warning(error_msg)
                return False, error_msg

            if data_version != Constants.DATA_VERSION:
                error_msg = error_msg_template.format(
                    f"incompatible file data version ({data_version} != {Constants.DATA_VERSION})"
                )

                warning(error_msg)
                return False, error_msg

            self.state.registered_set(data, "load_file")
            return True, None

        except FileNotFoundError as ex:
            error_msg = error_msg_template.format("could not locate data file under the provided file path")

            warning(error_msg_template.format(ex))
            return False, error_msg

        except json.decoder.JSONDecodeError as ex:
            error_msg = error_msg_template.format("could not parse file data from JSON")

            warning(error_msg_template.format(ex))
            return False, error_msg

        # Default case
        except Exception as ex:
            warning(error_msg_template.format(ex))
            return False, "Unable to load data from file."

    def try_save_state(self, file_path: str) -> tuple[bool, Optional[str]]:
        """
        Attempts to save data from the application state to a file using the provided file path.
        Returns a tuple containing first a bool indicating if the operation was successful, and second
        (if unsuccessful) a relevant string error message
        """

        error_msg_template = "Unable to save data to file: {}"

        try:
            with open(file_path, "w") as data_file:
                data_file.write(json.dumps(self.state.get()))

            self.is_state_unsaved = False
            return True, None

        # Default case
        except Exception as ex:
            warning(error_msg_template.format(ex))
            return False, "Unable to save data to file."

    def state__add_schedule(self):
        schedules = self.state.registered_get("workout_schedules")

        new_id = str(
            max(
                (int(schedule_id) for schedule_id in schedules), default=-1
            ) + 1
        )  # Gives the new schedule an ID incremented by 1 from the highest previous ID
        new_schedule = {"name": "", "schedule": {}}
        schedules[new_id] = new_schedule

        self.state.registered_set(schedules, "workout_schedules")

    def state__del_schedule(self, schedule_id):
        schedules = self.state.registered_get("workout_schedules")
        active_schedule_id = self.state.registered_get("active_schedule_id")

        del schedules[schedule_id]
        if schedule_id == active_schedule_id:
            self.state.registered_set(None, "active_schedule_id")

        self.state.registered_set(schedules, "workout_schedules")

    def state__add_workout_type(self):
        workout_types = self.state.registered_get("workout_types")

        new_id = str(
            max(
                (int(workout_type_id) for workout_type_id in workout_types), default=-1
            ) + 1
        )  # Gives the new workout type an ID incremented by 1 from the highest previous ID
        new_workout_type = {"name": "", "desc": "", "single_set_reps": 1}
        workout_types[new_id] = new_workout_type

        self.state.registered_set(workout_types, "workout_types")

    def _register_paths(self):
        self.state.register_path("load_file", [], [])  # Used to add metadata for listeners

        self.state.register_path("settings", ["settings"], [{}])
        self.state.register_path("active_schedule_id", ["settings", "active_schedule_id"], [{}, None])

        self.state.register_path("workout_tips", ["workout_tips"], [[Constants.TIP_PLACEHOLDER]])

        self.state.register_path("workout_types", ["workout_types"], [{}])
        self.state.register_path("workout_type_details", ["workout_types", Constants.PATH_DYNAMIC_KEY], [{}, {}])

        self.state.register_path("workout_schedules", ["workout_schedules"], [{}])
        self.state.register_path(
            "workout_schedule", ["workout_schedules", Constants.PATH_DYNAMIC_KEY], [{}, {}])
        self.state.register_path(
            "scheduled_sets_single_entry",
            [
                "workout_schedules",
                Constants.PATH_DYNAMIC_KEY,
                "schedule",
                Constants.PATH_DYNAMIC_KEY,
                Constants.PATH_DYNAMIC_KEY
            ],
            [{}, {}, {}, {}, 0])
        self.state.register_path(
            "completed_reps_single_entry",
            ["workout_log", Constants.PATH_DYNAMIC_KEY, Constants.PATH_DYNAMIC_KEY],
            [{}, {}, 0])

        self.state.register_path(
            "stopwatch_saved",
            ["stopwatch", "saved"],
            [{}, []])
