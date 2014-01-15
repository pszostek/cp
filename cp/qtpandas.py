'''
Easy integration of DataFrame into pyqt framework

@author: Jev Kuznetsov
'''

from PySide.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide.QtGui import (
    QApplication, QDialog, QVBoxLayout, QTableView, QWidget)
QVariant = lambda value=None: value
from pandas import DataFrame, Index


class DataFrameModel(QAbstractTableModel):
    ''' data model for a DataFrame class '''
    def __init__(self, parent=None):
        super(DataFrameModel, self).__init__(parent)
        self.df = DataFrame()

    def setDataFrame(self, dataFrame):
        self.df = dataFrame

    def signalUpdate(self):
        ''' tell viewers to update their data (this is full update, not
        efficient)'''
        self.layoutChanged.emit()

    #------------- table display functions -----------------
    def headerData(self, section, orientation, role=None):
        if role is None:
            role = Qt.DisplayRole
        if role != Qt.DisplayRole:
            return QVariant()

        if orientation == Qt.Horizontal:
            try:
                return self.df.columns.tolist()[section]
            except (IndexError, ):
                return QVariant()
        elif orientation == Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return str(self.df.index.tolist()[section])
            except (IndexError, ):
                return QVariant()

    def data(self, index, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()

        if not index.isValid():
            return QVariant()
        return str(self.df.iloc[index.row(), index.column()])

    def flags(self, index):
            flags = super(DataFrameModel, self).flags(index)
            flags |= Qt.ItemIsEditable
            return flags

    def setData(self, index, value, role):
        row = self.df.index[index.row()]
        col = self.df.columns[index.column()]
        if hasattr(value, 'toPyObject'):
            # PyQt4 gets a QVariant
            value = value.toPyObject()
        else:
            # PySide gets an unicode
            dtype = self.df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        self.df.set_value(row, col, value)
        return True

    def rowCount(self, index=QModelIndex()):
        return self.df.shape[0]

    def columnCount(self, index=QModelIndex()):
        return self.df.shape[1]


class DataFrameWidget(QWidget):
    ''' a simple widget for using DataFrames in a gui '''
    def __init__(self, dataFrame=None, parent=None):
        super(DataFrameWidget, self).__init__(parent)

        self.dataModel = DataFrameModel()
        self.dataTable = QTableView(parent)
        self.dataTable.setModel(self.dataModel)

        layout = QVBoxLayout()
        layout.addWidget(self.dataTable)
        self.setLayout(layout)
        # Set DataFrame
        self.setDataFrame(dataFrame)

    def setDataFrame(self, dataFrame):
        self.dataModel.setDataFrame(dataFrame)
        self.dataModel.signalUpdate()
        self.dataTable.resizeColumnsToContents()

    def resizeColumnsToContents(self):
        self.dataTable.resizeColumnsToContents()
#-----------------stand alone test code


def testDf():
    ''' creates test dataframe '''
    import pandas as pd
    import numpy as np
    cols = pd.MultiIndex.from_arrays([["foo", "foo", "bar", "bar"], ["a", "b", "c", "d"]])
    df = pd.DataFrame(np.random.randn(5, 4), index=range(5), columns=cols)
    return df

class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        df = testDf()  # make up some data
        widget = DataFrameWidget(df)
        widget.resizeColumnsToContents()

        layout = QVBoxLayout()
        layout.addWidget(widget)
        self.setLayout(layout)

if __name__ == '__main__':
    import sys
    import numpy as np

    app = QApplication(sys.argv)
    form = Form()
    form.show()
    app.exec_()
