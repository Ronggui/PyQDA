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

#ADDIN
#import sqlite3
import datetime
#from operator import itemgetter
from Memo import Ui_Dialog_memo
from AddItem import Ui_Dialog_addItem
from ConfirmDelete import Ui_Dialog_confirmDelete
from SelectFile import Ui_Dialog_selectfile
#END

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog_fcats(object):
    """
    File Category management.
    Shows a list of file categories which can be added to or deleted from.
    Show a list of files which can be dragged into file categories
    """

    #ADDIN
    FILE_NAME_COLUMN = 0
    FILE_MEMO_COLUMN = 1
    FILE_ID_COLUMN = 2
    CAT_NAME_COLUMN = 0
    CAT_MEMO_COLUMN = 1
    CAT_VIEW_COLUMN = 2
    CAT_ID_COLUMN = 3

    settings = None
    source = []  # the files
    cats = []  # file categories
    treeFile = []  # links files to categories
    selectedCategoryId = -1  # if -1 all categories and files are shown, if a category id then only that category and its files are shown

    def __init__(self, settings):
        self.source = []
        self.cats = []
        self.treeFile = []
        self.settings = settings

        cur = self.settings['conn'].cursor()
        cur.execute("select name, id, file, memo, owner, date, dateM, status from source")
        result = cur.fetchall()
        for row in result:
            self.source.append({'name':row[0], 'id':row[1], 'file':row[2], 'memo':row[3], 'owner':row[4], 'date':row[5], 'dateM':row[6], 'status':row[7]})

        # note fid is not used in filecat
        cur.execute("select name, fid, catid, owner, date, dateM, memo, status from filecat")
        result = cur.fetchall()
        for row in result:
            self.cats.append({'name':row[0],'fid':row[1], 'catid':row[2], 'owner':row[3], 'date':row[4], 'dateM':row[5], 'memo':row[6], 'status':row[7]})

        cur.execute("select fid, catid, date, dateM, memo, status, owner from treeFile")
        result = cur.fetchall()
        for row in result:
            self.treeFile.append({'fid':row[0], 'catid':row[1], 'date':row[2], 'dateM':row[3], 'memo':row[4], 'status':row[5], 'owner':row[6]})

    def fileCellSelected(self):
        """ When memo cells are selected in the table widget, open a memo dialog """
        x = self.tableWidget_files.currentRow()
        y = self.tableWidget_files.currentColumn()

        if y == self.FILE_MEMO_COLUMN:
            Dialog_memo = QtWidgets.QDialog()
            ui = Ui_Dialog_memo(self.source[x]['memo'])
            ui.setupUi(Dialog_memo, "File memo "+ self.source[x]['name'])
            Dialog_memo.exec_()
            memo = ui.getMemo()

            if memo == "":
                self.tableWidget_files.setItem(x, 1, QtWidgets.QTableWidgetItem())
            else:
                self.tableWidget_files.setItem(x, 1, QtWidgets.QTableWidgetItem("Yes"))

            #update source list and database
            self.source[x]['memo'] = str(memo)
            cur = self.settings['conn'].cursor()
            cur.execute("update source set memo=? where id=?", (self.source[x]['memo'], self.source[x]['id']))
            self.settings['conn'].commit()

    def fileCellModified(self):
        """ When a file name is changed in the table widget update the
        details in model and database """

        x = self.tableWidget_files.currentRow()
        y = self.tableWidget_files.currentColumn()
        if y == self.FILE_NAME_COLUMN:
            newFileText = str(self.tableWidget_files.item(x, y).text())
            # check that no other file has this text and this is is not empty
            update = True
            if newFileText == "":
                update = False
            for c in self.source:
                if c['name'] == newFileText:
                    update = False
            if update:
                # update source list and database
                cur = self.settings['conn'].cursor()
                cur.execute("update source set name=? where id=?", (newFileText, self.source[x]['id']))
                self.settings['conn'].commit()
                self.source[x]['name'] = newFileText
            else:  # put the original text back in the cell
                self.tableWidget_files.item(x, y).setText(self.source[x]['name'])

    def catsCellSelected(self):
        """ Open a memo dialog if a category memo cell is selected """

        x = self.tableWidget_cats.currentRow()
        y = self.tableWidget_cats.currentColumn()

        # category memo column
        if y == self.CAT_MEMO_COLUMN:
            Dialog_memo = QtWidgets.QDialog()
            ui = Ui_Dialog_memo(self.cats[x]['memo'])
            ui.setupUi(Dialog_memo, "Category memo " + self.cats[x]['name'])
            Dialog_memo.exec_()
            memo = ui.getMemo()

            if memo == "":
                self.tableWidget_cats.setItem(x,self.CAT_MEMO_COLUMN,QtWidgets.QTableWidgetItem())
            else:
                self.tableWidget_cats.setItem(x,self.CAT_MEMO_COLUMN,QtWidgets.QTableWidgetItem("Yes"))

            #update cats list and database
            self.cats[x]['memo'] = str(memo)
            cur = self.settings['conn'].cursor()
            cur.execute("update filecat set memo=? where catid=?", (self.cats[x]['memo'], self.cats[x]['catid']))
            self.settings['conn'].commit()

        # view files for this category
        if y == self.CAT_VIEW_COLUMN:
            #important need to unselect all files in tableWidget
            if self.selectedCategoryId == -1:  # all categories currently displayed, so change this to selected category
                self.pushButton_link.setEnabled(False)
                self.pushButton_unlink.setEnabled(True)
                self.selectedCategoryId = int(self.tableWidget_cats.item(x, self.CAT_ID_COLUMN).text())
                for (row, item) in enumerate(self.cats):
                    if self.selectedCategoryId != int(self.tableWidget_cats.item(row, self.CAT_ID_COLUMN).text()):
                        self.tableWidget_cats.hideRow(row)  # hide other categories

                # now show files associated with this category
                for(row, item) in enumerate(self.source):
                    hide = True
                    for treeFileItem in self.treeFile:
                        #print str(treeFileItem['catid'])+" "+str(self.selectedCategoryId)+" co:"+str(treeFileItem['fid'])+" "+str(item['id'])
                        if int(treeFileItem['catid']) == self.selectedCategoryId and treeFileItem['fid'] == item['id']:
                            hide = False
                    if hide:
                        self.tableWidget_files.hideRow(row)

            else:
                self.selectedCategoryId = -1
                self.pushButton_link.setEnabled(True)
                self.pushButton_unlink.setEnabled(False)
                for (row, item) in enumerate(self.cats):
                    self.tableWidget_cats.showRow(row)
                for(row, item) in enumerate(self.source):
                    self.tableWidget_files.showRow(row)

                # need to clear selection in category table when showing all rows
                # as there are no selected items but the previous view cell appears selected
                self.tableWidget_cats.clearSelection()

    def catsCellModified(self):
        """ When a category name is modified, update the model and database """

        x = self.tableWidget_cats.currentRow()
        y = self.tableWidget_cats.currentColumn()
        if y == self.CAT_NAME_COLUMN:
            newCatText = str(self.tableWidget_cats.item(x, y).text())
            # check that no other category has this text and this is is not empty
            update = True
            if newCatText == "":
                update = False
            for c in self.cats:
                if c['name'] == newCatText:
                    update = False
            if update:
                # update category list and database
                cur = self.settings['conn'].cursor()
                cur.execute("update filecat set name=? where catid=?", (newCatText, self.cats[x]['catid']))
                self.settings['conn'].commit()
                self.cats[x]['name'] = newCatText
            else:  # put the original text in the cell
                self.tableWidget_cats.item(x, y).setText(self.cats[x]['name'])

    def addCat(self):
        """ When button pressed, add a new category.
        Note: the addItem dialog does the checking for duplicate category names """

        Dialog_addCat = QtWidgets.QDialog()
        ui = Ui_Dialog_addItem(self.cats)
        ui.setupUi(Dialog_addCat, "Category")
        Dialog_addCat.exec_()
        newCatText = ui.getNewItem()
        if newCatText is not None:
            #add to database
            # need to generate a new id as the RQDA database does not have an autoincrement id field
            newid = 1
            for cat in self.cats:
                if cat['catid'] >= newid: newid = cat['catid']+1
            item = {'name':newCatText,'fid':None, 'catid':newid, 'memo':"", 'owner':self.settings['codername'], 'date':datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), 'dateM':"", 'status':1}
            self.cats.append(item)
            cur = self.settings['conn'].cursor()
            cur.execute("insert into filecat (name, fid, catid, memo, owner, date, dateM, status) values(?,?,?,?,?,?,?,?)"
                        ,(item['name'], item['fid'], item['catid'], item['memo'], item['owner'],
                        item['date'], item['dateM'], item['status']))
            self.settings['conn'].commit()

            #update widget
            self.tableWidget_cats.insertRow(0)
            newItem = QtWidgets.QTableWidgetItem(item['name'])
            self.tableWidget_cats.setItem(0, self.CAT_NAME_COLUMN, newItem)
            newItem = QtWidgets.QTableWidgetItem(item['memo'])
            self.tableWidget_cats.setItem(0, self.CAT_MEMO_COLUMN, newItem)
            newItem = QtWidgets.QTableWidgetItem(str(item['catid']))
            self.tableWidget_cats.setItem(0, self.CAT_ID_COLUMN, newItem)
            self.tableWidget_cats.resizeColumnsToContents()
            self.tableWidget_cats.resizeRowsToContents()

    def deleteCat(self):
        """ When category highlighted and Delete button pressed. Delete category from model and database """

        tableRowsToDelete = [] # for table widget ids
        idsToDelete = [] # for ids for cats and db
        catNamesToDelete = "" # for confirmDelete Dialog

        for itemWidget in self.tableWidget_cats.selectedItems():
            tableRowsToDelete.append(int(itemWidget.row()))
            idsToDelete.append(int(self.tableWidget_cats.item(itemWidget.row(), self.CAT_ID_COLUMN).text()))
            catNamesToDelete = catNamesToDelete+"\n" + str(self.tableWidget_cats.item(itemWidget.row(), self.CAT_NAME_COLUMN).text())
            #print "X:"+ str(itemWidget.row()) + "  y:"+str(itemWidget.column()) +"  "+itemWidget.text() +"  id:"+str(self.tableWidget_files.item(itemWidget.row(),3).text())
        if catNamesToDelete == "":
            return
        tableRowsToDelete.sort(reverse=True)

        Dialog_confirmDelete = QtWidgets.QDialog()
        ui = Ui_Dialog_confirmDelete(catNamesToDelete)
        ui.setupUi(Dialog_confirmDelete)
        ok = Dialog_confirmDelete.exec_()
        if ok:
            for r in tableRowsToDelete:
                self.tableWidget_cats.removeRow(r)

            if self.selectedCategoryId != -1:  # show all other categories and files again
                self.selectedCategoryId = -1
                for (row, item) in enumerate(self.cats):
                    self.tableWidget_cats.showRow(row)
                for(row, item) in enumerate(self.source):
                    self.tableWidget_files.showRow(row)

            for catid in idsToDelete:
                for item in self.cats:
                    if item['catid'] == catid:
                        self.cats.remove(item)
                        cur = self.settings['conn'].cursor()
                        #print(str(id) + "  "+ str(type(id)))
                        cur.execute("delete from treeFile where catid = ?", [catid])
                        cur.execute("delete from filecat where catid = ?", [catid])
                        self.settings['conn'].commit()

    def link(self):
        """ Link one or more selected files to one selected category when link button pressed"""

        if self.selectedCategoryId != -1:  # do not link if one category is already selected
            return
        catId = None
        fileIds = []

        # get the last (only) selected cat item
        for itemWidget in self.tableWidget_cats.selectedItems():
            catId = int(self.tableWidget_cats.item(itemWidget.row(), self.CAT_ID_COLUMN).text())
        if catId == None: return

        for itemWidget in self.tableWidget_files.selectedItems():
            fileIds.append(int(self.tableWidget_files.item(itemWidget.row(), self.FILE_ID_COLUMN).text()))
        if len(fileIds) == 0: return

        '''print("Linking Category  id:"+str(catId)+" with Files:"),
        for item in  fileIds:
            print(str(item)+ ", "),
        print'''
         # update Db and treeFile variable
        cur = self.settings['conn'].cursor()
        theDate = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
        for fid in fileIds:
            # check the link is not already in the Db
            cur.execute("select count(*) from treeFile where fid=? and catid=?",(fid, catId))
            result = cur.fetchone()[0]
            self.settings['conn'].commit()
            if result == 0:
                cur.execute("insert into treeFile (fid, catid, date, dateM, memo, status, owner) values(?,?,?,?,?,?,?)",
                        (fid, catId, theDate, theDate, "", 1, self.settings['codername']))
            else:
                return

        #update treeFile file
        self.treeFile = []
        cur.execute("select fid, catid, date, dateM, memo, status, owner from treeFile")
        result = cur.fetchall()
        for row in result:
            self.treeFile.append({'fid': row[0], 'catid': row[1], 'date': row[2], 'dateM': row[3], 'memo': row[4], 'status': row[5], 'owner':row[6]})
        self.settings['conn'].commit()

    def unlink(self):
        """ When button pressed, all selected files are unlinked from the selected category """

        fileIds = []
        if self.selectedCategoryId == -1:
            return
        for itemWidget in self.tableWidget_files.selectedItems():
            fileIds.append(int(self.tableWidget_files.item(itemWidget.row(), self.FILE_ID_COLUMN).text()))
        if len(fileIds) == 0:
            return
        #print("Unlink: selCatView:" + str(self.selectedCategoryId) +"  files:"+ str(fileIds))  #temp
        # update Db and treeFile variable
        cur = self.settings['conn'].cursor()
        for fid in fileIds:
            cur.execute("delete from treeFile where fid=? and catid=?",(fid, self.selectedCategoryId))
        self.treeFile = []
        cur.execute("select fid, catid, date, dateM, memo, status, owner from treeFile")
        result = cur.fetchall()
        for row in result:
            self.treeFile.append({'fid':row[0], 'catid':row[1], 'date':row[2], 'dateM':row[3], 'memo':row[4], 'status':row[5], 'owner':row[6]})
        self.settings['conn'].commit()

    def mergeCats(self):
        """When merge categories button is pressed, merge two or more categories into one category.
        Note: there is no undo for this """

        removeCats = []
        for itemWidget in self.tableWidget_cats.selectedItems():
            removeTemp = {'name':self.tableWidget_cats.item(itemWidget.row(), self.CAT_NAME_COLUMN).text(),'catid':int(self.tableWidget_cats.item(itemWidget.row(), self.CAT_ID_COLUMN).text())}
            # remove duplicate selections, have duplicates because tableWidget_cats is not row selection only
            addCat = True
            for remCat in removeCats:
                if removeTemp == remCat: addCat = False
            if addCat: removeCats.append(removeTemp)
        if len(removeCats) < 2:
            return

        Dialog_selectcat = QtWidgets.QDialog()
        ui = Ui_Dialog_selectfile(removeCats)
        ui.setupUi(Dialog_selectcat, "Merging, Select category to keep", "single")
        ok = Dialog_selectcat.exec_()
        if not(ok):
            return
        keepCat = ui.getSelected()
        #print(("Keeping: " + str(keepCat)))
        for cat in removeCats:
            if cat['catid'] == keepCat['catid']:
                removeCats.remove(cat)  # exclude the kept category from the remove list
        #print("Cats removing: " + str(removeCats))

        cur = self.settings['conn'].cursor()
        for cat in removeCats:
            cur.execute("")
            cur.execute("update treefile set catid=? where catid=?", (keepCat['catid'] ,cat['catid']))
            cur.execute("delete from filecat where catid=?",(cat['catid'],))

        # refresh cats, treefile and self.tableWidget_cats
        for row in self.cats:
            self.tableWidget_cats.removeRow(0)

        self.cats = []
        cur.execute("select name, fid, catid, owner, date, dateM, memo, status from filecat")
        result = cur.fetchall()
        for row in result:
            self.cats.append({'name':row[0],'fid':row[1], 'catid':row[2], 'owner':row[3], 'date':row[4], 'dateM':row[5], 'memo':row[6], 'status':row[7]})
        self.settings['conn'].commit()

        self.treeFile = []
        cur.execute("select fid, catid, date, dateM, memo, status, owner from treeFile")
        result = cur.fetchall()
        for row in result:
            self.treeFile.append({'fid':row[0], 'catid':row[1], 'date':row[2], 'dateM':row[3], 'memo':row[4], 'status':row[5], 'owner':row[6]})
        self.settings['conn'].commit()

        # refill cats table
        for row, cat in enumerate(self.cats):
            self.tableWidget_cats.insertRow(row)
            self.tableWidget_cats.setItem(row, self.CAT_NAME_COLUMN, QtWidgets.QTableWidgetItem(cat['name']))
            mtmp = cat['memo']
            if mtmp != None and mtmp != "":
                self.tableWidget_cats.setItem(row, self.CAT_MEMO_COLUMN, QtWidgets.QTableWidgetItem("Yes"))
            catid = cat['catid']
            if catid == None: catid = ""
            self.tableWidget_cats.setItem(row, self.CAT_ID_COLUMN, QtWidgets.QTableWidgetItem(str(catid)))
    #END ADDIN

    def setupUi(self, Dialog_cats):
        Dialog_cats.setObjectName(_fromUtf8("Dialog_cats"))
        sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        h = sizeObject.height() * 0.8
        w = sizeObject.width() * 0.8
        h = min([h, 1000])
        w = min([w, 2000])
        Dialog_cats.resize(w, h)
        Dialog_cats.move(20, 20)

        self.pushButton_add = QtWidgets.QPushButton(Dialog_cats)
        self.pushButton_add.setGeometry(QtCore.QRect(10, 10, 98, 27))
        self.pushButton_add.setObjectName(_fromUtf8("pushButton_add"))
        self.pushButton_delete = QtWidgets.QPushButton(Dialog_cats)
        self.pushButton_delete.setGeometry(QtCore.QRect(130, 10, 98, 27))
        self.pushButton_delete.setObjectName(_fromUtf8("pushButton_delete"))
        self.pushButton_mergeCats = QtWidgets.QPushButton(Dialog_cats)
        self.pushButton_mergeCats.setGeometry(QtCore.QRect(360, 10, 130, 27))
        self.pushButton_mergeCats.setObjectName(_fromUtf8("pushButton_mergeCats"))
        self.pushButton_link = QtWidgets.QPushButton(Dialog_cats)
        self.pushButton_link.setGeometry(QtCore.QRect(10, 50, 98, 27))
        self.pushButton_link.setObjectName(_fromUtf8("pushButton_link"))
        self.pushButton_unlink = QtWidgets.QPushButton(Dialog_cats)
        self.pushButton_unlink.setGeometry(QtCore.QRect(130, 50, 98, 27))
        self.pushButton_unlink.setObjectName(_fromUtf8("pushButton_unlink"))
        self.pushButton_unlink.setEnabled(False)

        '''self.pushButton_unmark = QtWidgets.QPushButton(Dialog_cats)
        self.pushButton_unmark.setGeometry(QtCore.QRect(250, 50, 98, 27))
        self.pushButton_unmark.setObjectName(_fromUtf8("pushButton_unmark"))
        self.pushButton_mark = QtWidgets.QPushButton(Dialog_cats)
        self.pushButton_mark.setGeometry(QtCore.QRect(370, 50, 98, 27))
        self.pushButton_mark.setObjectName(_fromUtf8("pushButton_mark"))'''

        #ADDIN
        self.splitter = QtWidgets.QSplitter(Dialog_cats)
        self.splitter.setGeometry(QtCore.QRect(10, 90, w - 20, h - 100))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        #END ADDIN

        self.tableWidget_files = QtWidgets.QTableWidget(self.splitter)
        self.tableWidget_files.setGeometry(QtCore.QRect(500, 90, 460, h-200))
        self.tableWidget_files.setObjectName(_fromUtf8("tableWidget_files"))
        self.tableWidget_files.setColumnCount(0)
        self.tableWidget_files.setRowCount(0)
        #self.tableWidget_files.setSelectionMode( QtWidgets.QAbstractItemView.SingleSelection )

        self.tableWidget_cats = QtWidgets.QTableWidget(self.splitter)
        self.tableWidget_cats.setGeometry(QtCore.QRect(10, 90, 460, h-200))
        self.tableWidget_cats.setObjectName(_fromUtf8("tableWidget_cats"))
        self.tableWidget_cats.setColumnCount(0)
        self.tableWidget_cats.setRowCount(0)
        #self.tableWidget_cats.setSelectionMode( QtWidgets.QAbstractItemView.SingleSelection )

        #fill files table
        self.tableWidget_files.setColumnCount(3)
        self.tableWidget_files.setHorizontalHeaderLabels(["File", "Memo", "id"])
        for row, file in enumerate(self.source):
            self.tableWidget_files.insertRow(row)
            self.tableWidget_files.setItem(row, self.FILE_NAME_COLUMN, QtWidgets.QTableWidgetItem(file['name']))
            mtmp = file['memo']
            if mtmp is not None and mtmp != "":
                self.tableWidget_files.setItem(row, self.FILE_MEMO_COLUMN, QtWidgets.QTableWidgetItem("Yes"))
            fid = file['id']
            if fid is None: fid = ""
            self.tableWidget_files.setItem(row, self.FILE_ID_COLUMN, QtWidgets.QTableWidgetItem(str(fid)))

        self.tableWidget_files.verticalHeader().setVisible(False)
        self.tableWidget_files.resizeColumnsToContents()
        self.tableWidget_files.resizeRowsToContents()
        if not self.settings['showIDs']:
            self.tableWidget_files.hideColumn(self.FILE_ID_COLUMN)

        #fill categories table
        self.tableWidget_cats.setColumnCount(4)
        self.tableWidget_cats.setHorizontalHeaderLabels(["Category", "Memo", "View", "catid"])
        for row, filecat in enumerate(self.cats):
            self.tableWidget_cats.insertRow(row)
            self.tableWidget_cats.setItem(row, self.CAT_NAME_COLUMN, QtWidgets.QTableWidgetItem(filecat['name']))
            mtmp = filecat['memo']
            if mtmp is not None and mtmp != "":
                self.tableWidget_cats.setItem(row, self.CAT_MEMO_COLUMN, QtWidgets.QTableWidgetItem("Yes"))
            catid = filecat['catid']
            if catid is None: catid = ""
            self.tableWidget_cats.setItem(row, self.CAT_ID_COLUMN, QtWidgets.QTableWidgetItem(str(catid)))

        self.tableWidget_cats.verticalHeader().setVisible(False)
        self.tableWidget_cats.resizeColumnsToContents()
        self.tableWidget_cats.resizeRowsToContents()
        if not self.settings['showIDs']:
                self.tableWidget_cats.hideColumn(self.CAT_ID_COLUMN)

        self.tableWidget_files.cellClicked.connect(self.fileCellSelected)
        self.tableWidget_cats.cellClicked.connect(self.catsCellSelected)
        self.tableWidget_cats.itemChanged.connect(self.catsCellModified)
        self.tableWidget_files.itemChanged.connect(self.fileCellModified)
        self.pushButton_add.clicked.connect(self.addCat)
        self.pushButton_delete.clicked.connect(self.deleteCat)
        self.pushButton_link.clicked.connect(self.link)
        self.pushButton_unlink.clicked.connect(self.unlink)
        self.pushButton_mergeCats.clicked.connect(self.mergeCats)
        #self.pushButton_memo.clicked.connect(self.codeMemo)
        #self.pushButton_memo.clicked.connect(self.catMemo)

        #END ADDIN

        self.retranslateUi(Dialog_cats)
        QtCore.QMetaObject.connectSlotsByName(Dialog_cats)

    def retranslateUi(self, Dialog_cats):
        Dialog_cats.setWindowTitle(QtWidgets.QApplication.translate("Dialog_cats", "Categories", None, 1))
        self.pushButton_add.setText(QtWidgets.QApplication.translate("Dialog_cats", "Add", None, 1))
        self.pushButton_delete.setText(QtWidgets.QApplication.translate("Dialog_cats", "Delete", None, 1))
        #self.pushButton_mergeCodes.setText(QtWidgets.QApplication.translate("Dialog_cats", "Merge Files", None, 1))
        self.pushButton_mergeCats.setText(QtWidgets.QApplication.translate("Dialog_cats", "Merge Categories", None, 1))
        self.pushButton_link.setText(QtWidgets.QApplication.translate("Dialog_cats", "Link", None, 1))
        self.pushButton_unlink.setText(QtWidgets.QApplication.translate("Dialog_cats", "Unlink", None, 1))
        #self.pushButton_unmark.setText(QtWidgets.QApplication.translate("Dialog_cats", "XUnmark", None, 1))
        #self.pushButton_mark.setText(QtWidgets.QApplication.translate("Dialog_cats", "XMark", None, 1))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_fcats = QtWidgets.QDialog()
    ui = Ui_Dialog_fcats()
    ui.setupUi(Dialog_fcats)
    Dialog_fcats.show()
    sys.exit(app.exec_())
