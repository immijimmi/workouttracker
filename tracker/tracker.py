from managedstate import State
from managedstate.extensions import Registrar, Listeners

import json
from random import shuffle
from logging import warning
from os import path

from .components import Component, GridHelper
from .constants import Constants
from .cls import Stopwatch


class Tracker(Component.with_extensions(GridHelper)):
    def __init__(self, container, config):
        super().__init__(container, styles={
            "frame": {"bg": Constants.DEFAULT_STYLE_ARGS["bg"]}
        })

        self._config = config

        self._board_handler = self._config.BOARD_HANDLER_CLS(self)

        # Tracker temporary variables
        self.state_file_path = path.relpath(self._config.STATE_FILE_PATH)
        self.is_state_unsaved = True
        self.visible_boards = set(self._config.INITIAL_BOARDS_VISIBLE)

        # State Initialisation
        self.state = State.with_extensions(Registrar, Listeners)()
        self._register_paths()
        self.state.add_listener(
            "set",
            lambda result, state_obj, *args, **kwargs: (
                None if state_obj.extension_data.get("registered_path_label", None) == "load_file"
                else self.save_state(self.state_file_path, catch=True)
            )
        )  # Only save if this was not a load operation

        loaded = self.load_state(self.state_file_path, catch=True)
        if loaded:
            self.is_state_unsaved = False

    @property
    def config(self):
        return self._config

    def _render(self):
        # Board-specific temporary variables
        self.tips = self.state.registered_get("workout_tips")
        shuffle(self.tips)
        self.tips_index = 0

        self.stopwatch = Stopwatch()

        # Initialise all boards
        self.boards = [board_class(self, self._frame) for board_class in self._board_handler.board_classes]

        frame_stretch = self._board_handler.arrange_boards()
        self._apply_frame_stretch(**frame_stretch)

    def load_state(self, file_path, catch=False):
        try:
            with open(file_path, "r") as data_file:
                self.state.registered_set(json.loads(data_file.read()), "load_file")
            return True
        except Constants.READ_ERRORS as ex:
            if not catch:
                raise ex

            warning("Unable to load application state from file: {0}".format(ex))

    def save_state(self, file_path, catch=False):
        try:
            with open(file_path, "w") as data_file:
                data_file.write(json.dumps(self.state.get()))

            self.is_state_unsaved = False
            return True
        except Constants.WRITE_ERRORS as ex:
            if not catch:
                raise ex

            warning("Unable to save application state to file: {0}".format(ex))

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
        self.state.register("load_file", [], [])  # Used to add metadata for listeners

        self.state.register("settings", ["settings"], [{}])
        self.state.register("active_schedule_id", ["settings", "active_schedule_id"], [{}, None])

        self.state.register("workout_tips", ["workout_tips"], [[Constants.TIP_PLACEHOLDER]])

        self.state.register("workout_types", ["workout_types"], [{}])
        self.state.register("workout_type_details", ["workout_types", Constants.PATH_DYNAMIC_KEY], [{}, {}])

        self.state.register("workout_schedules", ["workout_schedules"], [{}])
        self.state.register(
            "workout_schedule", ["workout_schedules", Constants.PATH_DYNAMIC_KEY], [{}, {}])
        self.state.register(
            "scheduled_sets_single_entry",
            [
                "workout_schedules",
                Constants.PATH_DYNAMIC_KEY,
                "schedule",
                Constants.PATH_DYNAMIC_KEY,
                Constants.PATH_DYNAMIC_KEY
            ],
            [{}, {}, {}, {}, 0])
        self.state.register(
            "completed_reps_single_entry",
            ["workout_log", Constants.PATH_DYNAMIC_KEY, Constants.PATH_DYNAMIC_KEY],
            [{}, {}, 0])

        self.state.register(
            "stopwatch_saved",
            ["stopwatch", "saved"],
            [{}, []])
