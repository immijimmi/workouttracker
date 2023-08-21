from tkinter import Tk
from os import path

from .tracker import Tracker
from .constants import Constants
from .config import Config


class App:
    def __init__(self, config=Config):
        self._window = Tk()
        self._window.resizable(False, False)
        self._window.minsize(width=200, height=0)  # Min width so that the window remains grabbable using the cursor
        self._window.iconbitmap(config.ICON_FILE_PATH)

        # Make the window expand to fit displayed content
        self._window.columnconfigure(0, weight=1)
        self._window.rowconfigure(0, weight=1)

        self.tracker = Tracker(self._window, on_file_change=self._on_file_change, config=config)
        self.tracker.render().grid(sticky="nswe")

        self._window.mainloop()

    def _on_file_change(self, tracker):
        file_path = tracker.state_file_path

        if file_path is None:
            filename = "Untitled"
        else:
            filename = path.basename(file_path)
        saved_str = "*" if tracker.is_state_unsaved else ""

        title = Constants.WINDOW_TITLE_FORMAT.format(f"{saved_str}{filename}")
        self._window.title(title)
