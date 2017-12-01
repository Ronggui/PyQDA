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


class Ui_Dialog_selectfile(object):
    """
    Requires a list of dictionaries. This list must have a dictionary item called 'name' which is
     displayed to the user.
    The setupui method requires a title string for the dialog title and a selection mode:
    "single" or any other text which equates to many.

    User selects one or more names from the list depending on selection mode.
    getSelected method returns the selected dictionary object(s).
    """

    dictList = None
    selectedname = None
    title = None

    def __init__(self, data):
        self.dictList = data

    def getSelected(self):
        """ Get a selected dictionary  or a list of dictionaries depending on the selection mode.
        """

        if self.selectionMode == "single":
            current = self.listView.currentIndex().row()
            return self.dictList[int(current)]
        else:
            selected = []
            for item in self.listView.selectedIndexes():
                selected.append(self.dictList[item.row()])
            return selected

    def setupUi(self, Dialog_selectfile, windowTitle, selectionMode):
        self.title = windowTitle  #ADDIN
        self.selectionMode = selectionMode  #ADDIN

        Dialog_selectfile.setObjectName(_fromUtf8("Dialog_selectfile"))
        Dialog_selectfile.resize(400, 433)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog_selectfile)
        self.buttonBox.setGeometry(QtCore.QRect(190, 390, 191, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.listView = QtWidgets.QListView(Dialog_selectfile)
        self.listView.setGeometry(QtCore.QRect(10, 10, 371, 361))
        self.listView.setObjectName(_fromUtf8("listView"))

        self.model = list_model(self.dictList)
        self.listView.setModel(self.model)
        if self.selectionMode == "single":
            self.listView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        else:
            self.listView.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        #self.retranslateUi(Dialog_selectfile)

        self.listView.doubleClicked.connect(Dialog_selectfile.accept)
        self.buttonBox.accepted.connect(Dialog_selectfile.accept) #changed
        self.buttonBox.rejected.connect(Dialog_selectfile.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog_selectfile)
        
"""
    def retranslateUi(self, Dialog_selectfile):
        Dialog_selectfile.setWindowTitle(QtWidgets.QApplication.translate("Dialog_selectfile", self.title, None, QtWidgets.QApplication.UnicodeUTF8))
"""

class list_model(QtCore.QAbstractListModel):
    def __init__(self, dictList, parent=None):
        super(list_model, self).__init__(parent)
        self.list = dictList

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.list)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:  # show just the name
            rowitem = self.list[index.row()]
            return QtCore.QVariant(rowitem['name'])
        elif role == QtCore.Qt.UserRole:  # return the whole python object
            rowitem = self.list[index.row()]
            return rowitem
        return QtCore.QVariant()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_selectfile = QtWidgets.QDialog()
    ui = Ui_Dialog_selectfile('')
    ui.setupUi(Dialog_selectfile, "title", "single")
    Dialog_selectfile.show()
    sys.exit(app.exec_())
