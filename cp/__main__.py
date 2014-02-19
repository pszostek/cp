#!/usr/bin/env python

from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtUiTools import QUiLoader
import sys
import numpy as np
from pandas import *
import random
import time
import signal
import os
from functools import partial
from gui.qtpandas import DataFrameModel
from gui.uiloader import loadUi

C_COLUMN, C_ROW = 0,1

class PivotComboBox(QComboBox):
    def __init__(self, parent=None):
        super(PivotComboBox, self).__init__(parent)
        self.role = None
        self.level = None
        self.disabledRows = []

    def clear(self):
        super(PivotComboBox, self).clear()
        self.addItem("")

    def enableItem(self, row):
        if row not in self.disabledRows:
            return
        toEnableIndex = self.model().index(row, 0)
        self.model().setData(toEnableIndex, 1|32, Qt.UserRole-1)
        del self.disabledRows[self.disabledRows.index(row)]

    def disableItem(self, row):
        toDisableIndex = self.model().index(row, 0)
        self.model().setData(toDisableIndex, 0, Qt.UserRole-1)
        self.disabledRows.append(row)

class MainWindow(QMainWindow):
    fileListChanged = Signal(list)

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.customWidgets = [PivotComboBox]
        loadUi('gui/cp.ui', self)

        self.redoButton.setIcon(QIcon.fromTheme("edit-redo"))
        self.undoButton.setIcon(QIcon.fromTheme("edit-undo"))
        self.openFileButton.setIcon(QIcon.fromTheme("document-open"))
        self.removeFileButton.setIcon(QIcon.fromTheme("edit-delete"))

        self.applyComboBoxesButton.clicked.connect(self.pivotData)
        self.rowComboBox1.activated.connect(partial(self.propagateComboBoxChange, self.rowComboBox1))
        self.rowComboBox1.role = C_ROW
        self.rowComboBox1.level = 1
        self.rowComboBox2.activated.connect(partial(self.propagateComboBoxChange, self.rowComboBox2))
        self.rowComboBox2.role = C_ROW
        self.rowComboBox2.level = 2
        self.rowComboBox3.activated.connect(partial(self.propagateComboBoxChange, self.rowComboBox3))
        self.rowComboBox3.role = C_ROW
        self.rowComboBox3.level = 3
        self.columnComboBox1.activated.connect(partial(self.propagateComboBoxChange, self.columnComboBox1))
        self.columnComboBox1.role = C_COLUMN
        self.columnComboBox1.level = 1
        self.columnComboBox2.activated.connect(partial(self.propagateComboBoxChange, self.columnComboBox2))
        self.columnComboBox2.role = C_COLUMN
        self.columnComboBox2.level = 2
        self.columnComboBox3.activated.connect(partial(self.propagateComboBoxChange, self.columnComboBox3))
        self.columnComboBox3.role = C_COLUMN
        self.columnComboBox3.level = 3

        self.actionExit.triggered.connect(self.close)
        self.actionData_file.triggered.connect(self.addDataFile)

        self.openFileButton.clicked.connect(self.addDataFile)
        self.removeFileButton.clicked.connect(self.removeDataFile)
        self.dataFilesList.itemDoubleClicked.connect(self.showDataFrameOutlook)
  
        self.dataFileContent.horizontalHeader().setVisible(True)
        self.dataFileContent.setSortingEnabled(True)
        self.dataFileContent.setShowGrid(True)
        self.dataFileContent.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.fileListChanged.connect(self.addNewItemsToComboBoxes)
        ####
        self.dataFrames = dict()  # (path, fileObject) dictionary

    ### SLOTS ###

    def addDataFile(self):
        selectedFilePath = QFileDialog.getOpenFileName(self, "Select data file")[0]
        if not selectedFilePath:
            return
        if selectedFilePath not in self.dataFrames.keys():
            try:
                self._addDataFrameByPath(selectedFilePath)
                self.fileListChanged.emit(self._getColumnNames())
            except:
                QMessageBox.critical(self, "Error", "Chosen file is not in the CSV format")
                raise
        else:
            QMessageBox.warning(self, "Error", "Chosen file is already open!")

    def removeDataFile(self):
        size = self.dataFilesList.size()
        if size == 0:
            QMessageBox.warning(self, "Error", "There are no files on the list!")
            return
        itemList = self.dataFilesList.selectedItems()
        for item in itemList:
            self.dataFilesList.takeItem(self.dataFilesList.indexFromItem(item).row())
            del self.dataFrames[item.data(Qt.ItemDataRole)]
        print "file removed"
 
    def showDataFrameOutlook(self, listItem):
        chosenFilePath = listItem.data(Qt.ItemDataRole)
        chosenDataFrame = self.dataFrames[chosenFilePath]
        self._fillTableFromDataFrame(self.dataFileContent, chosenDataFrame)

    def pivotData(self):
        c1i = self.columnComboBox1.currentIndex()
        c2i = self.columnComboBox2.currentIndex()
        c3i = self.columnComboBox3.currentIndex()
        r1i = self.rowComboBox1.currentIndex()
        r2i = self.rowComboBox2.currentIndex()
        r3i = self.rowComboBox3.currentIndex()
        if (not (c1i or c2i or c3i)):
            QMessageBox.critical(self, "Error", "Invalid choice in combo boxes!\nSelect at least one column pivot.")
        if (not (r1i or r2i or r3i)):
            QMessageBox.critical(self, "Error", "Invalid choice in combo boxes!\nSelect at least one row pivot.")
        if ((c2i and not c1i) or (c3i and not (c1i and c2i))):
            QMessageBox.critical(self, "Error", "Invalid choice in the combo boxes!")
        if ((r2i and not r1i) or (r3i and not (r1i and r2i))):
            QMessageBox.critical(self, "Error", "Invalid choice in the combo boxes!")


    def propagateComboBoxChange(self, source, index):
        level = source.level
        if source.role == C_COLUMN:
            if level == 1:
                if index == 0:
                    self.columnComboBox2.setEnabled(False)
                    self.columnComboBox3.setEnabled(False)
                else:
                    self.columnComboBox2.setEnabled(True)
                    self.columnComboBox2.disableItem(index)
                    self.columnComboBox3.disableItem(index)
            elif level == 2:
                if index == 0:
                    self.columnComboBox3.setEnabled(False)
                else:
                    self.columnComboBox3.setEnabled(True)
                    self.columnComboBox3.disableItem(index)
        else:  # source.role == C_ROW
            if level == 1:
                if index == 0:
                    self.rowComboBox2.setEnabled(False)
                    self.rowComboBox3.setEnabled(False)
                else:
                    self.rowComboBox2.setEnabled(True)
                    self.rowComboBox2.disableItem(index)
                    self.rowComboBox3.disableItem(index)
            elif level == 2:
                if index == 0:
                    self.rowComboBox3.setEnabled(False)
                else:
                    self.rowComboBox3.setEnabled(True)
                    self.rowComboBox3.disableItem(index)


    def addNewItemsToComboBoxes(self, listOfColumns):
        if len(self.dataFrames) > 0:
            self.rowComboBox1.setEnabled(True)
            self.columnComboBox1.setEnabled(True)
        self.rowComboBox1.clear()
        self.rowComboBox2.clear()
        self.rowComboBox3.clear()
        self.columnComboBox1.clear()
        self.columnComboBox2.clear()
        self.columnComboBox3.clear()

        self.rowComboBox1.insertItems(1, listOfColumns)
        self.rowComboBox2.insertItems(1, listOfColumns)
        self.rowComboBox3.insertItems(1, listOfColumns)
        self.columnComboBox1.insertItems(1, listOfColumns)
        self.columnComboBox2.insertItems(1, listOfColumns)
        self.columnComboBox3.insertItems(1, listOfColumns)

    ### PRIVATE FUNCTIONS ###

    def _getColumnNames(self):
        columnNames = list()
        for path, dataFrame in self.dataFrames.items():
            tableName = '.'.join(os.path.basename(path).split('.')[:-1])
            for columnName in dataFrame.columns:
                columnNames.append("%s::%s" % (tableName, columnName))
        return columnNames

    def _addDataFrameByPath(self, path):
        new_df = DataFrame.from_csv(path, index_col=0, sep=';', parse_dates=False)
        if new_df.shape[1] == 1:
            new_df =DataFrame.from_csv(path, index_col=0, sep=',', parse_dates=False)
        self.dataFrames[path] = new_df 
        self.dataFilesList.addItem(path)

    def _fillTableFromDataFrame(self, tableWidget, dataFrame):
        assert isinstance(tableWidget, QTableView), "Expected QTableView, got %s" % type(tableWidget)
        assert isinstance(dataFrame, DataFrame), "Expected DataFrame, got %s" % type(dataFrame)

        start_time = time.time()
        tableWidget.setModel(None)

        sourceModel = DataFrameModel(self)
        sourceModel.setDataFrame(dataFrame)
        proxyModel = QSortFilterProxyModel(self)
        proxyModel.setSourceModel(sourceModel)
        tableWidget.setModel(proxyModel)

        end_time = time.time()
        self.statusBar().showMessage("Inserted data in %g" % (end_time - start_time))

        tableWidget.show()

def main(argv=None):
    if argv is None:
        argv = sys.argv

    app = QApplication(argv)
    window = MainWindow()
    window.showMaximized()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app.setQuitOnLastWindowClosed(True)
    app.exec_()


if __name__ == '__main__':
    main()
