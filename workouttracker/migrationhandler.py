from managedstate import State
from managedstate.extensions import Registrar

from .constants import Constants


class MigrationHandler:
    def __init__(self, tracker):
        self.tracker = tracker

        self.migrate_version_lookup = {
            "0.1.0": self.to_0_1_1,
            "0.1.1": self.to_0_1_2
        }

    def to_latest_version(self, state: State.with_extensions(Registrar)) -> None:
        try:
            version = state.registered_get("version")
        # Would be raised by the state object when unable to return a value for the data version
        except ValueError as ex:
            raise ValueError("no version number found in file data") from ex

        self.register_paths(state)

        while version != Constants.DATA_VERSION:
            if version not in self.migrate_version_lookup:
                raise RuntimeError(f"unable to migrate data to the latest data version (no migration found for v{version})")

            previous_version = version
            self.migrate_version_lookup[version](state)
            version = state.registered_get("version")

            if version == previous_version:  # Migration method did not update version
                raise RuntimeError(f"unable to migrate data to the latest data version (migration from v{version} failed)")

            migration_log = state.registered_get("migration_log")
            migration_log.append((previous_version, version))
            state.registered_set(migration_log, "migration_log")

    @staticmethod
    def to_0_1_1(state: State.with_extensions(Registrar)) -> None:
        # Correcting logged reps being stored with decimal points as a result of the bug fixed in commit 490d62c
        workout_log: dict = state.registered_get("workout_log")
        for date_key in workout_log:
            workout_log_date: dict = workout_log[date_key]
            for workout_type_id in workout_log_date:
                # All reps completed values should be integers
                workout_log_date[workout_type_id] = round(workout_log_date[workout_type_id])

            workout_log[date_key] = workout_log_date

        state.registered_set(workout_log, "workout_log")

        state.registered_set("0.1.1", "version")

    @staticmethod
    def to_0_1_2(state: State.with_extensions(Registrar)) -> None:
        # Removing incorrect key generated due to the bug fixed in commit 9481791
        incorrect_key = "workout_schedule"

        data = state.get()
        if incorrect_key in data:
            del data[incorrect_key]

        state.set(data)

        # Just in case the aforementioned bug set the active schedule to an invalid schedule ID
        active_schedule_id = state.registered_get("active_schedule_id")
        workout_schedules = state.registered_get("workout_schedules")

        if (active_schedule_id is not None) and (active_schedule_id not in workout_schedules):
            state.registered_set(None, "active_schedule_id")

        state.registered_set("0.1.2", "version")

    @staticmethod
    def register_paths(state: State.with_extensions(Registrar)) -> None:
        state.register_path("migration_log", ["migration_log"], [[]])
