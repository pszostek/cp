#!/usr/bin/python2
# -*- coding: utf-8 -*-
from __future__ import division
import sys
import random

from PySide import QtCore
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtGui import QApplication
color = 0
colors = [("#ff7f2a", "#ffb380"),
          ("#ffd42a", "#ffe680"),
          ("#abc837", "#dde9af"),
          ("#2affd5", "#80ffe6"),
          ("#6600ff", "#b380ff")]

class MyGraphicsScene(QGraphicsScene):
    def __init__(self, parent):
        QGraphicsScene.__init__(self, parent)
        self.mousePos = None

    def drawForeground(self, painter, rect):
        QGraphicsScene.drawForeground(self, painter, rect)
        sceneRect = self.sceneRect()
        painter.setPen(QPen(Qt.black, 1))
        if self.mousePos:
          #  if self.mousePos.y() != -1:
          #      painter.drawLine(sceneRect.left(), self.mousePos.y(), sceneRect.right(), self.mousePos.y())
            painter.drawLine(self.mousePos.x(), sceneRect.top(), self.mousePos.x(), sceneRect.bottom())
    def onMouseChanged(self, newMousePos):
        self.mousePos = newMousePos
        self.invalidate()

class MyGraphicsView(QGraphicsView):
    mousePosChanged = QtCore.Signal(QPoint)
    def __init__(self, parent=None):
        QGraphicsView.__init__(self, parent)
        self.setMouseTracking(True)

        sizePolicy = QSizePolicy()
        sizePolicy.setHorizontalPolicy(QSizePolicy.Maximum)
        sizePolicy.setVerticalPolicy(QSizePolicy.Fixed)
        self.setSizePolicy(sizePolicy)

    def mouseMoveEvent(self, pEvent):
        mousePos = self.mapToScene(pEvent.pos())
        self.mousePosChanged.emit(mousePos.toPoint())

class TimePlot(QWidget):
    mousePosChanged = QtCore.Signal(QPoint)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.data = None
        self.width = 1000
        self.height = 20

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(QMargins(0,0,0,0))
        #self.layout.setSpacing(0)
        self.layout.invalidate()
        self.setFixedHeight(self.height)
        self.setLayout(self.layout)

        self.view = MyGraphicsView(self)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.scene = MyGraphicsScene(self)
        self.scene.setSceneRect(QRect(0,0,self.width, self.height))
        self.view.setScene(self.scene)
        self.view.resize(self.width, self.height)

        self.view.mousePosChanged.connect(self.scene.onMouseChanged)
        self.view.mousePosChanged.connect(self.onMouseChanged)
        mirrorTransform = QTransform()
        mirrorTransform.scale(1, -1) 
        self.view.setTransform(mirrorTransform)
       
        #this has no influence on the size:
        sizePolicy = QSizePolicy()
        sizePolicy.setHorizontalPolicy(QSizePolicy.Maximum)
        sizePolicy.setVerticalPolicy(QSizePolicy.Fixed)
        self.setSizePolicy(sizePolicy)


        self.layout.addWidget(self.view)
      #  self.view.setSceneRect(0, 0, self.width, self.height*0.1)
      #  self.view.show()

    def onMouseChanged(self, point):
        self.mousePosChanged.emit(point)

    def onOtherPlotMouseChanged(self, point):
        self.scene.onMouseChanged(QPoint(point.x(), -1))
    
    def sizeHint(self):
        return QSize(self.width, self.height)

    def setData(self, data):
        self.data = data
        self.scene.clear()
        self._redraw()

    def _redraw(self):
        countourPen = QPen(QBrush(QColor(colors[color][0])), 2)
        fillBrush = QBrush(QColor(colors[color][1]))

        sortedData = sorted(self.data, key=lambda x: x[0])
        data = self._integrate(sortedData)
        maxXValue = max(item[0] for item in data)
        maxYValue = max(item[1] for item in data)

        # scale to match the whole viewport
        polygonPoints = map(lambda p: QPoint(*p), data)
        polygonPoints.append(QPoint(data[len(data)-1][0], 0))
        polygonCoords = QPolygon(polygonPoints)

        scaleVertically = QTransform()
        scaleVertically.scale(self.width/(maxXValue), self.height/ (maxYValue))
        scaledPoly = scaleVertically.map(polygonCoords)

        # make a path form the polygon
        plotPath = QPainterPath()
        plotPath.addPolygon(scaledPoly)
        polyFromPath = plotPath.toFillPolygon()
        self.scene.addPolygon(polyFromPath, countourPen, fillBrush)
        print "drawn"

    def _integrate(self, data):
        windowSize = 10 
        added = []
        # slide with a window of size windowSize through the data
        # and for each data point count number of surrounding events
        # in the window
        for idx, point in enumerate(data):
            count = 0
            for lower_idx in reversed(xrange(0, idx)):
                if abs(data[lower_idx][0]-point[0]) <= windowSize/2:
                    count += 1
                else:
                    break
            for higher_idx in xrange(idx+1, len(data)):
                if abs(data[higher_idx][0]-point[0]) <= windowSize/2:
                    count += 1
                else:
                    break
            added.append((point[0], count))
        prevPoint = (0,0)
        ret = []
        for point in added:
            if point[1] == prevPoint[1]:
                pass
            else:
                ret.append(prevPoint)
            prevPoint = point
        return ret

    def show(self):
        self.view.show()

app = QApplication(sys.argv)
window = QWidget()
verticalLayout = QVBoxLayout(window)
verticalLayout.setContentsMargins(QMargins(0,0,0,0))
verticalLayout.setSpacing(0)
verticalLayout.invalidate()
verticalLayout.update()
plots = []
for _ in xrange(0,5):
   data = [(random.random()*1000, random.random()*10%1) for _ in xrange(0, 1000)]
   timePlot = TimePlot(window)
   timePlot.setData(data)
   plots.append(timePlot)
   verticalLayout.addWidget(timePlot)
   color += 1
   #timePlot.show()
for p1 in plots:
    for p2 in plots:
        if p1 is not p2:
            p1.mousePosChanged.connect(p2.onOtherPlotMouseChanged)
            p2.mousePosChanged.connect(p1.onOtherPlotMouseChanged)

window.setLayout(verticalLayout)
window.show()
app.exec_()
