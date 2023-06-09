
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List

from PyQt5.QtCore import *
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import *
from api import EventDownloader, retrieve_events
from event_widget import QEventWidget

from events import DATEFORMAT, DATETIMEFORMAT, EventDay, OEvent, TIMELABELFORMAT


class MainWindow(QMainWindow):
    def __init__(self, events: Dict[int, OEvent], parent= None) -> None:
        super().__init__(parent)

        self.events: Dict[int, OEvent] = events
        self.days: Dict[date, EventDay] = {}

        mainWidget = QWidget()
        mainLayout = QVBoxLayout()
        mainWidget.setLayout(mainLayout)

        # Buttons to navigate ----------------------------------------------------------------------
        mainbuttonsWidget = QWidget()
        mainbuttonsLayout = QHBoxLayout()
        mainbuttonsWidget.setLayout(mainbuttonsLayout)

        previous_day_button = QPushButton("Prev Day")
        previous_day_button.clicked.connect(self.previous_day)
        mainbuttonsLayout.addWidget(previous_day_button)

        previous_event_button = QPushButton("Prev Event")
        previous_event_button.clicked.connect(self.previous_event)
        mainbuttonsLayout.addWidget(previous_event_button)

        next_event_button = QPushButton("Next Event")
        next_event_button.clicked.connect(self.next_event)
        mainbuttonsLayout.addWidget(next_event_button)

        next_day_button = QPushButton("Next Day")
        next_day_button.clicked.connect(self.next_day)
        mainbuttonsLayout.addWidget(next_day_button)

        # log edit (Main Widget that displays the Log entry) ---------------------------------------
        self.event_widget = QEventWidget()

        mainLayout.addWidget(mainbuttonsWidget)
        mainLayout.addWidget(self.event_widget)


        # event selection --------------------------------------------------------------------------
        self.day_combo = QComboBox()

        for id, event in self.events.items():
            eventdate = event.datetime.date()
            if eventdate not in self.days:
                self.days[eventdate] = EventDay(eventdate)
            self.days[eventdate].events.append(id)

        # don't know why the events in day end up in reverse order
        for day in self.days.values():
            day.events.reverse()

        day_keys = [(k, k.strftime(DATEFORMAT)) for k in self.days.keys()]
        day_keys.sort(key=lambda k: k[1])
        for (k,s) in day_keys:
            self.day_combo.addItem(s, self.days[k])

        self.day_combo.currentIndexChanged.connect(self.select_day)


        self.log_list = QListView()
        self.model = QStandardItemModel()

        self.log_list.setModel(self.model)
        self.log_list.selectionModel().currentChanged.connect(self.select_event)

        selection_layout = QVBoxLayout()
        selection_layout.addWidget(self.day_combo)
        selection_layout.addWidget(self.log_list)

        selectionWidget = QWidget()
        selectionWidget.setLayout(selection_layout)
        selectionWidget.setMaximumSize(150, 100000);
        selectionWidget.setSizePolicy(QSizePolicy.Policy.Maximum,
                                      QSizePolicy.Policy.Minimum)

        # central widget ---------------------------------------------------------------------------
        self.central_widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(mainWidget)

        layout.addWidget(selectionWidget)

        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)
        self.selected_page = 0


        # select one element to trigger the signals
        self.day_combo.setCurrentIndex(0)

        menu = self.menuBar()
        fileMenu = menu.addMenu("&File")
        self.retrieveEventAction = QAction("&Retrieve Events")
        fileMenu.addAction(self.retrieveEventAction)
        self.retrieveEventAction.triggered.connect(self.retrieve_events)
        self.retrievEventPopup = None
        self.retrievEventProgress: QProgressBar = None


    def next_day(self):
        cI = self.day_combo.currentIndex()
        if cI < self.day_combo.count() - 1:
            self.day_combo.setCurrentIndex(cI + 1)

    def previous_day(self):
        cI = self.day_combo.currentIndex()
        if cI > 0:
            self.day_combo.setCurrentIndex(cI - 1)

    def next_event(self):
        cI = self.log_list.currentIndex()
        if cI.row() < self.model.rowCount(cI.parent()):
            self.log_list.setCurrentIndex(self.model.index(cI.row() + 1, cI.column(), cI.parent()))

    def previous_event(self):
        cI = self.log_list.currentIndex()
        if cI.row() > 0:
            self.log_list.setCurrentIndex(self.model.index(cI.row() - 1, cI.column(), cI.parent()))

    def retrieve_events(self):
        if self.retrievEventPopup is None:
            self.retrievEventPopup = QWidget()
            self.retrievEventProgress = QProgressBar()
            self.retrievEventProgress.setMinimum(0)
            self.retrievEventProgress.setMaximum(0)
            layout = QVBoxLayout()
            layout.addWidget(self.retrievEventProgress)
            self.retrievEventPopup.setLayout(layout)

        self.retrievEventProgress.setValue(0)

        downloader = EventDownloader()

        self.retrievEventPopup.show()

        print("start for in iter")
        for progress in downloader:
            print("loop")
            self.retrievEventProgress.setValue(progress)
            self.retrievEventPopup.repaint()

    def select_day(self, index):

        self.model.clear()

        for id in self.day_combo.currentData().events:
            event = self.events[id]
            self.model.appendRow(QStandardItem(f"{id} - {event.datetime.strftime(TIMELABELFORMAT)}"))
        self.log_list.setCurrentIndex(self.model.index(0, 0))


    def select_event(self, index: QModelIndex, previous: QModelIndex):
        selected_id = self.day_combo.currentData().events[index.row()]
        selected_event = self.events[selected_id]

        self.event_widget.set_event(selected_event)


