# -*- coding: utf-8 -*-

'''
Copyright (c) 2013 Colin Curtain

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Author: Colin Curtain (ccbogel)
https://github.com/ccbogel/PyQDA
'''

from PyQt5 import QtCore, QtGui, QtWidgets
from CodeColors import CodeColors
import re

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class Ui_Dialog_colorselect(QtWidgets.QDialog):
    #ADDIN
    colors = CodeColors()
    prevColorName = None
    selectedColor = None

    def __init__(self, prevColorName, parent=None):
        super(QtWidgets.QDialog, self).__init__(parent)  # use this to overrride accept method
        if prevColorName is not None:
            self.prevColorName = re.sub("\d+", "", prevColorName)  #regex to remove digits present in original RQDA

    def colorSelected(self):
        """ Get colour selection from table widget """
        x = self.tableWidget.currentRow()
        y = self.tableWidget.currentColumn()
        self.selectedColor = self.colors.getSelectorColor(x, y)
        self.label.setText(self.selectedColor['colname'])

        #palette = QtGui.QPalette(self.label)
        palette = QtGui.QPalette()
        c = QtGui.QColor(self.selectedColor["hex"])
        palette.setColor(QtGui.QPalette.Window, c)
        self.label.setPalette(palette)
        self.label.setAutoFillBackground(True)  # very important

    def getColor(self):
        """ Get the selected colour name """
        return self.selectedColor

    def accept(self):
        """ Overrriden accept button """
        self.thisDialog.accept()

    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(400, 333)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(290, 20, 81, 241))
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(50, 40, 151, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.tableWidget = QtWidgets.QTableWidget(Dialog)
        self.tableWidget.setGeometry(QtCore.QRect(30, 90, 346, 227))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setRowCount(10)
        self.tableWidget.setColumnCount(10)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        for i in range (0, 10):
            self.tableWidget.setRowHeight(i, 22)
            self.tableWidget.setColumnWidth(i, 34)
            for j in range (0, 10):
                item = QtWidgets.QTableWidgetItem()
                #item.setFlags(QtCore.Qt.ItemIsSelectable) #ruins selection dont use
                codeColor = self.colors.x11_short[i * 10 + j]
                item.setBackground(QtGui.QBrush(QtGui.QColor(codeColor['hex'])))
                self.tableWidget.setItem(i, j, item)
                if codeColor['colname'] == self.prevColorName:
                    self.label.setText(self.prevColorName)
                    #palette = QtGui.QPalette(self.label)
                    palette = QtGui.QPalette()
                    c = QtGui.QColor(codeColor["hex"])
                    palette.setColor(QtGui.QPalette.Window, c)
                    self.label.setPalette(palette)
                    self.label.setAutoFillBackground(True)  # very important

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.tableWidget.cellClicked.connect(self.colorSelected)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "Colour Selector", None, 1))
        #self.label.setText(QtWidgets.QApplication.translate("Dialog", "_____", None, QtWidgets.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_colorselect("Blue")
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
