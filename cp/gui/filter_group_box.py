#!/usr/bin/env python

from PySide.QtGui import *
from PySide.QtCore import *

class FilterLine(QWidget):
    def __init__(self, parent=None):
        super(FilterLine, self).__init__(parent)
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        self.listWidget = QListWidget()
        layout.addWidget(self.listWidget)
        
        self.conditionCombo = QComboBox()
        layout.addWidget(self.conditionCombo)

        self.valueEdit = QLineEdit()
        layout.addWidget(self.valueEdit)

class FilterGroupBox(QGroupBox):
    def __init__(self, parent=None):
        super(FilterGroupBox, self).__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(FilterLine())       
        layout.addWidget(FilterLine())
