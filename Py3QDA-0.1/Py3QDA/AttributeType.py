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
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)

class Ui_Dialog_attrType(object):
    """ Get user input for attribute type.
    Return is based on whether character or numeric radio button checked
    Called from Attributes.py """

    def setupUi(self, Dialog_attrType):

        Dialog_attrType.setObjectName(_fromUtf8("Dialog_attrType"))
        Dialog_attrType.resize(400, 188)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog_attrType)
        self.buttonBox.setGeometry(QtCore.QRect(160, 130, 211, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.radioButton_char = QtWidgets.QRadioButton(Dialog_attrType)
        self.radioButton_char.setGeometry(QtCore.QRect(30, 60, 116, 22))
        self.radioButton_char.setObjectName(_fromUtf8("radioButton_char"))
        self.radioButton_char.setChecked(True)
        self.buttonGroup = QtWidgets.QButtonGroup(Dialog_attrType)
        self.buttonGroup.setObjectName(_fromUtf8("buttonGroup"))
        self.buttonGroup.addButton(self.radioButton_char)
        self.radioButton_numeric = QtWidgets.QRadioButton(Dialog_attrType)
        self.radioButton_numeric.setGeometry(QtCore.QRect(30, 90, 116, 22))
        self.radioButton_numeric.setObjectName(_fromUtf8("radioButton_numeric"))
        self.buttonGroup.addButton(self.radioButton_numeric)
        self.label = QtWidgets.QLabel(Dialog_attrType)
        self.label.setGeometry(QtCore.QRect(20, 20, 241, 17))
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(Dialog_attrType)
        self.buttonBox.accepted.connect(Dialog_attrType.accept)
        self.buttonBox.rejected.connect(Dialog_attrType.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog_attrType)

    def retranslateUi(self, Dialog_attrType):
        Dialog_attrType.setWindowTitle(_translate("Dialog_attrType", "Choose Attribute Type", None))
        self.radioButton_char.setText(_translate("Dialog_attrType", "Character", None))
        self.radioButton_numeric.setText(_translate("Dialog_attrType", "Numeric", None))
        self.label.setText(_translate("Dialog_attrType", "Choose attribute type:", None))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_attrType = QtWidgets.QDialog()
    ui = Ui_Dialog_attrType()
    ui.setupUi(Dialog_attrType)
    Dialog_attrType.show()
    sys.exit(app.exec_())
