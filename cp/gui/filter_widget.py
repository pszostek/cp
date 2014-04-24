#!/usr/bin/env python

from PySide.QtGui import *
from PySide.QtCore import *
from pandas import DataFrame
from collections import namedtuple
import os
try:
    from istateful import IStateful
except:
    IStateful = object

Filter = namedtuple(
    'Filter',
    "data_frame_name column condition value".split(' '),
    verbose=False)


class NewFilterWidget(QWidget, IStateful):
    newFilterAdded = Signal(DataFrame, str, str, str)

    def __init__(self, parent=None):
        super(NewFilterWidget, self).__init__(parent)
        policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.setSizePolicy(policy)
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.treeWidget = QTreeWidget(self)
        self.treeWidget.setColumnCount(1)
        self.treeWidget.header().close()
        self.treeWidget.setSizePolicy(policy)
        layout.addWidget(self.treeWidget)

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
        table_item = QTreeWidgetItem(self.treeWidget)
        table_item.setText(0, table_name)
        for column_name in table_columns:
            column_item = QTreeWidgetItem(table_item)
            column_item.setText(0, column_name)
            column_item.setData(0, Qt.UserRole, (data_frame_path, column_name))

    def buttonPressed(self):
        data_frame, column_name = self.treeWidget.currentItem().data(
            0, Qt.UserRole)
        condition = self.conditionCombo.currentText()
        value = self.valueEdit.text()
        self.newFilterAdded.emit(data_frame, column_name, condition, value)

    def getState(self):
        return self._model_to_list()

    def setState(self, state):
        for parent_text, children_list in state:
            parent_item = QTreeWidgetItem(self.treeWidget)
            parent_item.setText(0, parent_text)
            for child_text, child_data in children_list:
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, child_text)
                child_item.setData(0, Qt.UserRole, tuple(child_data))

    def _model_to_list(self):
        it = QTreeWidgetItemIterator(self.treeWidget)
        cur_parent = None
        cur_children = None
        ret = []
        while it.value():
            item = it.value()
            if item.childCount() != 0:
                if cur_parent is not None:
                    ret.append((cur_parent, cur_children))
                cur_children = []
                cur_parent = item.text(0)
            else:
                cur_children.append((item.text(0), item.data(0, Qt.UserRole)))
            it += 1
        if cur_parent is not None:
            ret.append((cur_parent, cur_children))
        return ret


class FilterWidget(QWidget, IStateful):
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
        self.newFilterWidget = None
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

    def sizeHint(self):
        return QSize(0, 30)

    def getState(self):
        return (self.filters,
                self.filters_enabled,
                self.filter_indices,
                self.cur_filter_number,
                self.newFilterWidget.getState())

    def setState(self, state):
        (filters,
         filters_enabled,
         filter_indices,
         cur_filter_number,
         new_filter_line_state) = state

        self.filters = filters
        self.filters_enabled = filters_enabled
        self.filter_indices = filter_indices
        self.cur_filter_number = cur_filter_number

        for row_idx, filter_ in enumerate(filters.values()):
            assert isinstance(filter_, Filter)
            self._insertNewFilterIntoTable(new_filter=filter_,
                                           row=row_idx,
                                           filter_index=filter_indices[row_idx])

        self.newFilterWidget.setState(new_filter_line_state)

    def setDataFrameDict(self, data_frame_dict):
        self.data_frame_dict = data_frame_dict

    def getActiveFilters(self):
        return [filter_ for filter_id,
                filter_ in self.filters.items() if self.filters_enabled[filter_id]]

    def addDataFrame(self, data_frame, table_name, table_columns):
        self.newFilterWidget.addColumns(data_frame_path=data_frame.path,
                                        table_name=table_name,
                                        table_columns=table_columns)

    def _createNewFilterGroupBox(self):
        self.newFilterGroupBox = QGroupBox("New filter", self)
        self.newFilterGroupBox.setStyleSheet(self._getGroupBoxStyleSheet())
        policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.newFilterGroupBox.setSizePolicy(policy)

        layout = QHBoxLayout()
        self.newFilterGroupBox.setLayout(layout)

        self.newFilterWidget = NewFilterWidget(self)
        layout.addWidget(self.newFilterWidget)
        self.newFilterWidget.newFilterAdded.connect(self._onAddButtonPressed)
        return self.newFilterGroupBox

    def _createExistingFiltersGroupBox(self):
        self.existingFilterGroupBox = QGroupBox("Existing filters", self)
        self.existingFilterGroupBox.setStyleSheet(
            self._getGroupBoxStyleSheet())
        layout = QHBoxLayout()
        self.existingFilterGroupBox.setLayout(layout)

        self.filterTable = QTableWidget(0, 6, self)
        self.filterTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.filterTable.setSizePolicy(policy)
        self.filterTable.setHorizontalHeaderLabels(
            ["Data source", "Column", "Condition", "Value", "Enabled", ""])
        layout.addWidget(self.filterTable)
        return self.existingFilterGroupBox

    def _insertNewFilterIntoTable(self, new_filter, row, filter_index=None):
        from functools import partial
        if filter_index is None:
            filter_index = self.cur_filter_number
        row = self.filterTable.rowCount()

        self.filterTable.insertRow(row)
        self.filterTable.setItem(
            row, 0, QTableWidgetItem(
                new_filter.data_frame_name))
        self.filterTable.setItem(row, 1, QTableWidgetItem(new_filter.column))
        self.filterTable.setItem(
            row, 2, QTableWidgetItem(
                new_filter.condition))
        self.filterTable.setItem(row, 3, QTableWidgetItem(new_filter.value))

        enabledCheckBox = QCheckBox()
        enabledCheckBox.setCheckState(Qt.Checked)
        enabledCheckBox.stateChanged.connect(
            partial(
                self._onFilterCheckBoxChanged,
                filter_index))
        self.filterTable.setItem(row, 4, QTableWidgetItem())
        self.filterTable.setCellWidget(row, 4, enabledCheckBox)

        deleteButton = QPushButton("Remove")
        deleteButton.setIcon(QIcon.fromTheme("list-remove"))
        deleteButton.clicked.connect(
            partial(
                self._onDeleteButtonPressed,
                filter_index))
        self.filterTable.setItem(row, 5, QTableWidgetItem())
        self.filterTable.setCellWidget(row, 5, deleteButton)
        self.filterTable.resizeColumnsToContents()

    def _addNewFilter(self, new_filter):
        self.filters[self.cur_filter_number] = new_filter
        self.filters_enabled[self.cur_filter_number] = True
        self.filter_indices.append(self.cur_filter_number)

    def _onAddButtonPressed(
            self, data_frame_path, column_name, condition, value):
        row = self.filterTable.rowCount()
        data_frame_name = os.path.basename(data_frame_path)

        new_filter = Filter(data_frame_name=data_frame_name,
                            column=column_name,
                            condition=condition,
                            value=value)

        self._insertNewFilterIntoTable(new_filter, row)
        self._addNewFilter(new_filter)

        self.cur_filter_number += 1
        self.newFilterAdded.emit()

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
        print("deleteButton", filter_number)
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

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    widget = FilterWidget()
    widget.show()
    app.exec_()