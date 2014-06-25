#!/usr/bin/env python

from PySide.QtGui import *
from PySide.QtCore import *
from pandas import DataFrame
from collections import namedtuple
import os
try:
    from istateful import IStateful
except:
    IStateful=object

from filter_widget import NewFilterWidget

class ColoringWidget(QWidget, IStateful):
    newFilterAdded = Signal(DataFrame, str, str, str)

    def __init__(self, parent=None):
        super(ColoringWidget, self).__init__(parent)
        policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.setSizePolicy(policy)
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.treeWidget = QTreeWidget(self)
        self.treeWidget.setColumnCount(1)
        self.treeWidget.header().close()
        policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.treeWidget.setSizePolicy(policy)
        layout.addWidget(self.treeWidget)

        self.conditionCombo = QComboBox(self)
        self.conditionCombo.insertItems(0, ["==", "<", ">", "<=", ">=", "!="])
        layout.addWidget(self.conditionCombo)

        self.valueEdit = QLineEdit(self)
        layout.addWidget(self.valueEdit)

        self.addButton = QPushButton(self)
        self.addButton.setText("Stack")
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

if __name__ == "__main__":
    import sys
    argv = sys.argv
    app = QApplication(argv)
    window = ColoringWidget()
    window.showMaximized()
    app.exec_()
