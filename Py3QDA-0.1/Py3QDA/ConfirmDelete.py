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

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class Ui_Dialog_confirmDelete(object):
    """ A generic confirm delete dialog """

    labelText = ""

    def __init__(self, labelText):
        self.labelText = labelText

    def setupUi(self, Dialog_confirmDelete):
        Dialog_confirmDelete.setObjectName(_fromUtf8("Dialog_confirmDelete"))
        Dialog_confirmDelete.resize(400, 243)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog_confirmDelete)
        self.buttonBox.setGeometry(QtCore.QRect(290, 20, 81, 241))
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtWidgets.QLabel(Dialog_confirmDelete)
        self.label.setText(self.labelText)
        self.label.setGeometry(QtCore.QRect(30, 20, 251, 251))
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(Dialog_confirmDelete)
        self.buttonBox.accepted.connect(Dialog_confirmDelete.accept)
        self.buttonBox.rejected.connect(Dialog_confirmDelete.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog_confirmDelete)

    def retranslateUi(self, Dialog_confirmDelete):
        Dialog_confirmDelete.setWindowTitle(QtWidgets.QApplication.translate("Dialog_confirmDelete", "Confirm Delete", None, 1))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_confirmDelete = QtWidgets.QDialog()
    ui = Ui_Dialog_confirmDelete("label")
    ui.setupUi(Dialog_confirmDelete)
    Dialog_confirmDelete.show()
    sys.exit(app.exec_())
