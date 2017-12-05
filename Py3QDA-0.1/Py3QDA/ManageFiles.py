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
from Memo import Ui_Dialog_memo
from ConfirmDelete import Ui_Dialog_confirmDelete
import datetime
#from HTMLToText import html_to_text
import os

#for file extraction
from docx import opendocx, getdocumenttext
import zipfile
import xml.etree.ElementTree
try:
    import pyPdf # use this module only if it is installed
except:
    pass
#ENDADDIN

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class Ui_Dialog_manageFiles(object):
    """    View, import, export, rename and delete text files.    """

    sourcetext = []
    settings = None
    textDialog = None
    MEMO_COLUMN = 1
    DATE_COLUMN = 2
    NAME_COLUMN = 0
    ID_COLUMN = 3
    headerLabels = ["Name","Memo","Date","Id"]
    log = ""

    def __init__(self, settings):
        if settings is not None:
            self.log = ""
            self.sourcetext = []
            self.settings = settings
            cur = self.settings['conn'].cursor()
            cur.execute("select name, id, file, memo, owner, date, dateM, status from source order by name")
            result = cur.fetchall()
            for row in result:
                self.sourcetext.append({'name':row[0], 'id':row[1], 'file':row[2], 'memo':row[3], 'owner':row[4], 'date':row[5], 'dateM':row[6], 'status':row[7]})

    def cellSelected(self):
        """ When the table widget memo cell is selected display the memo.
        Update memo text, or delete memo by clearing text.
        If a new memo also show in table widget by displaying YES in the memo column"""

        x = self.tableWidget_files.currentRow()
        y = self.tableWidget_files.currentColumn()

        if y == self.MEMO_COLUMN:
            Dialog_memo = QtWidgets.QDialog()
            ui = Ui_Dialog_memo(self.sourcetext[x]['memo'])
            ui.setupUi(Dialog_memo, "File memo " + self.sourcetext[x]['name'])
            Dialog_memo.exec_()
            memo = ui.getMemo()
            if memo == "":
                self.tableWidget_files.setItem(x, self.MEMO_COLUMN, QtWidgets.QTableWidgetItem())
            else:
                self.tableWidget_files.setItem(x, self.MEMO_COLUMN, QtWidgets.QTableWidgetItem("Yes"))

            # update sourcetext list and database
            #self.sourcetext[x]['memo'] = memo.encode('raw_unicode_escape')
            self.sourcetext[x]['memo'] = memo
            cur = self.settings['conn'].cursor()
            cur.execute("update source set memo=? where id=?", (self.sourcetext[x]['memo'], self.sourcetext[x]['id']))
            self.settings['conn'].commit()

    def cellModified(self):
        """ If the filename has been changed in the table widget update the database """

        x = self.tableWidget_files.currentRow()
        y = self.tableWidget_files.currentColumn()
        if y == self.NAME_COLUMN:
            newText = str(self.tableWidget_files.item(x, y).text()).strip()

            # check that no other source file has this text and this is is not empty
            update = True
            if newText == "":
                update = False
            for c in self.sourcetext:
                if c['name'] == newText:
                    update = False
            if update:
                #update source list and database
                self.sourcetext[x]['name'] = newText
                cur = self.settings['conn'].cursor()
                cur.execute("update source set name=? where id=?", (newText, self.sourcetext[x]['id']))
                self.settings['conn'].commit()
            else:  #put the original text in the cell
                self.tableWidget_files.item(x, y).setText(self.sourcetext[x]['name'])

    def viewFile(self):
        """ View and edit the file contents """

        x = self.tableWidget_files.currentRow()
        Dialog_memo = QtWidgets.QDialog()
        text = self.sourcetext[x]['file']
        ui = Ui_Dialog_memo(text)
        ui.setupUi(Dialog_memo, "View file: " + self.sourcetext[x]['name'] +" (ID:"+ str(self.sourcetext[x]['id'])+") "
                   +self.sourcetext[x]['owner'] + ", " + self.sourcetext[x]['date'])
        Dialog_memo.exec_()
        # update model and database
        fileText = ui.getMemo() ## unicode
        if fileText != self.sourcetext[x]['file']:
            # NEED TO CHECK THAT THERE ARE NO CODES OR ANNOATIONS OR CASES LINKED TO THIS FILE BEFORE COMMITING CHANGE
            # CHECK NOT YET IMPLEMENTED
            self.sourcetext[x]['file'] = fileText
            cur = self.settings['conn'].cursor()
            cur.execute("update source set file=? where id=?", (self.sourcetext[x]['file'], self.sourcetext[x]['id']))
            self.settings['conn'].commit()
        else:
            pass

    def createFile(self):
        """ Create a new text file by entering text into the dialog """

        Dialog_text = QtWidgets.QDialog()
        ui = Ui_Dialog_memo("")
        ui.setupUi(Dialog_text, "New file")
        Dialog_text.exec_()
        fileText = ui.getMemo()
        fileName = ui.getFilename()
        if fileName == None or fileName == "":
            QtWidgets.QMessageBox.warning(None, 'Warning',"No filename was selected", QtWidgets.QMessageBox.Ok)
            return
        #check for non-unique filename
        if any(d['name'] == fileName for d in self.sourcetext):
            QtWidgets.QMessageBox.warning(None, 'Warning',"Filename in use", QtWidgets.QMessageBox.Ok)
            return

        # increment fileId until a spare id is available
        fileId = 1
        while any(d['id'] == fileId for d in self.sourcetext):
            fileId = fileId + 1

        # update database
        newFile = {'name':fileName, 'id':fileId, 'file': fileText, 'memo':"", 'owner':self.settings['codername'], 'date':datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), 'dateM':"", 'status':1}
        cur = self.settings['conn'].cursor()
        cur.execute("insert into source(name,id,file,memo,owner,date,dateM,status) values(?,?,?,?,?,?,?,?)",
                    (newFile['name'],newFile['id'],newFile['file'],newFile['memo'],newFile['owner'],newFile['date'],newFile['dateM'],newFile['status']))
        self.settings['conn'].commit()
        self.log +=newFile['name'] + " added.\n"

        # clear and refill table widget
        for r in self.sourcetext:
            self.tableWidget_files.removeRow(0)

        self.sourcetext.append(newFile)
        for row, itm in enumerate(self.sourcetext):
            self.tableWidget_files.insertRow(row)
            item = QtWidgets.QTableWidgetItem(itm['name'])
            self.tableWidget_files.setItem(row,self.NAME_COLUMN, item)
            item = QtWidgets.QTableWidgetItem(itm['date'])
            self.tableWidget_files.setItem(row,self.DATE_COLUMN, item)
            if itm['memo'] != None and itm['memo'] != "":
                self.tableWidget_files.setItem(row, self.MEMO_COLUMN, QtWidgets.QTableWidgetItem("Yes"))
            item = QtWidgets.QTableWidgetItem(str(itm['id']))
            self.tableWidget_files.setItem(row, self.ID_COLUMN, item)
        self.tableWidget_files.resizeColumnsToContents()
        self.tableWidget_files.resizeRowsToContents()

    def importFile(self):
        """ Import files and store as plain text.
        Can import from plain text files, also import from html, odt and docx
        Note importing from html, odt and docx all formatting is lost """

        importFile = QtWidgets.QFileDialog.getOpenFileName(None, 'Open file', "")[0]

        nameSplit = importFile.split("/")
        fileName = nameSplit[-1]
        plainText = ""

        # Import from odt
        if importFile[-4:].lower() == ".odt":
            odtFile = zipfile.ZipFile(importFile)
            share = xml.etree.ElementTree.fromstring(odtFile.read('content.xml'))
            document = ""
            for elmt in share.iter():
                if elmt.tag[-1] == "p" or elmt.tag[-1] == "h":
                    document += "\n"
                if elmt.text is not None:
                    document += elmt.text
            plainText = document.encode("utf-8")
            plainText = plainText.decode('utf-8', 'replace')

        # import PDF
        if importFile[-4:].lower() == ".pdf":
            try:
                content = ""
                # Load PDF into pyPDF
                pdf = pyPdf.PdfFileReader(file(importFile, "rb"))
                # Iterate pages
                for i in range(0, pdf.getNumPages()):
                    # Extract text from page and add to content
                    content += pdf.getPage(i).extractText() + "\n"
                content = " ".join(content.replace(u"\xa0", " ").strip().split())
                plainText = content.encode("ascii", "ignore")
            except Exception as e:
                QtWidgets.QMessageBox.warning(None, "Problem importing PDF",str(e)+"\nThe pyPdf module may not be installed.")
                return

        # Import from docx
        if importFile[-5:].lower() == ".docx":
            document = opendocx(importFile)
            paratextlist = getdocumenttext(document)  # Fetch all the text from the document
            # Make unicode version
            newparatextlist = []
            for paratext in paratextlist:
                #newparatextlist.append(paratext.encode("utf-8"))
                newparatextlist.append(paratext)
            plainText = '\n\n'.join(newparatextlist)  # Add two newlines under each paragraph
            #plainText = plainText.decode('utf-8', 'replace')

        # import from html
        if importFile[-5:].lower() == ".html" or importFile[-4:].lower() == ".htm":
            importErrors = 0
            with open(importFile, "r") as sourcefile:
                fileText = ""
                while 1:
                    line = sourcefile.readline()
                    if not line:
                        break
                    try:
                        fileText += line.decode('utf-8','replace')
                    except:
                        #print("html decode error, ignore this line")
                        importErrors += 1
                #plainText = html_to_text(fileText)
                QtWidgets.QMessageBox.warning(None, 'Warning', str(importErrors) + " lines not imported", QtWidgets.QMessageBox.Ok)

        # import plain text file (or anything else that was not in above filetypes)
        if plainText == "":
            importErrors = 0
            try:
                with open(importFile, "r", errors="replace") as sourcefile:
                    lines = sourcefile.readlines()
                    plainText = "".join(lines)
                    """
                    while 1:
                        line = sourcefile.readline()
                        if not line:
                            break
                        try:
                            plainText += str(line).decode('utf-8', 'replace')
                        except:
                            #print("Unicode Decode Error line ignored")
                            importErrors += 1
                    if plainText[0:6] == "\ufeff":  # associated with notepad files
                        plainText = plainText[6:]
                    """
            except:
                QtWidgets.QMessageBox.warning(None, 'Warning', "Cannot import " + str(importFile), QtWidgets.QMessageBox.Ok)
                return
            if importErrors > 0:
                QtWidgets.QMessageBox.warning(None, 'Warning', str(importErrors) + " lines not imported", QtWidgets.QMessageBox.Ok)

        # Final checks: check for duplicated filename and update model, widget and database
        if any(d['name'] == fileName for d in self.sourcetext):
            QtWidgets.QMessageBox.warning(None, 'Duplicate file', "Duplicate filename.\nFile not imported", QtWidgets.QMessageBox.Ok)
            return
        # increment fileId until a spare id is available
        fileId = 1
        while any(d['id'] == fileId for d in self.sourcetext):
            fileId += 1

        newFile = {'name':fileName, 'id':fileId, 'file': plainText, 'memo':"",
        'owner':self.settings['codername'], 'date':datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
         'dateM':"", 'status':1}

        # check the stored file for unicode problems and fix them if possible
        # usually problems with odt and docx files - apostrophes etc
        # still does not fix u2029 errors, added a bit below - might help
        newText = ""
        for c in plainText:
            try:
                if ord(c) == 8233: #hex:2029
                    c == "\n"
                newText += str(c)
            except UnicodeEncodeError as e:
                # e is: 'ascii' codec can't encode character u'\u20ac' in position 0: ordinal not in range(128)
                err = str(e)
                #err = err.split("\u")
                err = err[1].split("\' in")
                err = err[0].upper()
                if err in self.WINDOWS_1252_GREMLINS:
                    newText += self.WINDOWS_1252_GREMLINS[err]
                else:
                    newText += "?"

        #plainText = unicode(newText)
        plainText = newText
        newFile['file'] = plainText
        cur = self.settings['conn'].cursor()
        cur.execute("insert into source(name,id,file,memo,owner,date,dateM,status) values(?,?,?,?,?,?,?,?)",
                    (newFile['name'], newFile['id'], newFile['file'], newFile['memo'],newFile['owner'], newFile['date'], newFile['dateM'], newFile['status']))
        self.settings['conn'].commit()
        self.log +=newFile['name'] + " imported.\n"

        # clear and refill table widget
        for r in self.sourcetext:
            self.tableWidget_files.removeRow(0)
        self.sourcetext.append(newFile)
        self.fillTableWidget_files()

    def exportFile(self):
        """ Export file to a plain text file, filename will have .txt ending """

        x = self.tableWidget_files.currentRow()
        fileName = self.sourcetext[x]['name']
        if len(fileName) > 5 and (fileName[-5:] == ".html" or fileName[-5:] == ".docx"):
            fileName = fileName[0:len(fileName) - 5]
        if len(fileName) > 4 and (fileName[-4:] == ".htm" or fileName[-4:] == ".odt" or fileName[-4] == ".txt"):
            fileName = fileName[0:len(fileName) - 4]
        fileName += ".txt"
        options = QtWidgets.QFileDialog.DontResolveSymlinks | QtWidgets.QFileDialog.ShowDirsOnly
        directory = QtWidgets.QFileDialog.getExistingDirectory(None, "Select directory to save file", os.getenv('HOME'), options)
        if directory:
            fileName = directory + "/" + fileName
            print (("Exporting:  to " + fileName))
            filedata = self.sourcetext[x]['file']
            #filedata = filedata.encode('utf-8')
            f = open(fileName, 'w', encoding='utf8')
            f.write(filedata)
            f.close()

        QtWidgets.QMessageBox.information(None, "File Export", str(fileName) + " exported")
        self.log += fileName + " exported.\n"

    def deleteFile(self):
        """ Delete file from database and update model and widget """

        x = self.tableWidget_files.currentRow()
        fileId = self.sourcetext[x]['id']
        #print("Delete row: " + str(x))
        Dialog_confirmDelete = QtWidgets.QDialog()
        ui = Ui_Dialog_confirmDelete(self.sourcetext[x]['name'])
        ui.setupUi(Dialog_confirmDelete)
        ok = Dialog_confirmDelete.exec_()

        if ok:
            cur = self.settings['conn'].cursor()
            cur.execute("delete from source where id = ?", [fileId])
            cur.execute("delete from coding where fid = ?", [fileId])
            cur.execute("delete from coding2 where fid = ?", [fileId])
            cur.execute("delete from annotation where fid = ?", [fileId])
            cur.execute("delete from caselinkage where fid = ?", [fileId])
            cur.execute("delete from fileAttr where fileID = ?", [fileId])
            self.settings['conn'].commit()

            for item in self.sourcetext:
                if item['id'] == fileId:
                    self.log += item['name'] + " deleted.\n"
                    self.sourcetext.remove(item)
            self.tableWidget_files.removeRow(x)


    def fillTableWidget_files(self):
        """ Fill the table widget with file details """

        self.tableWidget_files.setColumnCount(len(self.headerLabels))
        self.tableWidget_files.setHorizontalHeaderLabels(self.headerLabels)
        self.tableWidget_files.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        for row, details in enumerate(self.sourcetext):
            self.tableWidget_files.insertRow(row)
            self.tableWidget_files.setItem(row, self.NAME_COLUMN, QtWidgets.QTableWidgetItem(details['name']))
            item = QtWidgets.QTableWidgetItem(details['date'])
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidget_files.setItem(row, self.DATE_COLUMN, item)
            memoitem = details['memo']
            if memoitem != None and memoitem != "":
                self.tableWidget_files.setItem(row, self.MEMO_COLUMN, QtWidgets.QTableWidgetItem("Yes"))
            self.tableWidget_files.setItem(row, self.ID_COLUMN, QtWidgets.QTableWidgetItem(details['id']))
        self.tableWidget_files.resizeColumnsToContents()
        self.tableWidget_files.resizeRowsToContents()
        self.tableWidget_files.hideColumn(self.ID_COLUMN)
        self.tableWidget_files.verticalHeader().setVisible(False)

    def getLog(self):
        """ Get details of file movments """

        return self.log

    #ENDADDIN

    def setupUi(self, Dialog_manageFile):
        Dialog_manageFile.setObjectName(_fromUtf8("Dialog_manageFile"))
        Dialog_manageFile.resize(519, 410)
        Dialog_manageFile.move(20, 20)
        self.tableWidget_files = QtWidgets.QTableWidget(Dialog_manageFile)
        self.tableWidget_files.setGeometry(QtCore.QRect(10, 50, 491, 341))
        self.tableWidget_files.setObjectName(_fromUtf8("tableWidget_files"))
        self.tableWidget_files.setColumnCount(0)
        self.tableWidget_files.setRowCount(0)
        self.pushButton_view = QtWidgets.QPushButton(Dialog_manageFile)
        self.pushButton_view.setGeometry(QtCore.QRect(10, 10, 81, 27))
        self.pushButton_view.setObjectName(_fromUtf8("pushButton_view"))
        self.pushButton_create = QtWidgets.QPushButton(Dialog_manageFile)
        self.pushButton_create.setGeometry(QtCore.QRect(100, 10, 81, 27))
        self.pushButton_create.setObjectName(_fromUtf8("pushButton_create"))
        self.pushButton_export = QtWidgets.QPushButton(Dialog_manageFile)
        self.pushButton_export.setGeometry(QtCore.QRect(280, 10, 81, 27))
        self.pushButton_export.setObjectName(_fromUtf8("pushButton_export"))
        self.pushButton_export.setToolTip("Export to a text file")
        self.pushButton_delete = QtWidgets.QPushButton(Dialog_manageFile)
        self.pushButton_delete.setGeometry(QtCore.QRect(417, 10, 81, 27))
        self.pushButton_delete.setObjectName(_fromUtf8("pushButton_delete"))
        self.pushButton_import = QtWidgets.QPushButton(Dialog_manageFile)
        self.pushButton_import.setGeometry(QtCore.QRect(190, 10, 81, 27))
        self.pushButton_import.setObjectName(_fromUtf8("pushButton_import"))

        self.retranslateUi(Dialog_manageFile)
        QtCore.QMetaObject.connectSlotsByName(Dialog_manageFile)

        #ADDIN
        self.fillTableWidget_files()

        self.tableWidget_files.itemChanged.connect(self.cellModified)
        self.pushButton_create.clicked.connect(self.createFile)
        self.pushButton_view.clicked.connect(self.viewFile)
        self.pushButton_delete.clicked.connect(self.deleteFile)
        self.pushButton_import.clicked.connect(self.importFile)
        self.pushButton_export.clicked.connect(self.exportFile)
        self.tableWidget_files.cellClicked.connect(self.cellSelected)

        #ENDADDIN

    def retranslateUi(self, Dialog_manageFile):
        Dialog_manageFile.setWindowTitle(QtWidgets.QApplication.translate("Dialog_manageFile", "Files", None, 1))
        self.pushButton_view.setText(QtWidgets.QApplication.translate("Dialog_manageFile", "View", None, 1))
        self.pushButton_export.setText(QtWidgets.QApplication.translate("Dialog_manageFile", "Export", None, 1))
        self.pushButton_delete.setText(QtWidgets.QApplication.translate("Dialog_manageFile", "Delete", None, 1))
        self.pushButton_create.setText(QtWidgets.QApplication.translate("Dialog_manageFile", "Create", None, 1))
        self.pushButton_import.setText(QtWidgets.QApplication.translate("Dialog_manageFile", "Import", None, 1))

    WINDOWS_1252_GREMLINS = {
        # adapted from http://effbot.org/zone/unicode-gremlins.htm
        '0152':u'Œ',  # LATIN CAPITAL LIGATURE OE
        '0153':u'œ',  # LATIN SMALL LIGATURE OE
        '0160':u'Š',  # LATIN CAPITAL LETTER S WITH CARON
        '0161':u'š',  # LATIN SMALL LETTER S WITH CARON
        '0178':u'Ÿ',  # LATIN CAPITAL LETTER Y WITH DIAERESIS
        '017E':u'ž',  # LATIN SMALL LETTER Z WITH CARON
        '017D':u'Ž',  # LATIN CAPITAL LETTER Z WITH CARON
        '0192':u'ƒ',  # LATIN SMALL LETTER F WITH HOOK
        '02C6':u'ˆ',  # MODIFIER LETTER CIRCUMFLEX ACCENT
        '02DC':u'~',  # SMALL TILDE
        '2013':u'-',  # EN DASH
        '2014':u'-',  # EM DASH
        '201A':u"'",  # SINGLE LOW-9 QUOTATION MARK
        '201C':u'"',  # LEFT DOUBLE QUOTATION MARK
        '201D':u'"',  # RIGHT DOUBLE QUOTATION MARK
        '201E':u"'",  # DOUBLE LOW-9 QUOTATION MARK
        '2018':u"'",  # LEFT SINGLE QUOTATION MARK
        '2019':u"'",  # RIGHT SINGLE QUOTATION MARK
        '2020':u'†',  # DAGGER
        '2021':u'‡',  # DOUBLE DAGGER
        '2022':u'•',  # BULLET
        '2026':u'…',  # HORIZONTAL ELLIPSIS
        '2030':u'‰',  # PER MILLE SIGN
        '2039':u"'",  # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
        '203A':u"'",  # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
        '20AC':u'€',  # EURO SIGN
        '2122':u'™'  # TRADE MARK SIGN
    }

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_manageFile = QtWidgets.QDialog()
    ui = Ui_Dialog_manageFiles(None)
    ui.setupUi(Dialog_manageFile)
    Dialog_manageFile.show()
    sys.exit(app.exec_())
