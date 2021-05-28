import serial
import time
import sys
from ui import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QErrorMessage
import serial_ports as sp
import mparser as ps
import graph
running = False
COMPORT = None
stepper_mode = 0


class AThread(QThread):
    def __init__(self, parentwindow):
        super().__init__()
        self.parentwindow = parentwindow

    def run(self):
        while running:
            mg = MyWindow.motors_go
            mg(self.parentwindow)
            time.sleep(0.05)
        self.parentwindow.motors_disable()
        self.parentwindow.ui.label.setText('Motors are stopped')


def start():
    global running
    running = True


def stop():
    global running
    running = False


class MyWindow(QtWidgets.QMainWindow):
    sig = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
        self.ui.pushButton.clicked.connect(self.start_motors)
        self.ui.pushButton_2.clicked.connect(self.stop_motors)
        self.thread = AThread(self)
        self.ui.listWidget.addItems(sp.serial_ports())
        self.ui.listWidget.addItems(sp.serial_ports())
        self.ui.listWidget.itemDoubleClicked.connect(self.changeComPort)
        self.ui.pushButton_4.clicked.connect(self.refresh)
        self.ui.horizontalSlider.setMaximum(100)
        self.ui.horizontalSlider.setMinimum(1)
        self.ui.horizontalSlider.valueChanged.connect(self.set_sm)
        self.comport = None
        self.graphWindow = graph.RGraphWidget()
        self.graphWindow.show()
        self.sig.connect(self.graphWindow.pushback_val)
        self.strr = "6"

    @pyqtSlot()
    def set_sm(self):
        global stepper_mode
        stepper_mode = self.ui.horizontalSlider.value()
        self.ui.label_3.setText(str(stepper_mode))
        self.strr = str(int(100 / (100-stepper_mode))) + 'mm/s'

    @pyqtSlot()
    def start_motors(self):
        self.comport.write('EM,1,1\r'.encode('ascii'))
        self.comport.read_until()
        if not running and COMPORT is not None:
            start()
            self.ui.label.setText('Motors are working')
            self.thread.start()

    @pyqtSlot()
    def stop_motors(self):
        stop()

    @pyqtSlot()
    def changeComPort(self):
        global COMPORT
        COMPORT = self.ui.listWidget.currentItem().text()
        self.ui.label_5.setText(COMPORT)
        self.comport = serial.Serial(COMPORT, timeout=0.05)

    @pyqtSlot()
    def refresh(self):
        self.ui.listWidget.clear()
        self.ui.listWidget.addItems(sp.serial_ports())

    def motors_disable(self):
        try:
            self.comport.write('EM,0,0\r'.encode('ascii'))
            self.comport.read_until()
        except serial.SerialException:
            self.handle_error('could not open port ' + COMPORT)

    def motors_go(self):
        try:
            #print(self.comport.read_until().decode("utf-8"))
            self.comport.write(('SM,100,'+self.strr+','+self.strr+'\r').encode('ascii'))
            self.comport.read_until()
            self.comport.write('AC,4,1\r'.encode('ascii'))
            self.comport.read_until()
            self.comport.write('A\r'.encode('ascii'))
            asm = self.comport.read_until().decode("utf-8")
            pumpval = ps.parseAnalogSignal(asm, 4)
            self.sig.emit(pumpval)

        except serial.SerialException:
            self.handle_error('could not open port ' + COMPORT)

    def handle_error(self, error):
        em = QErrorMessage(self)
        em.showMessage(error)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())