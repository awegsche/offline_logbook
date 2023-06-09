from datetime import date, datetime, timedelta
import json
from pathlib import Path
from typing import Dict, Generator, Iterable, List, Union
from PyQt5.QtWidgets import QApplication
from api import retrieve_events
from events import events_from_folder

from mainwindow import MainWindow

def main():
    """ Create a new entry in the logbook and attach the given files. """

    #retrieve_events(from_date=datetime.now() + timedelta(weeks=-6))

    app = QApplication([])
    window = MainWindow(events_from_folder("."))
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()

