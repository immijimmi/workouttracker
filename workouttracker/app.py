import logging
from tkinter import Tk
from os import path, makedirs
from time import gmtime
from datetime import datetime

from .tracker import Tracker
from .config import Config


class Constants:
    WINDOW_TITLE_FORMAT = "{0} - Workout Tracker"

    LOGS_DIR_PATH = "logs"
    LOGGER_NAME = "workouttracker"
    LOG_LINE_DATE_FORMAT = "%Y-%m-%dT%H.%M.%S"  # Expects a UTC datetime
    LOG_LINE_FORMAT = "%(asctime)s.%(msecs)sZ [%(name)s] %(levelname)-8s : %(message)s"
    LOG_FILENAME_FORMAT = f"{LOGGER_NAME} {LOG_LINE_DATE_FORMAT}.%fZ.log"


class App:
    def __init__(self, config=Config):
        self.logger = self.get_logger()

        try:
            self.window = Tk()
            self.window.resizable(False, False)
            self.window.minsize(width=210, height=50)  # Min width so that the window remains grabbable using the cursor
            self.window.iconbitmap(config.ICON_FILE_PATH)

            # Make the window expand to fit displayed content
            self.window.columnconfigure(0, weight=1)
            self.window.rowconfigure(0, weight=1)

            self.tracker = Tracker(
                self.window, on_file_change=self._on_file_change,
                config=config, logger=self.logger
            )
            self.tracker.render().grid(sticky="nswe")

            self.window.mainloop()

        except:
            self.logger.critical(f"A fatal exception has occurred.", exc_info=True)

        finally:
            for handler in self.logger.handlers:
                handler.close()

    def _on_file_change(self, tracker):
        file_path = tracker.state_file_path

        if file_path is None:
            filename = "Untitled"
        else:
            filename = path.basename(file_path)
        saved_str = "*" if tracker.is_state_unsaved else ""

        title = Constants.WINDOW_TITLE_FORMAT.format(f"{saved_str}{filename}")
        self.window.title(title)

    @staticmethod
    def get_logger():
        log_formatter = logging.Formatter(fmt=Constants.LOG_LINE_FORMAT, datefmt=Constants.LOG_LINE_DATE_FORMAT)
        log_formatter.converter = gmtime

        logger = logging.getLogger(Constants.LOGGER_NAME)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        makedirs(Constants.LOGS_DIR_PATH, exist_ok=True)
        log_filehandler = logging.FileHandler(
            path.join(Constants.LOGS_DIR_PATH, datetime.utcnow().strftime(Constants.LOG_FILENAME_FORMAT))
        )
        log_filehandler.setFormatter(log_formatter)
        logger.addHandler(log_filehandler)

        log_streamhandler = logging.StreamHandler()
        log_streamhandler.setFormatter(log_formatter)
        logger.addHandler(log_streamhandler)

        return logger
