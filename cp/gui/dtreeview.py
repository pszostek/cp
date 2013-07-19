#!/usr/bin/python2
# -*- coding: utf-8 -*-
from __future__ import division
from PySide import QtCore, QtGui
from PySide.QtGui import *
from PySide.QtCore import *
import time
from tree_model import *
import sys

from PySide.QtCore import QIODevice, QFile, SIGNAL, SLOT
from PySide.QtGui import QApplication, QLineEdit
from PySide.QtScript import QScriptEngine
from PySide.QtUiTools import QUiLoader
from PySide.QtGui import *
from PySide.QtCore import Slot, QMetaObject
from PySide.QtUiTools import QUiLoader
from PySide.QtGui import QApplication, QMainWindow, QMessageBox

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

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        loadUi('olprof.ui', self)
        self.pushButton.clicked.connect(self.pinupModel)
        self.model = None 
        self.treeView.setModel(self.model)

    def pinupModel(self):
        if not self.model:
            self.model = MyTreeModel(4, 20)
            self._set_data()
            self.treeView.setModel(self.model)

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


def main(argv=None):
    if argv is None:
        argv = sys.argv

    app = QApplication(argv)
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()