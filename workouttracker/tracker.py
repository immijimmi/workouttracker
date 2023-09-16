from managedstate import State
from managedstate.extensions import Registrar, Listeners
from managedstate.extensions.registrar import PartialQueries
from tkcomponents import Component
from tkcomponents.extensions import GridHelper

import json
from random import shuffle
from logging import warning
from typing import Optional, Callable

from .constants import Constants
from .stopwatch import Stopwatch
from .config import Config


class Tracker(Component.with_extensions(GridHelper)):
    def __init__(
            self, container,
            on_file_change: Callable[["Tracker"], None] = (lambda tracker: None),
            config=Config
    ):
        super().__init__(container, styles={
            "frame": {"bg": config.Theme.STANDARD_STYLE_ARGS["bg"]}
        })

        self._on_file_change = on_file_change
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
        self.visible_boards = set(self._config.INITIAL_BOARDS_VISIBLE)

        self._state_file_path = None
        self._is_state_unsaved = True
        self._on_file_change(self)

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
    def state_file_path(self) -> Optional[str]:
        return self._state_file_path

    @state_file_path.setter
    def state_file_path(self, value: Optional[str]):
        if value != self._state_file_path:
            self._state_file_path = value

            self._on_file_change(self)

    @property
    def is_state_unsaved(self) -> bool:
        return self._is_state_unsaved

    @is_state_unsaved.setter
    def is_state_unsaved(self, value: bool):
        if value != self._is_state_unsaved:
            self._is_state_unsaved = value

            self._on_file_change(self)

    @property
    def config(self):
        return self._config

    def _render(self):
        # Initialise all boards
        self.boards = {board_class(self, self._frame) for board_class in self._config.BOARDS_LIST}

        frame_stretch = self._board_handler.arrange_boards()
        self._apply_frame_stretch(**frame_stretch)

    def try_load_state(self, file_path: Optional[str]) -> tuple[bool, Optional[str]]:
        """
        Attempts to load data into the application state using the provided file path.
        Returns a tuple containing first a bool indicating if the operation was successful, and second
        (if unsuccessful) a relevant string error message
        """

        error_msg_template = "Failed to load file: {}"

        if file_path is None:
            error_msg = error_msg_template.format("no file currently selected")

            return False, error_msg

        try:
            with open(file_path, "r") as data_file:
                data = json.loads(data_file.read())

            # Version checking
            try:
                data_version = data[Constants.DATA_VERSION_KEY]
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
            error_msg = error_msg_template.format("no file found at the target location")

            warning(error_msg_template.format(ex))
            return False, error_msg

        except json.decoder.JSONDecodeError as ex:
            error_msg = error_msg_template.format("unable to parse data from JSON format")

            warning(error_msg_template.format(ex))
            return False, error_msg

        # Default case
        except Exception as ex:
            warning(error_msg_template.format(ex))
            return False, "Unable to load data from file."

    def try_save_state(self, file_path: Optional[str]) -> tuple[bool, Optional[str]]:
        """
        Attempts to save data from the application state to a file using the provided file path.
        Returns a tuple containing first a bool indicating if the operation was successful, and second
        (if unsuccessful) a relevant string error message
        """

        error_msg_template = "Failed to save file: {}"

        if file_path is None:
            error_msg = error_msg_template.format("save location not set")

            return False, error_msg

        try:
            with open(file_path, "w") as data_file:
                data = self.state.get()

                # Versioning
                if Constants.DATA_VERSION_KEY not in data:
                    data[Constants.DATA_VERSION_KEY] = Constants.DATA_VERSION

                data_file.write(json.dumps(data))

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

        self.state.register_path("version", ["version"])

        self.state.register_path("settings", ["settings"], [{}])
        self.state.register_path("active_schedule_id", ["settings", "active_schedule_id"], [{}, None])

        self.state.register_path("workout_tips", ["workout_tips"], [[Constants.TIP_PLACEHOLDER]])

        self.state.register_path("workout_types", ["workout_types"], [{}])
        self.state.register_path("workout_type_details", ["workout_types", PartialQueries.KEY], [{}])
        self.state.register_path(
            "workout_type_difficulty_log",
            ["workout_types", PartialQueries.KEY, "diff_log"],
            [{}, {}, {}]
        )
        self.state.register_path(
            "workout_type_current_difficulty",
            ["workout_types", PartialQueries.KEY, "diff_log", Constants.MAX_DICT_KEY],
            [{}, {}, {}, None]
        )

        self.state.register_path("workout_schedules", ["workout_schedules"], [{}])
        self.state.register_path(
            "workout_schedule",
            ["workout_schedules", PartialQueries.KEY],
            [{}]
        )
        self.state.register_path(
            "scheduled_sets_single_entry",
            [
                "workout_schedules",
                PartialQueries.KEY,
                "schedule",
                PartialQueries.KEY,
                PartialQueries.KEY
            ],
            [{}, {}, {}, {}, 0]
        )

        self.state.register_path(
            "completed_reps_single_entry",
            ["workout_log", PartialQueries.KEY, PartialQueries.KEY],
            [{}, {}, 0]
        )

        self.state.register_path(
            "stopwatch_saved",
            ["stopwatch", "saved"],
            [{}, []]
        )
