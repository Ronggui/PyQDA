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
import datetime # ADDIN

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

class Ui_Dialog_assignAttributes(object):
    """ Assign values to attributes for cases and files. Default initialisation uses case attributes. """

    #ADDIN
    NAME_COLUMN = 0
    ID_COLUMN = 1

    settings = None
    attributes = None # list of attribute names 'variables'
    values = None # attribute values
    attrType = None # indicator for Cases or Files
    casesOrFiles = [] # list of case names or file names and ids
    attrLabels = [] # contains tablewidget headings which start with the case or file name and case or file id

    def __init__(self,settings):

        self.settings = settings
        self.attributes = []
        self.attrLabels = []
        self.values = []
        self.attrType = "Cases"
        self.attrLabels = [self.attrType,"id"]

        cur = self.settings['conn'].cursor()
        cur.execute("select name, status, memo, class from attributes")
        result = cur.fetchall()
        for row in result:
            self.attributes.append({'name':row[0], 'status':row[1], 'memo':row[2], 'class':row[3]})
            self.attrLabels.append(row[0])

        cur.execute("select name, id from cases order by name")
        for row in result:
            self.casesOrFiles.append({'name':row[0], 'id':row[1]})
        self.loadValues()

    def loadValues(self):
        """ Load case or file names and ids. Load attribute values for cases or files. """

        attrTable = {}
        if self.attrType == "Cases":
            attrTable['name'] = "caseAttr"
            attrTable['id'] = "caseId"
        else:
            attrTable['name'] = "fileAttr"
            attrTable['id'] = "fileId"

        self.values = []
        cur = self.settings['conn'].cursor()
        cur.execute("select variable, value, " + attrTable['id'] + ", date, dateM, owner, status from " + attrTable['name'])
        result = cur.fetchall()
        for row in result:
            self.values.append({'variable':row[0], 'value':row[1], 'caseOrFileID':row[2], 'date':row[3], 'dateM':row[4], 'owner':row[5], 'status':row[6]})

        self.casesOrFiles = []
        tablename = ""
        if self.attrType == "Cases":
            tablename = "cases"
        else:
            tablename = "source"
        cur.execute("select name, id from " + tablename + " order by name")
        result = cur.fetchall()
        for row in result:
            self.casesOrFiles.append({'name':row[0], 'id':row[1]})

    def selectFiles(self):
        """ if files button selected, change attrType, load file attributes and update table widget """

        if self.attrType == "Files": return
        self.attrType = "Files"
        self.attrLabels[0] = self.attrType

        # empty tablewidget
        for row in self.casesOrFiles:
            self.tableWidget.removeRow(0)
        self.loadValues()
        self.fillTableWidget()

    def selectCases(self):
        """ if cases button selected, change attrType, load case attributes and update table widget """

        if self.attrType=="Cases": return
        self.attrType = "Cases"
        self.attrLabels[0] = self.attrType

        # empty tablewidget and refill
        for row in self.casesOrFiles:
            self.tableWidget.removeRow(0)
        self.loadValues()
        self.fillTableWidget()

    def cellModified(self):
        """ If an attribute value has been changed in the table widget update the values list and database """

        x = self.tableWidget.currentRow()
        y = self.tableWidget.currentColumn()
        if y <= self.ID_COLUMN: return

        newText = str(self.tableWidget.item(x, y).text()).strip().encode('raw_unicode_escape')
        #print(self.casesOrFiles[x]['name'], self.casesOrFiles[x]['id'], self.attributes[y-2]['name'], newText) #temp

        # check that numeric column value is actually numeric
        if self.attributes[y-2]['class'] == "numeric" and newText !="":
            try:
                float(newText)
            except ValueError:
                # replace original text, this was the easy way out
                # empty tablewidget and refill
                for row in self.casesOrFiles:
                    self.tableWidget.removeRow(0)
                self.fillTableWidget()
                return

        attrTable = {}
        if self.attrType == "Cases":
            attrTable['name'] = "caseAttr"
            attrTable['id'] = "caseId"
        else:
            attrTable['name'] = "fileAttr"
            attrTable['id'] = "fileId"

        # delete existing value from database, it may exist it may not
        cur = self.settings['conn'].cursor()
        sql = "delete from " + attrTable['name'] + " where variable=? and " + attrTable['id'] + " = ?"
        #print ("attr:" + self.attributes[y-2]['name'])
        #print ("case:"+self.casesOrFiles[x]['name'])
        cur.execute(sql, (self.attributes[y-2]['name'], self.casesOrFiles[x]['id']))
        self.settings['conn'].commit()
        if newText =="": return

        # add newText value to the database and to the model
        item = {'variable':self.attributes[y-2]['name'], 'value':newText,
             'caseOrFileID':self.casesOrFiles[x]['id'],
             'date':datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
             'dateM':"", 'owner':self.settings['codername'], 'status':1}
        # remove existing value from list, if the value is present
        for v in self.values:
            if v['caseOrFileID'] == item['caseOrFileID'] and v['variable'] == item['variable']:
                self.values.remove(v)

        # now add the item to values and database
        self.values.append(item)
        cur = self.settings['conn'].cursor()
        sql = "insert into " + attrTable['name'] + " (variable, value, " + attrTable['id'] + ", date, dateM, owner, status) values (?,?,?,?,?,?,?)"
        cur.execute(sql, (item['variable'], item['value'], item['caseOrFileID'], item['date'], item['dateM'], item['owner'], item['status']))
        self.settings['conn'].commit()

    def fillTableWidget(self):
        """ Fill the table widget with attribute details for each case or file. """

        self.tableWidget.setColumnCount(len(self.attrLabels))
        self.tableWidget.setHorizontalHeaderLabels(self.attrLabels)

        for row, cf in enumerate(self.casesOrFiles):
            self.tableWidget.insertRow(row)
            item = QtWidgets.QTableWidgetItem(cf['name'])
            item.setFlags(QtCore.Qt.ItemIsEnabled) # cannot be edited
            self.tableWidget.setItem(row, self.NAME_COLUMN, item)
            self.tableWidget.setItem(row, self.ID_COLUMN, QtWidgets.QTableWidgetItem(str(cf['id'])))

            for value in self.values:
                if cf['id'] == value['caseOrFileID']:
                    columnNum = 2
                    for colnum, collabel in enumerate(self.attrLabels):
                        if collabel == value['variable']:
                            columnNum = colnum
                    self.tableWidget.setItem(row,columnNum, QtWidgets.QTableWidgetItem(str(value['value'])))

        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.hideColumn(1)

    #END ADDIN

    def setupUi(self, Dialog_assignAttributes):
        Dialog_assignAttributes.setObjectName(_fromUtf8("Dialog_assignAttributes"))
        Dialog_assignAttributes.resize(854, 485)
        self.radioButton = QtWidgets.QRadioButton(Dialog_assignAttributes)
        self.radioButton.setGeometry(QtCore.QRect(180, 19, 81, 20))
        self.radioButton.setObjectName(_fromUtf8("radioButton"))
        self.radioButton.setChecked(True)
        self.buttonGroup = QtWidgets.QButtonGroup(Dialog_assignAttributes)
        self.buttonGroup.setObjectName(_fromUtf8("buttonGroup"))
        self.buttonGroup.addButton(self.radioButton)
        self.radioButton_2 = QtWidgets.QRadioButton(Dialog_assignAttributes)
        self.radioButton_2.setGeometry(QtCore.QRect(280, 19, 81, 20))
        self.radioButton_2.setObjectName(_fromUtf8("radioButton_2"))
        self.buttonGroup.addButton(self.radioButton_2)
        self.label = QtWidgets.QLabel(Dialog_assignAttributes)
        self.label.setGeometry(QtCore.QRect(20, 20, 161, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.tableWidget = QtWidgets.QTableWidget(Dialog_assignAttributes)
        self.tableWidget.setGeometry(QtCore.QRect(10, 50, 831, 421))
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)

        #ADDIN
        self.fillTableWidget()
        self.radioButton.clicked.connect(self.selectCases)
        self.radioButton_2.clicked.connect(self.selectFiles)
        self.tableWidget.cellChanged.connect(self.cellModified)
        #END ADDIN

        self.retranslateUi(Dialog_assignAttributes)
        QtCore.QMetaObject.connectSlotsByName(Dialog_assignAttributes)

    def retranslateUi(self, Dialog_assignAttributes):
        Dialog_assignAttributes.setWindowTitle(_translate("Dialog_assignAttributes", "Assign attributes to cases and files", None))
        self.radioButton.setText(_translate("Dialog_assignAttributes", "Cases", None))
        self.radioButton_2.setText(_translate("Dialog_assignAttributes", "Files", None))
        self.label.setText(_translate("Dialog_assignAttributes", "Assign attributes to:", None))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_assignAttributes = QtWidgets.QDialog()
    ui = Ui_Dialog_assignAttributes()
    ui.setupUi(Dialog_assignAttributes)
    Dialog_assignAttributes.show()
    sys.exit(app.exec_())
