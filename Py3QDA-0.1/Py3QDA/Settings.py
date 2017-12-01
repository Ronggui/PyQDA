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


class Ui_Dialog_settings(QtWidgets.QDialog):#add in dialog object
    """ Basic settings for the coder name, coder table and to display ids.
    Font type and size not implemented yet - so commented out. """

    settings = {}
    thisDialog = None  # important need this to close on overriden accept

    def __init__(self, settings, parent=None):
        self.settings = settings

        super(QtWidgets.QDialog, self).__init__(parent)  # use this to overrride accept method

    def accept(self):
        self.settings['codername'] = str(self.lineEdit_coderName.text()).encode('raw_unicode_escape')
        '''self.settings['font'] = str(self.fontComboBox.currentText()).encode('raw_unicode_escape')
        self.settings['size'] = self.spinBox.value()
        '''
        if self.checkBox.isChecked():
            self.settings['showIDs'] = True
        else:
            self.settings['showIDs'] = False
        if self.radioButton_coder1.isChecked():
            self.settings['codertable'] = "coding"
        else:
            self.settings['codertable'] = "coding2"
        self.thisDialog.accept()

    def setupUi(self, Dialog_settings):
        Dialog_settings.setObjectName(_fromUtf8("Dialog_settings"))
        Dialog_settings.resize(378, 244)
        self.thisDialog = Dialog_settings #ADDIN
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog_settings)
        self.buttonBox.setGeometry(QtCore.QRect(140, 200, 201, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.lineEdit_coderName = QtWidgets.QLineEdit(Dialog_settings)
        self.lineEdit_coderName.setGeometry(QtCore.QRect(150, 24, 113, 27))
        self.lineEdit_coderName.setObjectName(_fromUtf8("lineEdit_coderName"))
        self.label_coderName = QtWidgets.QLabel(Dialog_settings)
        self.label_coderName.setGeometry(QtCore.QRect(40, 30, 91, 17))
        self.label_coderName.setObjectName(_fromUtf8("label_coderName"))
        '''self.fontComboBox = QtWidgets.QFontComboBox(Dialog_settings)
        self.fontComboBox.setGeometry(QtCore.QRect(30, 150, 229, 27))
        self.fontComboBox.setObjectName(_fromUtf8("fontComboBox"))
        self.spinBox = QtWidgets.QSpinBox(Dialog_settings)
        self.spinBox.setGeometry(QtCore.QRect(270, 150, 71, 27))
        self.spinBox.setMinimum(8)
        self.spinBox.setMaximum(32)
        self.spinBox.setSingleStep(2)
        self.spinBox.setObjectName(_fromUtf8("spinBox"))
        self.label = QtWidgets.QLabel(Dialog_settings)
        self.label.setGeometry(QtCore.QRect(30, 130, 66, 17))
        self.label.setObjectName(_fromUtf8("label"))'''
        self.radioButton_coder1 = QtWidgets.QRadioButton(Dialog_settings)
        self.radioButton_coder1.setGeometry(QtCore.QRect(30, 60, 116, 22))
        self.radioButton_coder1.setObjectName(_fromUtf8("radioButton_coder1"))
        self.radioButton_coder2 = QtWidgets.QRadioButton(Dialog_settings)
        self.radioButton_coder2.setGeometry(QtCore.QRect(150, 60, 116, 22))
        self.radioButton_coder2.setObjectName(_fromUtf8("radioButton_coder2"))
        self.checkBox = QtWidgets.QCheckBox(Dialog_settings)
        self.checkBox.setGeometry(QtCore.QRect(30, 93, 97, 22))
        self.checkBox.setObjectName(_fromUtf8("checkBox"))

        #ADDIN
        self.lineEdit_coderName.setText(self.settings['codername'])
        '''
        if self.settings['font'] != "":
            self.fontComboBox.setCurrentFont(QtWidgets.QFont(self.settings['font']))
        if self.settings['size'] != "":
            self.spinBox.setValue(self.settings['size'])
        '''

        if self.settings['codertable'] == "coding":
            self.radioButton_coder1.setChecked(True)
        else:
            self.radioButton_coder2.setChecked(True)
        if self.settings['showIDs'] is True:
            self.checkBox.setChecked(True)
        else:
            self.checkBox.setChecked(False)
        #END ADDIN

        #self.retranslateUi(Dialog_settings)
        self.buttonBox.accepted.connect(self.accept) #changed
        self.buttonBox.rejected.connect(Dialog_settings.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog_settings)

"""
    def retranslateUi(self, Dialog_settings):
        Dialog_settings.setWindowTitle(QtWidgets.QApplication.translate("Dialog_settings", "Settings", None, QtWidgets.QApplication.UnicodeUTF8))
        self.label_coderName.setText(QtWidgets.QApplication.translate("Dialog_settings", "Coder Name", None, QtWidgets.QApplication.UnicodeUTF8))
        self.radioButton_coder1.setText(QtWidgets.QApplication.translate("Dialog_settings", "Coder 1", None, QtWidgets.QApplication.UnicodeUTF8))
        self.radioButton_coder2.setText(QtWidgets.QApplication.translate("Dialog_settings", "Coder 2", None, QtWidgets.QApplication.UnicodeUTF8))
        #self.label.setText(QtWidgets.QApplication.translate("Dialog_settings", "File Font", None, QtWidgets.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtWidgets.QApplication.translate("Dialog_settings", "Show IDs", None))
"""

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_settings = QtWidgets.QDialog()
    ui = Ui_Dialog_settings({'codername':'coder', 'codertable':'coding','showIDs':True})
    ui.setupUi(Dialog_settings)
    Dialog_settings.show()
    sys.exit(app.exec_())
