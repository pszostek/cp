#!/usr/bin/env python
import hhv
from PySide import QtCore, QtGui
from PySide.QtGui import *
from PySide.QtCore import *
import sys

class ExampleModel(QAbstractTableModel):
    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._horizontalHeaderModel = QStandardItemModel()
        self._verticalHeaderModel = QStandardItemModel()
        self.fillHeaderModel(self._horizontalHeaderModel)
        self.fillHeaderModel(self._verticalHeaderModel)

    def fillHeaderModel(self, headerModel):
        rootItem = QStandardItem("root")
        rotatedTextCell = QStandardItem("rotated text")
        rotatedTextCell.setData(1, Qt.UserRole)
        rootItem.appendColumn([rotatedTextCell])

        cell = QStandardItem("level 2")
        rootItem.appendColumn([cell])

        cell.appendColumn([QStandardItem("level 3")])
        cell.appendColumn([QStandardItem("level 3")])

        rootItem.appendColumn([QStandardItem("level 2")])
        headerModel.setItem(0,0,rootItem)
    def rowCount(self, index):
        return 4

    def columnCount(self, index):
        return 4

    def data(self, index, role):
        if role == Qt.UserRole:
            return self._horizontalHeaderModel
        if role == Qt.UserRole+1:
            return self._verticalHeaderModel
        if role == Qt.DisplayRole and index.isValid():
            return "index(%d, %d)" % (index.row(), index.column())


app = QtGui.QApplication(sys.argv)
em = ExampleModel()
tv = QTableView()
hv = hhv.HierarchicalHeaderView(QtCore.Qt.Horizontal)
tv.setHorizontalHeader(hv)
hv = hhv.HierarchicalHeaderView(Qt.Vertical, tv)
tv.setVerticalHeader(hv)
tv.setModel(em)
tv.show()
app.exec_()
