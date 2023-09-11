
from logging import info
from PyQt5.QtGui import QIcon, QImage, QPixmap
from pathlib import Path
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QTextEdit, QVBoxLayout, QWidget, QScrollArea
import typing
from PyQt5 import QtCore

from events import TIMELABELFORMAT, OEvent


class QEventWidget(QWidget):
    def __init__(self, parent: typing.Optional['QWidget'] = None) -> None:
        super().__init__(parent)
        self.info_label = QLabel()
        self.textedit = QTextEdit()
        self.attachment_widget = QWidget()
        self.attachment_widget.setLayout(QHBoxLayout())
        self.open_attachments: typing.List[QPixmap] = []

        attachment_scroll = QScrollArea()
        attachment_scroll.setMaximumHeight(200)
        #attachment_scroll.setWidget(self.attachment_widget)



        central_layout = QVBoxLayout()
        central_layout.addWidget(self.info_label)
        central_layout.addWidget(self.textedit)
        #central_layout.addWidget(attachment_scroll)
        central_layout.addWidget(self.attachment_widget)

        self.setLayout(central_layout)

    def set_event(self, oevent: OEvent):
        self.textedit.setHtml(oevent.comment)
        attachment_layout = self.attachment_widget.layout()
        while attachment_layout.count() > 0:
            attachment_layout.itemAt(0).widget().setParent(None)
        atts = 0
        self.open_attachments = []
        for att in oevent.attachments:
            filename = oevent.filepath.parent / att["filename"]
            if filename.suffix == ".png":
                atts += 1
                label = ImageLabel(filename)
                self.open_attachments.append(label)
                attachment_layout.addWidget(label)

        #self.attachment_widget.setLayout(attachment_layout)
        self.info_label.setText(f"<p><b>{oevent.datetime.strftime(TIMELABELFORMAT)}</b> | {oevent.id} | {atts} attachments</p>")


class ImageLabel(QWidget):
    def __init__(self, filename: Path, parent=None) -> None:
        super().__init__(parent)
        self.image = QPixmap(str(filename))
        self.label = QIcon(self.image.scaled(200, 200,
                                          QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                          QtCore.Qt.TransformationMode.SmoothTransformation
                                         ))
        self.button = QPushButton()
        self.button.setIcon(self.label)
        self.button.setIconSize(QtCore.QSize(200, 200))
        self.image_window = None
        self.image_window_label = None
        #self.label.setScaledContents(True)
        #self.label.setPixmap(self.image.scaled(200, 200,
        #                                  QtCore.Qt.AspectRatioMode.KeepAspectRatio,
        #                                  QtCore.Qt.TransformationMode.SmoothTransformation
        #                                 ))
        #self.label.setMaximumHeight(200)
        #self.label.setMaximumWidth(200)
        self.button.clicked.connect(self.click)

        layout = QHBoxLayout()
        layout.addWidget(self.button)

        self.setLayout(layout)

    def click(self, e):
        if self.image_window is None:
            self.image_window = QWidget()
            self.image_window_label = QLabel()
            layout = QHBoxLayout()
            layout.addWidget(self.image_window_label)
            self.image_window.setLayout(layout)
            self.image_window_label.setScaledContents(True)
            self.image_window_label.setSizePolicy(
                QSizePolicy.Policy.Ignored,
                QSizePolicy.Policy.Ignored
            )
            #self.image_window_label.resize(800,600)
        self.image_window_label.setPixmap(self.image)
        self.image_window.resize(800,600)
        self.image_window.show()


