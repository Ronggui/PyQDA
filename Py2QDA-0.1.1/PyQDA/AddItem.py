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

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog_addItem(QtGui.QDialog):
    """
    Dialog to get a new code or code category from user.
    Requires a label for Dialog title and label in setupUI
    Requires a list of dictionary 'name' items.
    Dialog returns ok if the item is not a duplicate of a name in the list.
    Returns one item through getnewItem method.
    """
    #ADDIN
    newItem = None
    existingItems = []
    Dialog_addItem = None
    typeOfItem = "" # for dialog title and label: Code or Category

    def __init__(self, items, parent=None):
        super(QtGui.QDialog, self).__init__(parent) # use this to overrride accept method
        for i in items:
            self.existingItems.append(i['name'])

    def accept(self):
        """ On pressing accept button, check there is no duplicate.
        If no duplicate then accept end close the dialog """

        thisItem = str(self.lineEdit.text())
        duplicate = False
        if thisItem in self.existingItems:
            duplicate = True
            QtGui.QMessageBox.warning(None, "Duplicated", "This already exists", QtGui.QMessageBox.Ok)
        if duplicate==False:
            self.newItem = thisItem
        self.Dialog_addItem.accept()

    def getNewItem(self):
        """ Get the new code or category text """

        return self.newItem

    #END

    def setupUi(self, Dialog_addItem, typeOfItem):
        self.typeOfItem = typeOfItem #ADDIN
        self.Dialog_addItem = Dialog_addItem #ADDIN
        Dialog_addItem.setObjectName(_fromUtf8("Dialog_addItem"))
        Dialog_addItem.resize(400, 142)
        self.lineEdit = QtGui.QLineEdit(Dialog_addItem)
        self.lineEdit.setGeometry(QtCore.QRect(20, 40, 351, 27))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.label = QtGui.QLabel(Dialog_addItem)
        self.label.setGeometry(QtCore.QRect(20, 20, 100, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.buttonBox = QtGui.QDialogButtonBox(Dialog_addItem)
        self.buttonBox.setGeometry(QtCore.QRect(170, 90, 201, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

        self.retranslateUi(Dialog_addItem)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog_addItem.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog_addItem)

    def retranslateUi(self, Dialog_addItem):
        Dialog_addItem.setWindowTitle(QtGui.QApplication.translate("Dialog_addCode", "Add "+self.typeOfItem, None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog_addCode", self.typeOfItem+":", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog_addItem = QtGui.QDialog()
    ui = Ui_Dialog_addItem()
    ui.setupUi(Dialog_addItem)
    Dialog_addItem.show()
    sys.exit(app.exec_())

