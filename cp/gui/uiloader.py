#!/usr/bin/env python

from PySide.QtUiTools import QUiLoader
from PySide.QtCore import QMetaObject

class UiLoader(QUiLoader):
    def __init__(self, baseinstance):
        QUiLoader.__init__(self, baseinstance)
        self.baseinstance = baseinstance
        self.customWidgets = set()

    def createWidget(self, class_name, parent=None, name=''):
        if class_name not in self.availableWidgets():
            print self._customWidgetNames()
            if class_name in self._customWidgetNames():
                print class_name, "1'"
                widgetCls = [cls for cls in self.customWidgets if cls.__name__ == class_name][0]
                widget = widgetCls(parent=parent)
                print widgetCls
                if self.baseinstance:
                    print name
                    # set an attribute for the new child widget on the base
                    # instance, just like PyQt4.uic.loadUi does.
                    setattr(self.baseinstance, name, widget)
                return widget
        if parent is None and self.baseinstance:
            # supposed to create the top-level widget, return the base instance
            # instead
            return self.baseinstance
        else:
            # create a new widget for child widgets
            widget = QUiLoader.createWidget(self, class_name, parent, name)
            if self.baseinstance:
                # set an attribute for the new child widget on the base
                # instance, just like PyQt4.uic.loadUi does.
                setattr(self.baseinstance, name, widget)
            return widget

    def _customWidgetNames(self):
        return map(lambda cls: cls.__name__, self.customWidgets)

    def registerCustomWidget(self, classObj):
        self.customWidgets.add(classObj)


def loadUi(uifile, customWidgets=None, baseinstance=None):
    loader = UiLoader(baseinstance)
    for customWidget in customWidgets:
        loader.registerCustomWidget(customWidget)
    widget = loader.load(uifile)
    QMetaObject.connectSlotsByName(widget)
    return widget