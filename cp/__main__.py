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
from gui.qtpandas import DataFrameModel, DataFrameView
from gui.uiloader import loadUi
from gui import qtpandas

C_COLUMN, C_ROW = 0,1

def pivot(data_frames_dict, column_tuples, row_tuples):
    """ Returns a pivoted data frame 

    data_frames_dict: a dictionary with csv paths as keys and Pandas.DataFrame as values
    column_tuples: ordered list of tuples (csv_path, name_of_chosen_column)
    row_tuples: ordered list of tuples (csv_path, name_of_chosen_row)
    """
    pass

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
        self.customWidgets = [PivotComboBox, DataFrameView]
        loadUi('gui/cp.ui', baseinstance=self, customWidgets=self.customWidgets)

#        self.tableWidget = qtpandas.DataFrameWidget(self)
        print type(self.dataFrameView)
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
        self.dataFileContent.setSortingEnabled(False)
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
                self.fileListChanged.emit(self._getAvailableColumns())
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

    def get_combo_choices(self):
        column_combos = [self.columnComboBox1,
                 self.columnComboBox2,
                 self.columnComboBox3]

        row_combos = [self.rowComboBox1,
                      self.rowComboBox2,
                      self.rowComboBox3]


        chosen_rows = []
        chosen_columns = []

        for chosen_items, combos in [(chosen_rows, row_combos), (chosen_columns, column_combos)]:
            missing_choice = False
            for combo in combos:
                column_tuple = tuple(combo.itemData(combo.currentIndex()))
                chosen_items.append(column_tuple)
                if combo.level == 0:
                    if not combo.currentIndex():
                        QMessageBox.critical(self, "Error", "Invalid choice in combo boxes!\nSelect at least one column pivot.")
                        #return
                    else:
                        pass
                else:
                    if combo.currentIndex():
                        if missing_choice: #there is already one missing 
                            QMessageBox.critical(self, "Error", "Invalid choice in the combo boxes!")
                            #return
                    else:
                        missing_choice = True
        return chosen_rows, chosen_columns

    def pivotData(self):
        chosen_rows, chosen_columns = self.get_combo_choices()
        pivotedDataFrame = pivot(self.dataFrames, chosen_rows)


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

        for tableName, columnName in listOfColumns:
            string = "%s::%s" % (tableName, columnName)
            userData = (tableName, columnName)
            self.rowComboBox1.insertItem(1, string, userData)
            self.rowComboBox2.insertItem(1, string, userData)
            self.rowComboBox3.insertItem(1, string, userData)
            self.columnComboBox1.insertItem(1, string, userData)
            self.columnComboBox2.insertItem(1, string, userData)
            self.columnComboBox3.insertItem(1, string, userData)

    ### PRIVATE FUNCTIONS ###

    def _getAvailableColumns(self):
        columns = list()
        for path, dataFrame in self.dataFrames.items():
            tableName = os.path.basename(path)
            for columnName in dataFrame.columns:
                columns.append((tableName, columnName))
        return columns

    def _addDataFrameByPath(self, path):
        try:
            new_df = DataFrame.from_csv(path, index_col=[0], sep=';', parse_dates=False)
            if new_df.shape[1] == 1 or new_df.shape[1] == 0:
                new_df =DataFrame.from_csv(path, index_col=[0], sep=',', parse_dates=False)
        except IndexError: # index columns not recognized
            new_df =DataFrame.from_csv(path, index_col=[0], sep=',', parse_dates=False)
        print new_df.shape, new_df.columns
        self.dataFrames[path] = new_df 
        self.dataFilesList.addItem(path)

    def _fillTableFromDataFrame(self, tableWidget, dataFrame):
        assert isinstance(tableWidget, QTableView), "Expected QTableView, got %s" % type(tableWidget)
        assert isinstance(dataFrame, DataFrame), "Expected DataFrame, got %s" % type(dataFrame)

        start_time = time.time()
        tableWidget.setModel(None)

        sourceModel = DataFrameModel(dataFrame)
        proxyModel = QSortFilterProxyModel(self)
        proxyModel.setSourceModel(sourceModel)

        for i in xrange(len(dataFrame.columns.tolist())):
            label = str(dataFrame.columns.tolist()[i])
            item = QStandardItem(label)
            proxyModel.setHeaderData(i, Qt.Orientation.Horizontal, label)
        tableWidget.setModel(proxyModel)
       #  from itertools import repeat
       #  horizontalHeaderView = QHeaderView(Qt.Orientation.Horizontal, tableWidget)
       #  # horizontalModel = QStringListModel(list(repeat('1', 18)))
       # # horizontalModel = QStandardItemModel(tableWidget)
       #  horizontalModel = QStandardItemModel()
       #  for i in xrange(len(dataFrame.columns.tolist())):
       #      label = str(dataFrame.columns.tolist()[i])
       #      item = QStandardItem(label)
       #      print dataFrame.columns.tolist()[i]
       #      print item
       #      horizontalModel.insertColumn(0, [item])
       #      horizontalModel.setData(horizontalModel.createIndex(i,0), label)
       #  horizontalHeaderView.setModel(horizontalModel)
       #  horizontalHeaderView.setVisible(True)
       #  tableWidget.setHorizontalHeader(horizontalHeaderView)

        end_time = time.time()
        self.statusBar().showMessage("Inserted data in %g" % (end_time - start_time))

        tableWidget.show()

def main(argv=None):
    from pandas import DataFrame
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
