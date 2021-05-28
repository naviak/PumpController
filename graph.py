import math
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import pyqtSlot
from scipy import signal
#app = pg.mkQApp()
from PyQt5.QtWidgets import QWidget


class MultiLine(pg.QtGui.QGraphicsPathItem):
    def __init__(self, x, y):
        self.path = pg.arrayToQPath(x, y)
        pg.QtGui.QGraphicsPathItem.__init__(self, self.path)
        self.setPen(pg.mkPen('w', width=2))

    def shape(self):
        return pg.QtGui.QGraphicsItem.shape(self)

    def boundingRect(self):
        return self.path.boundingRect()


class RGraphWidget(pg.GraphicsLayoutWidget):
    def __init__(self):
        super(RGraphWidget, self).__init__()
        self.x1 = np.arange(0, 1, 0.001)
        self.y1 = np.arange(0, 1, 0.001)
        self.lines = None
        self.w1 = self.addPlot()

    @pyqtSlot(float)
    def pushback_val(self, val):
        self.y1 = np.append(self.y1, val)
        self.y1 = self.y1[1:]
        self.showGraphs()

    def showGraphs(self):
        self.w1.clear()
        self.lines = MultiLine(self.x1, self.y1)
        self.w1.setTitle("Signal")
        self.w1.addItem(self.lines)
