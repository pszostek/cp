#!/usr/bin/env python

from PySide.QtGui import *
from PySide.QtCore import *
from pandas import DataFrame
import os

class NewFilterLine(QWidget):
    newFilterAdded = Signal(DataFrame, str, str, str)

    def __init__(self, parent=None):
        super(NewFilterLine, self).__init__(parent)
        policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setSizePolicy(policy)
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.listWidget = QTreeWidget(self)
        self.listWidget.setColumnCount(1)
     #   self.listWidget.setEnabled(False)
        policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.listWidget.setSizePolicy(policy)
        layout.addWidget(self.listWidget)

        self.conditionCombo = QComboBox(self)
        self.conditionCombo.insertItems(0, ["==", "<", ">", "<=", ">=", "!="])
      #  self.conditionCombo.setEnabled(False)
        layout.addWidget(self.conditionCombo)

        self.valueEdit = QLineEdit(self)
      #  self.valueEdit.setEnabled(False)
        layout.addWidget(self.valueEdit)

        self.addButton = QPushButton(self)
        self.addButton.setText("Add")
        self.addButton.setIcon(QIcon.fromTheme("list-add"))
       # self.addButton.setEnabled(False)
        layout.addWidget(self.addButton)

        self.addButton.clicked.connect(self.buttonPressed)

    def addColumns(self, data_frame_path, table_name, table_columns):
        table_item = QTreeWidgetItem(self.listWidget)
        table_item.setText(0, table_name)
        for column_name in table_columns:
            column_item = QTreeWidgetItem(table_item)
            column_item.setText(0, column_name)
            column_item.setData(0, Qt.UserRole, (data_frame_path, column_name))

    def buttonPressed(self):
        data_frame, column_name = self.listWidget.currentItem().data(0, Qt.UserRole)
        condition = self.conditionCombo.currentText()
        value = self.valueEdit.text()
        self.newFilterAdded.emit(data_frame, column_name, condition, value)

class FilterWidget(QWidget):
    newFilterAdded = Signal(tuple)

    def __init__(self, parent=None):
        """
        data_frame_dict: dictionary where keys are CSV paths
                         and values are data frame object
        """
        super(FilterWidget, self).__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.createNewFilterGroupBox())
        layout.addWidget(self.createExistingFiltersGroupBox())

    def createNewFilterGroupBox(self):
        self.newFilterToolBox = QGroupBox(self)
        layout = QHBoxLayout()
        self.newFilterToolBox.setLayout(layout)
        policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setSizePolicy(policy)
        
        self.newFilterLine = NewFilterLine(self)
        layout.addWidget(self.newFilterLine)
        self.newFilterLine.newFilterAdded.connect(self.onAddButtonPressed)


        self.newFilterToolBox.insertItem(1, self.filterTable, "Existing filters")

        return self.newFilterToolBox

    def createExistingFiltersGroupBox(self):
        self.existingFilterToolBox = QGroupBox(self)
        layout = QHBoxLayout()
        policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.filterTable = QTableWidget(0, 5, self)
        self.filterTable.setSizePolicy(policy)
        layout.addWidget(self.filterTable)
        return self.existingFilterToolBox

    def onAddButtonPressed(self, data_frame_path, column_name, condition, value):
        row = self.filterTable.rowCount()
        data_frame_name = os.path.basename(data_frame_path)
        self.filterTable.insertRow(row)
        self.filterTable.setItem(row, 0, QTableWidgetItem(data_frame_name))
        self.filterTable.setItem(row, 1, QTableWidgetItem(column_name))
        self.filterTable.setItem(row, 2, QTableWidgetItem(condition))
        self.filterTable.setItem(row, 3, QTableWidgetItem(value))
        self.newFilterAdded.emit((data_frame_path, column_name, condition, value))

    def addDataFrame(self, data_frame, table_name, table_columns):
        print("addDataFrame")
        self.newFilterLine.addColumns(data_frame_path=data_frame.path,
                                        table_name=table_name,
                                        table_columns=table_columns)
