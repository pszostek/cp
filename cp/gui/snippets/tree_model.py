from PySide.QtCore import *
from PySide.QtGui import *

class TreeItem(object):
    def __init__(self, data, parent=None):
        self._parent = parent
        self._childItems = []
        self._itemData = data if data else []

    def appendChild(self, child):
        self._childItems.append(child)

    def child(self, row):
        return self._childItems[row]

    def columnCount(self):
        return len(self._itemData)

    def childCount(self):
        return len(self._childItems)

    def data(self, column):
        return self._itemData[column]

    def row(self):
        if self._parent:
            return self._parent._childItems.index(self)
        return 0

    def parent(self):
        return self._parent

class TreeModel(QAbstractItemModel):
    def __init__(self, data, parent=None):
        QAbstractItemModel.__init__(self, parent)
        self._rootItem = TreeItem(None, )
        self._setupModelData(data, self._rootItem)

    def _getRootNodes(self):
        raise NotImplementedError()

    def data(self, index, role):
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()
        return item.data(index.column())

    def flags(self, index):
        if not index.isValid():
            return 0

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._rootItem.data(section)
        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self._rootItem:
            return QModelIndex()
        else:
            return self.createIndex(node.parent.row, 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.interPointer()

        return parentItem.childCount()

    def columnCount(self, parent=None):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self._rootItem.columnCount()

    def _setupModelData(self, lines, parent):
        """ lines is a list of tuples (head, [item1, item2, item3])
        """
        for head, items in lines:
            head_item = TreeItem(head, parent)
            parent.appendChild(head_item)
            for item in items:
                head_item.appendChild(TreeItem(item, head_item))


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    # widget = TreeViewComboBox()
    widget = QComboBox()
    tv = QTreeView(widget)
    tree_model = TreeModel([("A", ['a','b','c']),("B", ['a','b','c'])])
    tv.setModel(tree_model)
    widget.setView(tv)
    widget.setModel(tree_model)
    widget.show()
    app.exec_()