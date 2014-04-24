#!/usr/bin/env python

from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtUiTools import QUiLoader
from istateful import IStateful


class PivotComboBox(QComboBox, IStateful):

    def __init__(self, parent=None):
        super(PivotComboBox, self).__init__(parent)
        self.role = None
        self.level = None
        self.disabledRows = []
        self.previous_index = None

        self.insertItem(0, "", None)

    def clear(self):
        super(PivotComboBox, self).clear()
        self.insertItem(0, "", None)

    def enableItem(self, row):
        if row not in self.disabledRows:
            return
        toEnableIndex = self.model().index(row, 0)
        self.model().setData(toEnableIndex, 1 | 32, Qt.UserRole - 1)
        del self.disabledRows[self.disabledRows.index(row)]

    def enableAllItems(self):
        for idx in xrange(self.count()):
            self.enableItem(idx)

    def disableItem(self, row):
        toDisableIndex = self.model().index(row, 0)
        self.model().setData(toDisableIndex, 0, Qt.UserRole - 1)
        self.disabledRows.append(row)

    def mousePressEvent(self, event):
        self.previous_index = self.currentIndex()
        super(PivotComboBox, self).mousePressEvent(event)

    def previousIndex(self):
        return self.previous_index

    def getState(self):
        row_count = self.model().rowCount()
        items = []
        for idx in xrange(1, row_count):
            items.append((self.itemText(idx), self.itemData(idx)))
        return [self.role,
                self.level,
                self.disabledRows,
                self.previous_index,
                self.currentIndex(),
                self.isEnabled(),
                items]

    def setState(self, state):
        self.clear()
        (self.role,
            self.level,
            self.disabledRows,
            self.previous_index,
            current_index,
            is_enabled,
            items) = state
        for item in reversed(items):
            self.insertItem(
                1,
                item[0],
                item[1])  # insert at #1, #0 is taken by ""
        self.setCurrentIndex(current_index)
        self.setEnabled(is_enabled)
