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

from PyQt5 import QtGui, QtWidgets
import csv
import datetime


class ImportAttributes():
    """ Import case and file attributes from a csv file. Loading strings as unicode.
    The first row must contain the attribute names.
    The first cell of the first row must contain either 'case' or 'file'
    this then allows automatic assignment of attributes
    to case attributes or file attributes."""

    values = None  # obtained from csv file
    settings = None
    attributes = None  # attribute names obtained from csv file
    storedAttributes = None  # atribute names already in database
    attributesTable = ""  # case or source
    casesOrFiles = None
    log = ""

    def __init__(self, settings):
        self.settings = settings
        self.attributes = []
        self.attributesType = []
        self.values = []
        self.storedAttributes = []
        self.casesOrFiles = []
        self.log = ""

        cur = self.settings['conn'].cursor()
        cur.execute("select name, status, date, dateM, owner, memo, class from attributes")
        result = cur.fetchall()
        for row in result:
            self.storedAttributes.append({'name':row[0], 'status':row[1], 'date':row[2],
            'dateM':row[3], 'owner':row[4], 'memo':row[5], 'class':row[6]})

        fileName = str(QtWidgets.QFileDialog.getOpenFileName(None, 'Open file', ""))
        #if fileName == "":
        #return
        if fileName[-4:] != ".csv":
            QtWidgets.QMessageBox.warning(None, "Warning",
                 str(fileName) + "\nis not a CSV file.\nFile not imported", QtWidgets.QMessageBox.Ok)
            return
        with open(fileName, 'rb') as f:
            '''can change the dialect from csv.excel to others
            csv.register_dialect('MyDialect', delimiter='\t',doublequote=False,quotechar='',
                lineterminator='\n',escapechar='',quoting=csv.QUOTE_MIMIMAL)
            there's also an excel-tab dialect see http://pymotw.com/2/csv/
            '''
            #reader = csv.reader(f)
            reader = self.unicode_csv_reader(f, csv.excel)
            try:
                for row in reader:
                    self.values.append(row)
            except csv.Error as e:
                print(('file %s, line %d: %s' % (fileName, reader.line_num, e)))

        self.attributes = self.values[0]
        self.attributesType = [""] * len(self.attributes)
        self.values.remove(self.attributes)

        if len(self.attributes) == 1 or len(self.values) == 0:
            QtWidgets.QMessageBox.warning(None, "Error",
            "The file contains no attributes\nFile not imported", QtWidgets.QMessageBox.Ok)
            return
        for att in self.attributes:
            if att == "":
                QtWidgets.QMessageBox.warning(None, "Error",
                 "Blank attribute name\nFile not imported", QtWidgets.QMessageBox.Ok)
                return

        self.attributesTable = ""
        if self.attributes[0].lower() == "case" or self.attributes[0].lower() == "cases":
            self.attributesTable = "caseAttr"
        if self.attributes[0].lower() == "file" or self.attributes[0].lower() == "files":
            self.attributesTable = "fileAttr"
        if self.attributesTable == "":
            QtWidgets.QMessageBox.warning(None, "Error",
              "The first column must contain Case or File names\nFile not imported", QtWidgets.QMessageBox.Ok)
            return

        # find attribute type
        for col, att in enumerate(self.attributes):
            numeric = True
            for val in self.values:
                try:
                    float(val[col])
                except ValueError:
                    numeric = False
            if numeric:
                self.attributesType[col] = "numeric"
            else:
                self.attributesType[col] = "character"

            isStoredAtt = False
            for sAtt in self.storedAttributes:
                if sAtt['name'].lower() == att.lower():
                    isStoredAtt = True

            if isStoredAtt == False and col > 0:
                # add the attribute
                item = {'name':att.encode('raw_unicode_escape'), 'memo':"", 'owner':self.settings['codername'],
                'date':datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
                'dateM':"", 'status':1, 'class':self.attributesType[col]}
                cur = self.settings['conn'].cursor()
                cur.execute("insert into attributes (name,status,date,dateM,owner,memo,class) values(?,?,?,?,?,?,?)"
                , (item['name'], item['status'], item['date'], item['dateM'], item['owner'], item['memo'], item['class']))
                self.settings['conn'].commit()

        # add attribute values
        # first, delete all values where the variable and caseid or fileid match
        idType = "caseId"
        idTable = "cases"
        if self.attributesTable == "fileAttr":
            idType = "fileId"
            idTable = "source"
        cur = self.settings['conn'].cursor()
        sql = "select name, id, status from " + idTable
        cur.execute(sql)
        result = cur.fetchall()
        for row in result:
            for val in self.values:
                if val[0] == row[0]:
                    val[0] = row[1]

        for val in self.values:
            for col, value in enumerate(val):
                if col > 0:
                    sql = "delete from " + self.attributesTable + " where variable = ? and "\
                     + idType + " = (select id from " + idTable + " where name = ?)"
                    #print sql, self.attributes[col], val[0]
                    cur.execute(sql, (self.attributes[col], val[0]))

                    sql = "insert into " + self.attributesTable + " (variable, value, "\
                     + idType + ", date, dateM, owner, status) values (?,?,?,?,?,?,?)"
                    cur.execute(sql, (self.attributes[col], val[col], val[0],
                     datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), ""
                    , self.settings['codername'], 1))
        self.settings['conn'].commit()
        self.log += "Attributes from " + fileName + " imported\n"

    def getLog(self):
        """ Get details of file movments """
        return self.log

    """ The two methods below are based on examples from
    http://docs.python.org/2/library/csv.html#csv-examples
    to be able to import unicode formatted csv files """

    def unicode_csv_reader(self, unicode_csv_data, dialect, **kwargs):
            # csv.py doesn't do Unicode; encode temporarily as UTF-8:
            csv_reader = csv.reader(self.utf_8_encoder(unicode_csv_data),
                                    dialect=dialect, **kwargs)
            for row in csv_reader:
                # decode UTF-8 back to Unicode, cell by cell:
                yield [unicode(cell, 'utf-8') for cell in row]

    def utf_8_encoder(self, unicode_csv_data):
            for line in unicode_csv_data:
                yield line.encode('utf-8')
