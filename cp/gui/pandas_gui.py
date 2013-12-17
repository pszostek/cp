#!/usr/bin/env python
from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtUiTools import QUiLoader
import sys
import numpy as numpy
from pandas import *
import random
randn = np.random.randn

numbers = "zero one two three four five six seven eight nine".split()
numbers.extend("ten eleven twelve thirteen fourteen fifteen sixteen".split())

items = []
for row_idx in xrange(0, 4000):
    items.append(tuple([int(random.random()*10000), [random.random()*100//1 for _ in xrange(20)]]))
df = DataFrame.from_items(items, orient='index', columns=numbers)

class UiLoader(QUiLoader):
    def __init__(self, baseinstance):
        QUiLoader.__init__(self, baseinstance)
        self.baseinstance = baseinstance

    def createWidget(self, class_name, parent=None, name=''):
        if parent is None and self.baseinstance:
            # supposed to create the top-level widget, return the base instance
            # instead
            return self.baseinstance
        else:
            # create a new widget for child widgets
            widget = QUiLoader.createWidget(self, class_name, parent, name)
            if self.baseinstance:
                # set an attribute for the new child widget on the base
                # instance, just like PyQt4.uic.loadUi does.
                setattr(self.baseinstance, name, widget)
            return widget


def loadUi(uifile, baseinstance=None):
    loader = UiLoader(baseinstance)
    widget = loader.load(uifile)
    QMetaObject.connectSlotsByName(widget)
    return widget

class MainWindow(QMainWindow):

    def __init__(self, df, parent=None):
        QMainWindow.__init__(self, parent)
        loadUi('pandas.ui', self)
        self.df = df

        self._set_data()


    def _set_data(self):
        row_count = self.df.shape[0]
        column_count = len(self.df.columns)
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)
        self.tableWidget.setHorizontalHeaderLabels(df.columns)
        self.tableWidget.setShowGrid(True)
        for row_idx, row in enumerate(self.df.iterrows()):
            for col_idx, column_name in enumerate(self.df.columns):
                item = QTableWidgetItem(str(row[1][col_idx]))
                self.tableWidget.setItem(row_idx, col_idx, item)
           # for col_idx in xrange(0,20):
           #     item = QTableWidgetItem("1")
           #     self.tableWidget.setItem(row_idx, col_idx, item)
      #  print(self.tableWidget.data(self.model.createIndex(1, 1, self.tableWidget.invisibleRootItem()), Qt.DisplayRole))
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.setVerticalHeaderLabels(map(str, self.df.index.values))
        self.tableWidget.show()

def main(argv=None):
    if argv is None:
        argv = sys.argv

    app = QApplication(argv)
    window = MainWindow(df)
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
