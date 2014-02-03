#!/usr/bin/env python

from __future__ import division
from PySide import QtCore, QtGui
from PySide.QtGui import *
from PySide.QtCore import *
import time
from tree_model import *


class TreeViewDelegate(QtGui.QStyledItemDelegate):
    def paint(self, painter, option, index):
        QtGui.QStyledItemDelegate.paint(self, painter, option, index)
        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setColor(QtGui.QColor("grey"))
        painter.setPen(pen)
        painter.drawRect(option.rect)


class MyTreeModel(QtGui.QStandardItemModel):
    def __init__(self, row, cols):
        QStandardItemModel.__init__(self, row, cols)
        self.filterValue = None

    def data(self, index, role):
        if not index.isValid():
            return QtGui.QStandardItemModel.data(self, index, role)
        if role == QtCore.Qt.BackgroundRole:
            value = self.data(index, QtCore.Qt.DisplayRole)
            try:
                value = float(value)
            except:
                value = 0
            if self.filterValue is not None:
                if value > self.filterValue:
                    return QColor("red")
                else:
                    return QColor("white")
            else:

                if value is None:
                    return QtGui.QColor("white")
                r, g, b = 0, 0, 0
                if 1/8 <= value and value <= 1/8:
                    r = 0
                    g = 0
                    b = 4*value + .5
                elif 1/8 < value and value <= 3/8:
                    r = 0
                    g = 4*value - .5
                    b = 0
                elif 3/8 < value and value <= 5/8:
                    r = 4*value - 1.5
                    g = 1
                    b = -4*value + 2.5
                elif (5/8 < value and value <= 7/8):
                    r = 1
                    g = -4*value + 3.5
                    b = 0
                elif (7/8 < value and value <= 1):
                    r = -4*value + 4.5
                    g = 0
                    b = 0
                else:
                    r = .5
                    g = 0
                    b = 0
                return QtGui.QColor.fromRgb(255*r, 255*g, 255*b, 100)
        return QtGui.QStandardItemModel.data(self, index, role)

    def filterChanged(self, text):
        print("filterChanged %s" % text)
        top = self.index(0, 0)
        bottom = self.index(self.rowCount()-1, self.columnCount()-1)

        try:
            value = float(text)
            self.filterValue = value

            self.dataChanged.emit(top, bottom)
        except ValueError:
            self.filterValue = None
            self.dataChanged.emit(top, bottom)


class MainWindow(QtGui.QMainWindow):
    def __init__(self, nr_columns, rows):
        super(MainWindow, self).__init__()

        self.setupModel()
        self.setupViews()
        self.statusBar()
        self.resize(870, 550)

    def setupModel(self):
        self.model = MyTreeModel(4, 20)
        self._set_data()

    def _set_data(self):
        start_time = time.time()
        for row_idx in xrange(0, 15):
            for col_idx in xrange(0,20):
                item = QStandardItem(str(((row_idx+1)*(col_idx+1))/(20*15)))
                #self.model.setData(self.model.index(row_idx, col_idx, QtCore.QModelIndex()), row_idx*col_idx)
                if col_idx == 0:
                    for subrow_idx in xrange(0,50):
                        children = []
                        for subcol_idx in xrange(0,20):
                            child = QStandardItem("%f" % ((subcol_idx+1)*(subrow_idx+1) /(50*20)))
                            children.append(child)
                        item.appendRow(children)
                self.model.setItem(row_idx, col_idx, item)
        end_time = time.time()
        print(self.model.data(self.model.createIndex(1, 1, self.model.invisibleRootItem()), Qt.DisplayRole))
        self.statusBar().showMessage("Inserted data in %g" % (end_time - start_time))

    def setupViews(self):
        splitter = QtGui.QSplitter()
        splitter.setStretchFactor(0,1)
        splitter.setStretchFactor(1,5)

        self.table = QtGui.QTreeView()
        self.table.setSortingEnabled(True)
        self.table.setItemDelegate(TreeViewDelegate())
        self.table.setModel(self.model)
        splitter.addWidget(self.table)

        self.le = QLineEdit(self)
        self.le.textChanged.connect(self.model.filterChanged)
        label = QLabel("Filter value")
        splitter.addWidget(self.le)
        verticalBox = QGroupBox()
        layout = QVBoxLayout()
        layout.addWidget(self.le)
        verticalBox.setLayout(layout)
        splitter.addWidget(verticalBox)

        self.selectionModel = QtGui.QItemSelectionModel(self.model)
        self.table.setSelectionModel(self.selectionModel)
        self.setCentralWidget(splitter)

if __name__ == '__main__':

    import sys
    import csv
    with open('../../../csv/sample.csv', 'rb') as csvfile:
        sample_reader = csv.reader(csvfile, delimiter=',')
        rows = list(sample_reader)[1:]
        rows = [map(float, row) for row in rows]
    rows = rows[:500]
    app = QtGui.QApplication(sys.argv)
    window = MainWindow(30, rows)
    window.show()
    window.showMaximized()
    sys.exit(app.exec_())
