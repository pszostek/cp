'''
Easy integration of DataFrame into pyqt framework

@author: Jev Kuznetsov
'''
from __future__ import print_function
from PySide import QtCore, QtGui
from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtCore import QAbstractTableModel, Qt, QModelIndex
QVariant = lambda value=None: value
import pandas
from itertools import repeat
from pandas import DataFrame, Index
# try:
#     from hierarchical_header import HierarchicalHeaderView
# except ImportError:
#     from HierarchicalHeaderView import HierarchicalHeaderView

from HierarchicalHeaderView import HierarchicalHeaderView
#from hierarchical_header import HierarchicalHeaderView


class DataFrameModel(QAbstractTableModel):

    ''' data model for a DataFrame class '''

    def __init__(self, dataFrame=None, parent=None):
        super(DataFrameModel, self).__init__(parent)
        self.df = dataFrame
        self.sortSection = 0
        self.sortOrder = None
        self._horizontalHeaderModel = QStandardItemModel()
        self._verticalHeaderModel = QStandardItemModel()

    def setDataFrame(self, dataFrame):
        assert dataFrame is not None
        self.df = dataFrame
        print(dataFrame.columns)
        print(dataFrame.index)
        self.fillHeaderModel(self._horizontalHeaderModel, dataFrame.columns)
        self.fillHeaderModel(self._verticalHeaderModel, dataFrame.index)

    # def signalUpdate(self):
    #     ''' tell viewers to update their data (this is full update, not
    #     efficient)'''
    #     self.layoutChanged.emit()

    def fillHeaderModel(self, headerModel, index):
        from collections import defaultdict
        if isinstance(index, pandas.MultiIndex):
            label_tuples = index.tolist()
            max_len = len(label_tuples[0])
            last_items = list(repeat((None, None), max_len))
            for tuple_ in label_tuples:
                for level, label in enumerate(tuple_):
                    last_cell = last_items[level]
                    if last_cell[0] == label: #label is the same
                        continue
                    else:
                        cell = QStandardItem(str(label))
                        if level == 0: # take root item
                            root = headerModel.invisibleRootItem()
                            root.appendColumn([cell])
                        else: # take the parent
                            parent = last_items[level-1][1]
                            parent.appendColumn([cell])
                        last_items[level] = (label, cell)
                        for i in xrange(level+1, max_len): #invalidate the remaining part
                            last_items[i] = (None, None)

        elif isinstance(index, pandas.Int64Index):# or \
                #isinstance(index, pandas.Float64Index):
            rootItem = headerModel.invisibleRootItem()
            for entry in index:
                cell = QStandardItem(str(entry))
                rootItem.appendColumn([cell])
        elif isinstance(index, pandas.Index):
            rootItem = headerModel.invisibleRootItem()
            for entry in index:
                cell = QStandardItem(entry)
                rootItem.appendColumn([cell])
        else:
            pass
            #print(type(index), index)

    def data(self, index, role):
        if role == Qt.DisplayRole and index.isValid():
            return str(self.df.iloc[index.row(), index.column()])
        elif role == Qt.UserRole:
            return self._horizontalHeaderModel
        elif role == Qt.UserRole + 1:
            return self._verticalHeaderModel

    def rowCount(self, index=QModelIndex()):
        return self.df.shape[0]

    def columnCount(self, index=QModelIndex()):
        return self.df.shape[1]

    def sort(self, column, order):
        print("sort")
        if order == self.sortOrder and column == self.sortSection:
            print("skip")
            return
        column_list = self.df.columns.tolist()
        column_tuple = column_list[column]
        if order == Qt.SortOrder.AscendingOrder:
            self.sortOrder = Qt.SortOrder.AscendingOrder
            ascending = True
        else:
            self.sortOrder = Qt.SortOrder.DescendingOrder
            ascending = False
        self.sortSection = column
        self.df.sort([column_tuple], inplace=True, ascending=ascending)
        print(self.df.index)
        topLeft = self.createIndex(0,0)
        bottomRight = self.createIndex(df.shape[0]-1, df.shape[1]-1)
        self._verticalHeaderModel = QStandardItemModel()
        self.fillHeaderModel(self._verticalHeaderModel, df.index)
        self.headerDataChanged.emit(Qt.Orientation.Vertical, 0, df.shape[0]-1)
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, df.shape[1]-1)
        self.wid = DataFrameView(self.df)
        self.wid.resize(250, 150)
        self.wid.setWindowTitle('NewWindow')
        self.wid.show()

        self.layoutChanged.emit()
        self.dataChanged.emit(topLeft, bottomRight)

    def headerData(self, section, orientation, role):
        #print("headerData", orientation, section, role)
        #return "1"
        pass

class DataFrameView(QTableView):

    ''' a simple widget for using DataFrames in a gui '''

    def __init__(self, dataFrame=None, parent=None):
        super(DataFrameView, self).__init__(parent)

        horizontalHeaderView = HierarchicalHeaderView(
            QtCore.Qt.Horizontal,
            self)
        horizontalHeaderView.setClickable(True)
        self.setHorizontalHeader(horizontalHeaderView)

        verticalHeaderView = HierarchicalHeaderView(QtCore.Qt.Vertical, self)
        verticalHeaderView.setClickable(True)
        self.setVerticalHeader(verticalHeaderView)

        if dataFrame is None:
            self.dataModel = None
        else:
            self.setModel(dataFrame=dataFrame)

    def setModel(self, dataFrame):
        assert isinstance(dataFrame, DataFrame)
        assert dataFrame is not None

        self.dataModel = DataFrameModel()
        self.dataModel.setDataFrame(dataFrame)
        self.dataModel.headerDataChanged.connect(self.verticalHeader().headerDataChanged)
        super(DataFrameView, self).setModel(self.dataModel)


def testDf():
    ''' creates test dataframe '''
    import pandas as pd
    import numpy as np
    cols = pd.MultiIndex.from_arrays(
        [["foo", "foo", "bar", "bar"], ["a", "b", "c", "d"]])
    df = pd.DataFrame(np.random.randn(5, 4), index=range(4, 9), columns=cols)
    return df

def testDf1():
    import pandas as pd
    import numpy as np
    arrays = [['bar', 'bar', 'baz', 'baz', 'foo', 'foo', 'qux', 'qux'],
             ['one', 'two', 'one', 'two', 'one', 'two', 'one', 'two']]
    tuples = list(zip(*arrays))
    index = pd.MultiIndex.from_tuples(tuples, names=['first', 'second'])
    df = pd.DataFrame(np.random.randn(3, 8), index=['Aaaa', 'Bbbb', 'Cccc'], columns=index)
    return df


if __name__ == '__main__':
    import sys
    import numpy as np

    app = QApplication(sys.argv)
    #df = testDf1()  # make up some data
    df = DataFrame.from_csv('../fullcms.csv', index_col=[0, 1, 2], sep=',')
    # print df.columns
    # print df.index
    import random
    #rows = random.sample(df.index, 50)
    #df = df.ix[rows]
    df = df[:10]
    widget = DataFrameView(dataFrame=df)
    widget.horizontalHeader().setSortIndicator(-1, Qt.SortOrder.DescendingOrder)
    widget.setSortingEnabled(True)
    widget.show()
    app.exec_()
