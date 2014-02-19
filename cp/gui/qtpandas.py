'''
Easy integration of DataFrame into pyqt framework

@author: Jev Kuznetsov
'''
from PySide import QtCore, QtGui
from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide.QtGui import (
    QApplication, QDialog, QVBoxLayout, QTableView, QWidget)
QVariant = lambda value=None: value
import pandas
from pandas import DataFrame, Index
from hierarchical_header import HierarchicalHeaderView


class DataFrameModel(QAbstractTableModel):
    ''' data model for a DataFrame class '''
    def __init__(self, parent=None):
        super(DataFrameModel, self).__init__(parent)
        self.df = DataFrame()
        self._horizontalHeaderModel = QStandardItemModel()
        self._verticalHeaderModel = QStandardItemModel()
        self.fillHeaderModel(self._horizontalHeaderModel, df.columns)
        self.fillHeaderModel(self._verticalHeaderModel, df.index)

    def setDataFrame(self, dataFrame):
        self.df = dataFrame

    # def signalUpdate(self):
    #     ''' tell viewers to update their data (this is full update, not
    #     efficient)'''
    #     self.layoutChanged.emit()

    def fillHeaderModel(self, headerModel, index):
        from collections import defaultdict
        if isinstance(index, pandas.MultiIndex):
            label_tuples = index.tolist()
            nodes_tree = {} # {((1,2), 'a'), ...}]
            print label_tuples
            for tuple_ in label_tuples:
                print "tuple"
                for level, label in enumerate(tuple_):
                    print level, label
                    #check if a node with this path on this level is 
                    if (level, tuple_[:level+1]) not in nodes_tree.keys():
                        cell = QStandardItem(label)
                        nodes_tree[(level, tuple_[:level+1])] = cell
                        if level == 0:
                            pass
                            #headerModel.invisibleRootItem().appendColumn([cell])
                        else:
                            pass
                            # root = nodes_tree[(level-1, tuple_[:level])]
                            # root.appendColumn([cell])

        elif isinstance(index, pandas.Int64Index) or \
             isinstance(index, pandas.Float64Index):
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
            print type(index), index
    
    def data(self, index, role):
        if role == Qt.UserRole:
            return self._horizontalHeaderModel
        elif role == Qt.UserRole+1:
            return self._verticalHeaderModel
        else:
            if not index.isValid():
                return QVariant()
            elif role == Qt.DisplayRole and index.isValid():
                return str(self.df.iloc[index.row(), index.column()])

    def rowCount(self, index=QModelIndex()):
        return self.df.shape[0]

    def columnCount(self, index=QModelIndex()):
        return self.df.shape[1]


class DataFrameWidget(QTableView):
    ''' a simple widget for using DataFrames in a gui '''
    def __init__(self, dataFrame=None, parent=None):
        super(DataFrameWidget, self).__init__(parent)

        self.dataModel = DataFrameModel()
        self.dataModel.setDataFrame(dataFrame)
        horizontalHeaderView = HierarchicalHeaderView(QtCore.Qt.Horizontal, self)
        self.setHorizontalHeader(horizontalHeaderView)
        verticalHeaderView = HierarchicalHeaderView(QtCore.Qt.Vertical, self)
        self.setVerticalHeader(verticalHeaderView)
        self.setModel(self.dataModel)

def testDf():
    ''' creates test dataframe '''
    import pandas as pd
    import numpy as np
    cols = pd.MultiIndex.from_arrays([["foo", "foo", "bar", "bar"], ["a", "b", "c", "d"]])
    df = pd.DataFrame(np.random.randn(5, 4), index=range(4,9), columns=cols)
    return df

if __name__ == '__main__':
    import sys
    import numpy as np

    app = QApplication(sys.argv)
    # df = testDf()  # make up some data
    df = DataFrame.from_csv('../fullcms.csv', index_col=[0,1,2], sep=',')
    # print df.columns
    # print df.index
    widget = DataFrameWidget(df)
    widget.show()
    app.exec_()
