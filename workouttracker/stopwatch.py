from datetime import datetime, timedelta


class Stopwatch:
    def __init__(self):
        self._stored_duration = timedelta(0)

        self._current_start = None

    @property
    def elapsed(self) -> timedelta:
        return self._stored_duration + (
            (datetime.now() - self._current_start) if self._current_start else timedelta(0)
        )

    @property
    def is_running(self) -> bool:
        return bool(self._current_start)

    def start(self) -> None:
        if self.is_running:
            raise RuntimeError("timer is already running")

        self._current_start = datetime.now()

    def stop(self) -> None:
        if not self.is_running:
            raise RuntimeError("timer is already stopped")

        self._stored_duration += datetime.now() - self._current_start
        self._current_start = None

    def reset(self) -> None:
        if self.is_running:
            raise RuntimeError("timer cannot be reset while running")

        self._stored_duration = timedelta(0)
