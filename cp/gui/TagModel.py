
import tags.tag, symcollector.fncollector
import pandas
from PySide import QtGui, QtCore
#import gui.hierarchical_header.HierarchicalHeaderView 
from gui.HierarchicalHeaderView import HierarchicalHeaderView

class TagHeaderModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super(TagHeaderModel, self).__init__()
    def rowCount(self, parent=QtCore.QModelIndex()):
        return 3
    def columnCount(self, parent=QtCore.QModelIndex()):
        return 3
    def headerData(self, section, orientation, role):
        pass
    def data(self, index, role=QtCore.Qt.DisplayRole):
        print("called data")
        if role == HierarchicalHeaderView.HorizontalHeaderDataRole:
            print("hier role in tag header data")
            horizmodel = QtGui.QStandardItemModel()
            self.protect = [horizmodel]
            elements = QtGui.QStandardItem("Elements")
            horizmodel.appendColumn([elements])
            cycles = QtGui.QStandardItem("Cycles")
            horizmodel.appendColumn([cycles])
            #cycles.appendColumn([QtGui.QStandardItem("SIMD")])
            #cycles.appendColumn([QtGui.QStandardItem("NON SIMD")])

            misses = QtGui.QStandardItem("Cache misses")
            #misses.appendColumn([QtGui.QStandardItem("SIMD")])
            #misses.appendColumn([QtGui.QStandardItem("NON SIMD")])
            horizmodel.appendColumn([misses])
            return horizmodel        
        if role == QtCore.Qt.DisplayRole:
            i = index.row()
            j = index.column()
            return "row {0} column {1}".format(i, j)
        else:
            return None 
    


class TagItem(object):
    def __init__(self, tag, parent=None, rowIndexInParent=0):
        self._parent = parent
        self._tag = tag
        self._rowIndexInParent = rowIndexInParent
    def row(self):
        return self._rowIndexInParent
    def child(self, row):
        if len(self._tag.children) <= row:
            return None
        return TagItem(self._tag.children[row], self, row)
    def data(self, column):
        if column == 0:
            return self._tag.label
        return self._tag.getSamples()[column]
    def getParent(self):
        return self._parent 
    def childCount(self):
        return len(self._tag.children)

class TagModel(QtCore.QAbstractItemModel):
    def __init__(self, rootTag, parent=None):
        super(TagModel, self).__init__()
        #self.tags = tags
        df = symcollector.fncollector.getFunctions("../simple-binary/shapes/a.out")
        #df = symcollector.fncollector.getFunctions("/home/gbitzes/feather/bin/tests")
        #self.rootTag = tags.tag.functionTag(df)
        self.rootTag = tags.tag.classTag(df)
        dynamic = pandas.DataFrame.from_csv("fakedata_shapes.csv")
        dynamic = dynamic.reset_index()
        dynamic = tags.tag.makeCumulative(dynamic)
        self.rootTag2 = tags.tag.Tag(0, 0, "ROOT TAG")
        self.rootTag2.addChild(self.rootTag)
        self.rootTag2.finalize(dynamic)
        self.rootItem = TagItem(self.rootTag2)
        self.protectFromTheWrathOfGC = []
    #def data(self, index, role=QtCore.Qt.DisplayRole):
    #    if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
    #        return 1337
    #    return None
    #def headerData(self, section, orientation, role):
    #    if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
    #        return section
    #
    #    if role == HierarchicalHeaderView.HorizontalHeaderDataRole:
    #        print("hier role in header data")

    #    if role == QtCore.Qt.DisplayRole:
    #        if orientation == QtCore.Qt.Horizontal:
    #            if section == 0:
    #                horizmodel = QtGui.QStandardItemModel()
    #                firstlvl = []
    #                rootItem = QtGui.QStandardItem()
    #                item = QtGui.QStandardItem()
    #                item.setText("aaa")
    #                firstlvl.append(item)
    #                rootItem.appendColumn(firstlvl)
    #                #item = QtGui.QStandardItem()
    #                #item.setText("aa")
    #                #rootItem.appendColumn(item)
    #                #item = QtGui.QStandardItem()
    #                #rootItem.appendColumn(item)
    #                horizmodel.setItem(0, 0, rootItem)
    #                return horizmodel
    #                return "adfaf"
    #            if section == 1:
    #                return "ghgdhdh"
    #            if section == 2:
    #                return "lkfhaklfh" 
    #    return None

    def columnCount(self, index=QtCore.QModelIndex()):
        return 5
    def rowCount(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            parent = self.rootItem
        else:
            parent = parent.internalPointer()
        return parent.childCount()        
    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
 
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
    def data(self, index, role):
        if not index.isValid():
            return None
        if role != QtCore.Qt.DisplayRole:
            return None
        
        item = index.internalPointer()
        return item.data(index.column()) 
    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        if childItem == self.rootItem:
            return QtCore.QModelIndex()
        parentItem = childItem.getParent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()
        return self.createIndex(parentItem.row(), 0, parentItem)
    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        if not parent.isValid():
           parentItem = self.rootItem 
        else:
           parentItem = parent.internalPointer()
        childItem = parentItem.child(row)
        if childItem:
            newindex = self.createIndex(row, column, childItem)
            internal = newindex.internalPointer()
            self.protectFromTheWrathOfGC.append(internal)
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

