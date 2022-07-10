import os
import sys
sys.path.insert(0, os.path.dirname(os.getcwd()))

from tracker import App, Config


class CustomConfig(Config):
    pass


if __name__ == "__main__":
    App(config=CustomConfig)

    raise SystemExit
