#!/usr/bin/env python

from __future__ import division
from PySide import QtCore, QtGui
from PySide.QtGui import *
from PySide.QtCore import *
from tree_model import *


class TreeViewDelegate(QtGui.QStyledItemDelegate):
    def paint(self, painter, option, index):
        QtGui.QStyledItemDelegate.paint(self, painter, option, index)
        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setColor(QtGui.QColor("grey"))
        painter.setPen(pen)
        painter.drawRect(option.rect)

class MyTreeView(QtGui.QTreeView):
    def valueChanged(self, value):
        self.value = value

    def returnPressed(self):
        self.setCurrentIndex(self.model().createIndex(int(self.value),0))
        self.scrollTo(self.model().createIndex(int(self.value),2))

class MainWindow(QtGui.QMainWindow):
    def __init__(self, nr_columns, rows):
        super(MainWindow, self).__init__()

        self.setupModel(nr_columns=nr_columns, rows=rows)
        self.setupViews()
   #     self.statusBar()
        self.resize(870, 550)

    def setupModel(self, nr_columns, rows):
        self.model = QtGui.QStandardItemModel(len(rows), nr_columns, self)
        self._set_data(rows)

    def _set_data(self, rows):
        for row_idx, row in enumerate(rows):
            self.model.insertRows(row_idx, 1, self.model.createIndex(0,0))
            for col_idx, col in enumerate(row):
                self.model.setData(self.model.index(row_idx, col_idx, QtCore.QModelIndex()), col)

    def setupViews(self):
        topLayout = QHBoxLayout(self)

        self.table = MyTreeView()
     #   self.table.setSortingEnabled(True)
        self.table.setAnimated(True)
        self.table.setItemDelegate(TreeViewDelegate())
        self.table.setModel(self.model)
        self.table.setCurrentIndex(QModelIndex())

        topLayout.addWidget(self.table)
        topLayout.addStretch(1)

       # self.le = QLineEdit(self)
       # self.le.textEdited.connect(self.table.valueChanged)
       # self.le.returnPressed.connect(self.table.returnPressed)
       # splitter.addWidget(self.le)

        bottomWidget = QWidget()
        bottomLayout = QHBoxLayout(bottomWidget)

        self.scene = QGraphicsScene(0, 0, 200, 20, self)
     #   bottomLayout.addWidget(self.scene)
        # elipse = QGraphicsEllipseItem(0.0, 0.0, 10.0, 100.0, None, self.scene)
        # textItem = QGraphicsSimpleTextItem("text", None, self.scene)
        # textItem.setPos(0, 0)
        # textItem.setFlag(QGraphicsItem.ItemIsMovable)
        # self.scene.addItem(textItem)
        # self.scene.addItem(elipse)
        graphicsView = QGraphicsView(self.scene, bottomWidget)
        graphicsView.setRenderHints(QPainter.Antialiasing)

        mainLayout = QVBoxLayout(self);
        mainLayout.addWidget(topLayout)
      #  mainLayout.addStretch(1)
        mainLayout.addWidget(bottomWidget)
     #  mainLayout.addStretch(1)

        self.selectionModel = QtGui.QItemSelectionModel(self.model)
        self.table.setSelectionModel(self.selectionModel)

        self.setLayout(mainLayout)

if __name__ == '__main__':

    import sys
    import csv
    with open('timeseries.csv', 'rb') as csvfile:
        sample_reader = csv.reader(csvfile, delimiter=',')
        rows = list(sample_reader)
    app = QtGui.QApplication(sys.argv)
    window = MainWindow(nr_columns=3, rows=rows)
    window.show()
 #   window.showMaximized()
    sys.exit(app.exec_())
