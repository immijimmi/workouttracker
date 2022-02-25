from tkinter import Tk

from .tracker import Tracker
from .constants import Constants
from .config import DefaultConfig


class App:
    def __init__(self, config=DefaultConfig):
        self._window = Tk()
        self._window.title(Constants.WINDOW_TITLE)
        self._window.iconbitmap(config.ICON_FILE_PATH)

        self._window.minsize(width=200, height=0)  # Min width so that the window remains grabbable using the cursor

        # Make the window expand to fit displayed content
        self._window.columnconfigure(0, weight=1)
        self._window.rowconfigure(0, weight=1)

        self.tracker = Tracker(self._window, config)
        self.tracker.render().grid(sticky="nswe")

        self._window.resizable(False, False)
        self._window.mainloop()
