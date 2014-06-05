'''
Easy integration of DataFrame into pyqt framework

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
from collections import deque
# try:
#     from hierarchical_header import HierarchicalHeaderView
# except ImportError:
#     from HierarchicalHeaderView import HierarchicalHeaderView

#from HierarchicalHeaderView import HierarchicalHeaderView
from hierarchical_header import HierarchicalHeaderView

class DataFrameModel(QAbstractTableModel):

    ''' data model for a DataFrame class '''

    def __init__(self, dataFrame=None, parent=None):
        super(DataFrameModel, self).__init__(parent)
        self.df = dataFrame
        if dataFrame is not None:
            self.setDataFrame(dataFrame)
        self.sortSection = 0
        self.sortOrder = None
        self._horizontalHeaderModel = QStandardItemModel()
        self._verticalHeaderModel = QStandardItemModel()

    def setDataFrame(self, dataFrame):
        assert dataFrame is not None
        self.modelAboutToBeReset.emit()
        self.df = dataFrame

        self._horizontalHeaderModel = QStandardItemModel()
        # self._horizontalHeaderModel.modelAboutToBeReset.emit()
        # self._horizontalHeaderModel.beginResetModel()
        # self._horizontalHeaderModel.reset()
        # self._horizontalHeaderModel.endResetModel()
        # print(dataFrame.columns)
        self.fillHeaderModel(self._horizontalHeaderModel, dataFrame.columns)
        self._horizontalHeaderModel.modelReset.emit()

        self._verticalHeaderModel = QStandardItemModel()
        # self._verticalHeaderModel.modelAboutToBeReset.emit()
        # self._verticalHeaderModel.beginResetModel()
        # self._verticalHeaderModel.reset()
        # self._verticalHeaderModel.endResetModel()
        # print(dataFrame.index)
        self.fillHeaderModel(self._verticalHeaderModel, dataFrame.index)
        self._verticalHeaderModel.modelReset.emit()
        self.modelReset.emit()
        self.headerDataChanged.emit(Qt.Vertical, 0, 1)
        self.headerDataChanged.emit(Qt.Horizontal, 0, 1)

    # def signalUpdate(self):
    #     ''' tell viewers to update their data (this is full update, not
    #     efficient)'''
    #     self.layoutChanged.emit()

    def fillHeaderModel(self, headerModel, index):
        from collections import defaultdict
        from pandas import Int64Index
        try:
            from pandas import Float64Index
        except:
            Float64index = Int64Index

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

        elif isinstance(index, Int64Index) or\
                isinstance(index, Float64Index):
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
    def dataInt(self, index):
        return self.df.iloc[index.row(), index.column()]

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
        if order == self.sortOrder and column == self.sortSection:
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
        topLeft = self.createIndex(0,0)
        bottomRight = self.createIndex(self.df.shape[0]-1, self.df.shape[1]-1)
        self._verticalHeaderModel = QStandardItemModel()
        self.fillHeaderModel(self._verticalHeaderModel, self.df.index)
        self.headerDataChanged.emit(Qt.Orientation.Vertical, 0, 1000)#self.df.shape[0]-1)
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, 1000)#self.df.shape[1]-1)
        # self.wid = DataFrameView(self.df)
        # self.wid.resize(250, 150)
        # self.wid.setWindowTitle('NewWindow')
        # self.wid.show()

        self.layoutChanged.emit()
        self.dataChanged.emit(topLeft, bottomRight)

    def headerData(self, section, orientation, role):
        #just to display in a normal QTableView
        if role == Qt.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.df.columns[section]
            elif orientation == Qt.Orientation.Vertical:
                return self.df.index[section] 

    def getMinimum(self):
        return self.df.min()

    def getMaximum(self):
        return self.df.max()

    def setHeaderData(self, section, orientation, value, role):
        print("setHeaderData")
        super(DataFrameModel, self).setHeaderData(section, orientation, value, role)


class ColorDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ColorDelegate, self).__init__(parent)
        self._minimum = None
        self._maximum = None

    def paint(self, painter, option, index):
        if self._minimum is None:
            self._minimum = index.model().getMinimum()
        if self._maximum is None:
            self._maximum = index.model().getMaximum()
        value = index.model().dataInt(index)/max(self._maximum)
        if value == 0:
            red = green = blue = 0
        if 1/8 <= value and value > 0:
            red = 0
            green = 0
            blue = 4*value + .5
        elif 1/8 < value and value <= 3/8:
            red = 0
            green = 4*value - .5
            blue = 0
        elif 3/8 < value and value <= 5/8:
            red = 4*value - 1.5
            green = 1
            blue = -4*value + 2.5
        elif (5/8 < value and value <= 7/8):
            red = 1
            green = -4*value + 3.5
            blue = 0
        elif (7/8 < value and value <= 1):
            red = -4*value + 4.5
            green = 0
            blue = 0
        else:
            red = .5
            green = 0
            blue = 0
        background = QtGui.QColor.fromRgb(255*red, 255*green, 255*blue, 100)
        painter.fillRect(option.rect, background)
        super(ColorDelegate, self).paint(painter, option, index)

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
            self.setDataFrame(dataFrame=dataFrame)

    def setModel(self, model):
        assert isinstance(model, DataFrameModel) or (model is None)
        super(DataFrameView, self).setModel(model)

    def setDataFrame(self, dataFrame):
        assert isinstance(dataFrame, DataFrame) or (dataFrame is None)
        if dataFrame is not None:
            # if self.dataModel is None:
            #     self.dataModel = DataFrameModel()
            # self.dataModel.setDataFrame(dataFrame)
            self.dataModel = DataFrameModel()
            self.dataModel.setDataFrame(dataFrame)
            print(dataFrame)
            self.dataModel.headerDataChanged.connect(self.verticalHeader().headerDataChanged)
            self.update()

        super(DataFrameView, self).setModel(self.dataModel)

    def getDataFrame(self):
        return self.dataModel.df


def testDf():
    ''' creates test dataframe '''
    import numpy as np
    cols = pandas.MultiIndex.from_arrays(
        [["foo", "foo", "bar", "bar"], ["a", "b", "c", "d"]])
    df = pandas.DataFrame(np.random.randn(5, 4), index=range(4, 9), columns=cols)
    return df

def testDf1():
    import numpy as np
    arrays = [['bar', 'bar', 'baz', 'baz', 'foo', 'foo', 'qux', 'qux'],
             ['one', 'two', 'one', 'two', 'one', 'two', 'one', 'two']]
    tuples = list(zip(*arrays))
    index = pandas.MultiIndex.from_tuples(tuples, names=['first', 'second'])
    df = pandas.DataFrame(np.random.randn(3, 8), index=['Aaaa', 'Bbbb', 'Cccc'], columns=index)
    return df

def testDf2():
    ''' creates test dataframe '''
    import numpy as np
    cols = pandas.MultiIndex.from_arrays([["a"],["b"]])
    df = pandas.DataFrame(np.random.randn(5, 1), index=range(4, 9), columns=cols)
    return df


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    # df = testDf2()  # make up some data
    # df = DataFrame.from_csv('../fullcms.csv', index_col=[0, 1, 2], sep=',')
    # print df.columns
    # print df.index
    #rows = random.sample(df.index, 50)
    #df = df.ix[rows]
    # df = df[:1000]
    df = DataFrame.from_csv("../view1.csv", index_col=[0,1])
    widget = DataFrameView()
    widget.setDataFrame(df)
    widget.horizontalHeader().setSortIndicator(-1, Qt.SortOrder.DescendingOrder)
    widget.setSortingEnabled(True)
    widget.show()
    app.exec_()
