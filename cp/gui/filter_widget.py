#!/usr/bin/env python

from PySide.QtGui import *
from PySide.QtCore import *
from pandas import DataFrame
from collections import namedtuple
import os

Filter = namedtuple(
    'Filter',
    "data_frame column condition value".split(' '),
    verbose=False)


class NewFilterLine(QWidget):
    newFilterAdded = Signal(DataFrame, str, str, str)

    def __init__(self, parent=None):
        super(NewFilterLine, self).__init__(parent)
        policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.setSizePolicy(policy)
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.listWidget = QTreeWidget(self)
        self.listWidget.setColumnCount(1)
        self.listWidget.header().close()
        policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.listWidget.setSizePolicy(policy)
        layout.addWidget(self.listWidget)

        self.conditionCombo = QComboBox(self)
        self.conditionCombo.insertItems(0, ["==", "<", ">", "<=", ">=", "!="])
        layout.addWidget(self.conditionCombo)

        self.valueEdit = QLineEdit(self)
        layout.addWidget(self.valueEdit)

        self.addButton = QPushButton(self)
        self.addButton.setText("Add")
        self.addButton.setIcon(QIcon.fromTheme("list-add"))
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
        data_frame, column_name = self.listWidget.currentItem().data(
            0, Qt.UserRole)
        condition = self.conditionCombo.currentText()
        value = self.valueEdit.text()
        self.newFilterAdded.emit(data_frame, column_name, condition, value)


class FilterWidget(QWidget):
    newFilterAdded = Signal()

    def __init__(self, parent=None):
        """
        data_frame_dict: dictionary where keys are CSV paths
                         and values are data frame object
        """
        super(FilterWidget, self).__init__(parent)
        layout = QHBoxLayout()
        self.setLayout(layout)
        policy = QSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding)
        self.setSizePolicy(policy)

        self.newFilterGroupBox = None
        self.newFilterLine = None
        self.existingFilterGroupBox = None
        self.filterTable = None

        layout.addWidget(self._createNewFilterGroupBox())
        layout.addWidget(self._createExistingFiltersGroupBox())
        layout.setStretch(0, 2)
        layout.setStretch(1, 3)

        ###

        self.data_frame_dict = None
        self.filters = {}  # (filter_id, Filter)
        self.filters_enabled = {}
        self.filter_indices = []
        self.cur_filter_number = 0

    def setDataFrameDict(self, data_frame_dict):
        self.data_frame_dict = data_frame_dict

    def getFilters(self):
        return [filter_ for filter_id,
                filter_ in self.filters.items() if self.filters_enabled[filter_id]]

    def addDataFrame(self, data_frame, table_name, table_columns):
        print("addDataFrame")
        self.newFilterLine.addColumns(data_frame_path=data_frame.path,
                                      table_name=table_name,
                                      table_columns=table_columns)

    def _createNewFilterGroupBox(self):
        self.newFilterGroupBox = QGroupBox("New filter", self)
        self.newFilterGroupBox.setStyleSheet(self._getGroupBoxStyleSheet())
        policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.newFilterGroupBox.setSizePolicy(policy)

        layout = QHBoxLayout()
        self.newFilterGroupBox.setLayout(layout)

        self.newFilterLine = NewFilterLine(self)
        layout.addWidget(self.newFilterLine)
        self.newFilterLine.newFilterAdded.connect(self._onAddButtonPressed)
        return self.newFilterGroupBox

    def _createExistingFiltersGroupBox(self):
        self.existingFilterGroupBox = QGroupBox("Existing filters", self)
        self.existingFilterGroupBox.setStyleSheet(
            self._getGroupBoxStyleSheet())
        layout = QHBoxLayout()
        self.existingFilterGroupBox.setLayout(layout)

        self.filterTable = QTableWidget(0, 6, self)
        self.filterTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.filterTable.setSizePolicy(policy)
        self.filterTable.setHorizontalHeaderLabels(
            ["Data source", "Column", "Condition", "Value", "Enabled", ""])
        layout.addWidget(self.filterTable)
        return self.existingFilterGroupBox

    def _onAddButtonPressed(
            self, data_frame_path, column_name, condition, value):
        from functools import partial
        row = self.filterTable.rowCount()
        data_frame_name = os.path.basename(data_frame_path)
        self.filterTable.insertRow(row)
        self.filterTable.setItem(row, 0, QTableWidgetItem(data_frame_name))
        self.filterTable.setItem(row, 1, QTableWidgetItem(column_name))
        self.filterTable.setItem(row, 2, QTableWidgetItem(condition))
        self.filterTable.setItem(row, 3, QTableWidgetItem(value))

        enabledCheckBox = QCheckBox()
        enabledCheckBox.setCheckState(Qt.Checked)
        enabledCheckBox.stateChanged.connect(
            partial(
                self._onFilterCheckBoxChanged,
                self.cur_filter_number))
        self.filterTable.setItem(row, 4, QTableWidgetItem())
        self.filterTable.setCellWidget(row, 4, enabledCheckBox)

        deleteButton = QPushButton("Remove")
        deleteButton.setIcon(QIcon.fromTheme("list-remove"))
        deleteButton.clicked.connect(
            partial(
                self._onDeleteButtonPressed,
                self.cur_filter_number))
        self.filterTable.setItem(row, 5, QTableWidgetItem())
        self.filterTable.setCellWidget(row, 5, deleteButton)
        self.filterTable.resizeColumnsToContents()

        data_frame = self.data_frame_dict[data_frame_path]
        new_filter = Filter(data_frame=data_frame,
                            column=column_name,
                            condition=condition,
                            value=value)
        self._addFilter(new_filter, row)
        self.newFilterAdded.emit()

    def _addFilter(self, new_filter, row):
        self.filters[self.cur_filter_number] = new_filter
        self.filters_enabled[self.cur_filter_number] = True
        self.filter_indices.append(self.cur_filter_number)
        self.cur_filter_number += 1

    def _deleteFilter(self, filter_number):
        row_number = self.filter_indices.index(filter_number)
        was_enabled = self.filters_enabled[filter_number]
        self.filterTable.removeRow(row_number)

        del self.filters_enabled[filter_number]
        del self.filters[filter_number]
        self.filter_indices.remove(filter_number)

        if was_enabled:
            self.newFilterAdded.emit()

    def _onDeleteButtonPressed(self, filter_number):
        self._deleteFilter(filter_number)
        self.newFilterAdded.emit()

    def _onFilterCheckBoxChanged(self, filter_number, state):
        if state == Qt.Checked:
            self.filters_enabled[filter_number] = True
        else:  # unchecked
            self.filters_enabled[filter_number] = False
        self.newFilterAdded.emit()

    def _getGroupBoxStyleSheet(self):
        return """

QGroupBox {
    border: 1px solid gray;
    border-radius: 9px;
    margin-top: 0.5em;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px 0 3px;
}

"""
