#!/usr/bin/env python

from PySide.QtGui import *
from PySide.QtCore import *
import signal
import os
import sys
import time
import pivot
from istateful import IStateful
from pandas import DataFrame
from functools import partial
from gui.qtpandas import DataFrameModel, DataFrameView#, ColorDelegate
from gui.uiloader import loadUi
from collections import deque
from gui.pivot_combo_box import PivotComboBox
from gui.foldable_widget import FilterWindow
from gui.filter_group_box import FilterGroupBox

C_COLUMN, C_ROW = 0, 1


class MainWindow(QMainWindow, IStateful):
    fileListChanged = Signal(list)

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.customWidgets = [PivotComboBox, DataFrameView, FilterGroupBox]
        loadUi('gui/cp.ui', baseinstance=self,
               customWidgets=self.customWidgets)

#        self.tableWidget = qtpandas.DataFrameWidget(self)
        self.redoButton.setIcon(QIcon.fromTheme("edit-redo"))
        self.undoButton.setIcon(QIcon.fromTheme("edit-undo"))
        self.openFileButton.setIcon(QIcon.fromTheme("document-open"))
        self.removeFileButton.setIcon(QIcon.fromTheme("edit-delete"))

        self.applyComboBoxesButton.clicked.connect(self.pivotData)
        self.rowComboBox1.activated.connect(
            partial(self.propagateComboBoxChange, self.rowComboBox1))
        self.rowComboBox1.role = C_ROW
        self.rowComboBox1.level = 1
        self.rowComboBox2.activated.connect(
            partial(self.propagateComboBoxChange, self.rowComboBox2))
        self.rowComboBox2.role = C_ROW
        self.rowComboBox2.level = 2
        self.rowComboBox3.activated.connect(
            partial(self.propagateComboBoxChange, self.rowComboBox3))
        self.rowComboBox3.role = C_ROW
        self.rowComboBox3.level = 3
        self.columnComboBox1.activated.connect(
            partial(self.propagateComboBoxChange, self.columnComboBox1))
        self.columnComboBox1.role = C_COLUMN
        self.columnComboBox1.level = 1
        self.columnComboBox2.activated.connect(
            partial(self.propagateComboBoxChange, self.columnComboBox2))
        self.columnComboBox2.role = C_COLUMN
        self.columnComboBox2.level = 2
        self.columnComboBox3.activated.connect(
            partial(self.propagateComboBoxChange, self.columnComboBox3))
        self.columnComboBox3.role = C_COLUMN
        self.columnComboBox3.level = 3

        self.actionExit.triggered.connect(self.close)
        self.actionData_file.triggered.connect(self.addDataFile)
        self.actionSave_as.triggered.connect(self.saveProjectAs)
        self.actionProject.triggered.connect(self.openProject)

        self.openFileButton.clicked.connect(self.addDataFile)
        self.removeFileButton.clicked.connect(self.removeDataFile)
        self.dataFilesList.itemDoubleClicked.connect(self.showDataFrameOutlook)

        self.dataFileContent.horizontalHeader().setVisible(True)
        self.dataFileContent.setSortingEnabled(False)
        self.dataFileContent.setShowGrid(True)
        self.dataFileContent.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.fileListChanged.connect(self.addNewItemsToComboBoxes)

        print(dir(self))
        self.filterGroupBoxButton.released.connect(self.toggleFilterGroupBox)
        self.filterGroupBox.hide()
        print(type(self.filterGroupBox))
       # self.filterCheckBox.stateChanged.connect(self.toggleFilter)
        ####
        self.dataFrames = dict()  # (path, fileObject) dictionary
        self.dataDisplayed = False
        self.filtersDisplayed = False

    ### SLOTS ###

    def toggleFilterGroupBox(self):
        self.filtersDisplayed = not self.filtersDisplayed
        if self.filtersDisplayed:
            self.filterGroupBox.show()
            self.filterGroupBoxButton.setText(">>> Filters")
        else:
            self.filterGroupBox.hide()
            self.filterGroupBoxButton.setText("<<< Filters")

    def addDataFile(self):
        selected_file_paths = QFileDialog.getOpenFileNames(
            self, "Select data file")[0]
        if not selected_file_paths:
            return
        for selected_file_path in selected_file_paths:
            if selected_file_path not in self.dataFrames.keys():
                try:
                    self._addDataFrameByPath(selected_file_path)
                    self.fileListChanged.emit(self._getAvailableColumns())
                except:
                    QMessageBox.critical(
                        self, "Error", "Chosen file is not in the CSV format")
                    raise
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Chosen file is already open!")

    def setState(self, state):
        import StringIO
        for combo in self.getColumnCombos() + self.getRowCombos():
            combo.setState(state.popleft())
        self.displayedValueComboBox.setState(state.popleft())
        self.dataFrames = {}

        data_frame_paths = state.popleft()
        self.dataFilesList.clear()
        for data_frame_path in data_frame_paths:
            self._addDataFrameByPath(data_frame_path)

        data_frame_string = state.popleft()
        f = StringIO.StringIO(data_frame_string)
        self.dataFrameView.setDataFrame(DataFrame.from_csv(f))

    def getState(self):
        import StringIO
        state = deque()
        for combo in self.getColumnCombos()+self.getRowCombos():
            state.append(combo.getState())
        state.append(self.displayedValueComboBox.getState())
        state.append(self.dataFrames.keys())

        f = StringIO.StringIO()
        self.dataFrameView.dataModel.df.to_csv(f)
        state.append(f.getvalue())

        return state

    def openProject(self):
        import dill as pickle
        path = QFileDialog.getOpenFileName()
        input_file = open(path[0], 'rb')
        state = pickle.load(input_file)
        input_file.close()
        self.setState(state)

    def saveProjectAs(self):
        import dill as pickle
        path = QFileDialog.getSaveFileName()
        output_file = open(path[0], 'wb')
        state = self.getState()
        pickle.dump(state, output_file)
        output_file.close()

    def removeDataFile(self):
        size = self.dataFilesList.size()
        if size == 0:
            QMessageBox.warning(
                self, "Error", "There are no files on the list!")
            return
        itemList = self.dataFilesList.selectedItems()
        for item in itemList:
            self.dataFilesList.takeItem(
                self.dataFilesList.indexFromItem(item).row())
            del self.dataFrames[item.data(Qt.ItemDataRole)]

    def showDataFrameOutlook(self, listItem):
        chosenFilePath = listItem.data(Qt.ItemDataRole)
        chosenDataFrame = self.dataFrames[chosenFilePath]
        self._fillTableFromDataFrame(self.dataFileContent, chosenDataFrame)

    def getComboChoices(self):
        column_combos = self.getColumnCombos()
        row_combos = self.getRowCombos()

        chosen_rows = []
        chosen_columns = []

        for chosen_items, combos in [(chosen_rows, row_combos), (chosen_columns, column_combos)]:
            missing_choice = False
            for combo in combos:
                if combo.level == 0:
                    if not combo.currentIndex():
                        QMessageBox.critical(
                            self, "Error", "Invalid choice in combo boxes!\nSelect at least one column pivot.")
                        return
                    else:
                        pass
                else:
                    if combo.currentIndex():
                        if missing_choice:  # there is already one missing
                            QMessageBox.critical(
                                self, "Error", "Invalid choice in the combo boxes!")
                            return
                    else:
                        missing_choice = True
                try:
                    column_tuple = tuple(combo.itemData(combo.currentIndex()))
                    chosen_items.append(column_tuple)
                except TypeError:
                    pass
        displayed_value = tuple(self.displayedValueComboBox.itemData(
            self.displayedValueComboBox.currentIndex()))
        return chosen_rows, chosen_columns, displayed_value

    def pivotData(self):
        from pivot import PivotEngineException
        # if self.filterCheckBox.isChecked():
        #     filter_string = self.filterLineEdit.text()
        # else:
        #     filter_string = None
        filter_string = self.filterLineEdit.text()
        ###
        row_tuples, column_tuples, displayed_value = self.getComboChoices()
        try:
            pivoted_data_frame = pivot.pivot(
                data_frames_dict=self.dataFrames,
                column_tuples=column_tuples,
                row_tuples=row_tuples,
                displayed_value=displayed_value,
                filter_string=filter_string)
          #  self.dataFrameView.setItemDelegate(ColorDelegate())
            self.dataFrameView.setDataFrame(pivoted_data_frame)
        except PivotEngineException, e:
            QMessageBox.warning(self,
                                "Error",
                                str(e))

    def getColumnCombos(self):
        return [self.columnComboBox1,
                self.columnComboBox2,
                self.columnComboBox3]

    def getRowCombos(self):
        return [self.rowComboBox1,
                self.rowComboBox2,
                self.rowComboBox3]

    def propagateComboBoxChange(self, source, index):
        level = source.level

        # if source.role == C_COLUMN:
        #     for combo in self.getColumnCombos():

        previous_index = source.previousIndex()
        if source.role == C_COLUMN:
            if level == 1:
                if index == 0:
                    self.columnComboBox2.setEnabled(False)
                    self.columnComboBox3.setEnabled(False)
                else:
                    self.columnComboBox2.setEnabled(True)
                    self.columnComboBox2.disableItem(index)
                    self.columnComboBox3.disableItem(index)
                if previous_index:
                    self.columnComboBox2.enableItem(previous_index)
                    self.columnComboBox3.enableItem(previous_index)

            elif level == 2:
                if index == 0:
                    self.columnComboBox3.setEnabled(False)
                else:
                    self.columnComboBox3.setEnabled(True)
                    self.columnComboBox3.disableItem(index)
                if previous_index:
                    self.columnComboBox3.enableItem(previous_index)
        else:  # source.role == C_ROW
            if level == 1:
                if index == 0:
                    self.rowComboBox2.setEnabled(False)
                    self.rowComboBox3.setEnabled(False)
                else:
                    self.rowComboBox2.setEnabled(True)
                    self.rowComboBox2.disableItem(index)
                    self.rowComboBox3.disableItem(index)
                if previous_index:
                    self.rowComboBox2.enableItem(previous_index)
                    self.rowComboBox3.enableItem(previous_index)
            elif level == 2:
                if index == 0:
                    self.rowComboBox3.setEnabled(False)
                else:
                    self.rowComboBox3.setEnabled(True)
                    self.rowComboBox3.disableItem(index)
                if previous_index:
                    self.rowComboBox3.enableItem(previous_index)

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
        self.displayedValueComboBox.clear()

        for path, column_name in listOfColumns:
            table_name = os.path.basename(path)
            string = "%s::%s" % (table_name, column_name)
            user_data = (path, column_name)
            self.displayedValueComboBox.insertItem(1, string, user_data)
            self.rowComboBox1.insertItem(1, string, user_data)
            self.rowComboBox2.insertItem(1, string, user_data)
            self.rowComboBox3.insertItem(1, string, user_data)
            self.columnComboBox1.insertItem(1, string, user_data)
            self.columnComboBox2.insertItem(1, string, user_data)
            self.columnComboBox3.insertItem(1, string, user_data)

    ### PRIVATE FUNCTIONS ###

    def _getAvailableColumns(self):
        columns = list()
        for path, dataFrame in self.dataFrames.items():
            for column_name in dataFrame.columns:
                columns.append((path, column_name))
        return columns

    def _addDataFrameByPath(self, path):
        try:
            new_df = DataFrame.from_csv(
                path, index_col=[0], sep=';', parse_dates=False)
            if new_df.shape[1] == 1 or new_df.shape[1] == 0:
                new_df = DataFrame.from_csv(
                    path, index_col=[0], sep=',', parse_dates=False)
        except IndexError:  # index columns not recognized
            new_df = DataFrame.from_csv(
                path, index_col=[0], sep=',', parse_dates=False)
        # print new_df.shape, new_df.columns
        self.dataFrames[path] = new_df
        self.dataFilesList.addItem(path)

    def _fillTableFromDataFrame(self, tableWidget, dataFrame):
        assert isinstance(
            tableWidget, QTableView), "Expected QTableView, got %s" % type(tableWidget)
        assert isinstance(
            dataFrame, DataFrame), "Expected DataFrame, got %s" % type(dataFrame)

        start_time = time.time()
        tableWidget.setModel(None)

        sourceModel = DataFrameModel(dataFrame)
        proxyModel = QSortFilterProxyModel(self)
        proxyModel.setSourceModel(sourceModel)

        for i in xrange(len(dataFrame.columns.tolist())):
            label = str(dataFrame.columns.tolist()[i])
            proxyModel.setHeaderData(i, Qt.Orientation.Horizontal, label)
        tableWidget.setModel(proxyModel)

        end_time = time.time()
        self.statusBar().showMessage(
            "Inserted data in %g" % (end_time - start_time))

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

    # df_dict = {}
    # df = DataFrame.from_csv('/home/paszoste/cp/csv/libCore.so.stat.csv.1')
    # df_dict['/home/paszoste/cp/csv/libCore.so.stat.csv.1'] = df
    # df = DataFrame.from_csv('/home/paszoste/cp/csv/libCore.disas.csv')
    # df_dict['/home/paszoste/cp/csv/libCore.disas.csv'] = df
    # column_tuples = [('/home/paszoste/cp/csv/libCore.disas.csv', u'noperands')]
    # row_tuples = [('/home/paszoste/cp/csv/libCore.so.stat.csv.1', u'XED_ICLASS')]
    # displayed_value = ('/home/paszoste/cp/csv/libCore.so.stat.csv.1', u'execcount')
    # pivot(df_dict, column_tuples, row_tuples, displayed_value)

if __name__ == '__main__':
    main()
