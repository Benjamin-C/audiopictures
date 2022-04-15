from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import * # Qt,QTimer

from os import listdir
from os.path import isfile, isdir, join

import time

# The user's home directory
from os.path import expanduser
HOME = expanduser("~")

import sys

app = QApplication([])

# Force the style to be the same on all OSs:
app.setStyle("gtk2")

# Now use a palette to switch to dark colors:
palette = QPalette()
palette.setColor(QPalette.Window, QColor(53, 53, 53))
palette.setColor(QPalette.WindowText, Qt.white)
palette.setColor(QPalette.Base, QColor(25, 25, 25))
palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
palette.setColor(QPalette.ToolTipBase, Qt.white)
palette.setColor(QPalette.ToolTipText, Qt.white)
palette.setColor(QPalette.Text, Qt.white)
palette.setColor(QPalette.Button, QColor(53, 53, 53))
palette.setColor(QPalette.ButtonText, Qt.white)
palette.setColor(QPalette.BrightText, Qt.red)
palette.setColor(QPalette.Link, QColor(42, 130, 218))
palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
palette.setColor(QPalette.HighlightedText, Qt.black)
app.setPalette(palette)

app.setApplicationName("Image Singer")

def strTime(seconds):
    seconds = round(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    str = (f'{h:d}' if (h > 0) else '') + f'{m:02d}:{s:02d}'
    return str

num = 0

class MyPopup(QWidget):
    def __init__(self, btn, parent = None, widget=None):
        QWidget.__init__(self, parent)
        layout = QGridLayout(self)
        testlabel = QLabel()
        testlabel.setText(f"{btn.x}, {btn.y}: {btn.val} & {btn.amp}")
        layout.addWidget(testlabel)

        # adjust the margins or you will get an invisible, unintended border
        layout.setContentsMargins(0, 0, 0, 0)

        # need to set the layout
        self.setLayout(layout)
        self.adjustSize()

        # tag this widget as a popup
        self.setWindowFlags(Qt.Popup)

        # calculate the botoom right point from the parents rectangle
        point = btn.rect().bottomLeft()

        # map that point as a global position
        global_point = btn.mapToGlobal(point)

        # by default, a widget will be placed from its top-left corner, so
        # we need to move it to the left based on the widgets width
        self.move(global_point - QPoint(0, 0))

# Main window class
class MainWindow(QMainWindow):

    px = []

    def __init__(self, width, height, parent=None):
        super(MainWindow, self).__init__(parent)
        verticalLayout = QVBoxLayout()

        # self.testlabel = QLabel()
        # self.testlabel.setText("Hello!")
        # verticalLayout.addWidget(self.testlabel)

        grid = QGridLayout()

        for i in range(height):
            self.px.append([])
            for j in range(width):
                button = QPushButton(" ",self)
                self.px[i].append(button)
                self.setBtnColor(i, j,0)
                self.setBtnInfo(i, j, "", "")
                button.setStyleSheet("font-size:40px;background-color:#000000;border: 2px solid #222222")
                button.setFixedSize(24,24)
                button.clicked.connect(self.Button)
                button.x = j;
                button.y = i;
                grid.addWidget(button,i,j)


        # def self_pauseVideo():
        #     print("Pause!")
        # self.pauseButton = QPushButton("Do something!")
        # verticalLayout.addWidget(self.pauseButton)
        # self.pauseButton.clicked.connect(self_pauseVideo)

        mainWidget = QWidget()
        mainWidget.setLayout(grid)
        self.setCentralWidget(mainWidget)
        self.setGeometry(1920+100,100,0,0)

    def Button(self):
        snd = self.sender()
        self.w = MyPopup(snd)
        self.w.show()

    def setBtnColor(self, row, col, val):
        self.px[row][col].setStyleSheet(f"font-size:40px;background-color:#{val:02X}{val:02X}{val:02X};border: 2px solid #222222")

    def setBtnInfo(self, row, col, val, amp):
        self.px[row][col].val = val;
        self.px[row][col].amp = amp;

if __name__ == '__main__':
    window = MainWindow(6, 6)

    print('Got here')

    print("This application must be closed from the window, ctl+c will not work.")
    window.show()
    app.exec_()
