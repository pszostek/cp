#!/usr/bin/env python

from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtUiTools import QUiLoader
import sys
import numpy as np
from pandas import *
import random
import time
randn = np.random.randn


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
        self._set_table()


    def _set_table(self):
        row_count = self.df.shape[0]
        column_count = len(self.df.columns)
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count+1)
        self.tableWidget.setHorizontalHeaderLabels([''] + list(self.df.columns))
        self.tableWidget.setShowGrid(True)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)

        grayBrush = QBrush(Qt.lightGray)
        start_time = time.time()
        for row_idx, row in enumerate(self.df.iterrows()):
            indexItem = QTableWidgetItem(str(row[0]))
            indexItem.setFlags(indexItem.flags() ^ Qt.ItemIsEditable)
            indexItem.setBackground(grayBrush)
            self.tableWidget.setItem(row_idx, 0, indexItem)
            for col_idx, column_name in enumerate(self.df.columns):
                item = QTableWidgetItem(str(row[1][col_idx]))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.tableWidget.setItem(row_idx, col_idx+1, item)
        end_time = time.time()
        self.statusBar().showMessage("Inserted data in %g" % (end_time - start_time))
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.show()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    numbers = "zero one two three four five six seven eight nine".split()
    numbers.extend("ten eleven twelve thirteen fourteen fifteen sixteen".split())

    items = []
    for row_idx in xrange(0, 4000):
        items.append((int(random.random()*10000), [random.random()*100//1 for _ in xrange(20)]))
    df = DataFrame.from_items(items, orient='index', columns=numbers)

    app = QApplication(argv)
    window = MainWindow(df)
    window.showMaximized()
    app.exec_()


if __name__ == '__main__':
    main()
