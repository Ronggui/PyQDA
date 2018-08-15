#!/usr/bin/python
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


Copyright (c) 2017-2018 Rongui Huang

Port to Python 3 and PyQt5
'''

"""
Main loop and main view.
"""
## for pyinstaller to find required packages
import logging
try:
    from lxml import etree
except:
    from xml import etree
# note lxml is not installed on all OS, may then try xml module instead
try:
    from PIL import Image
except ImportError:
    import Image
import zipfile
import shutil
import re
import time
import os
from os.path import join
import re
##
import sys
import datetime
import sqlite3
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from .Codes import Ui_Dialog_codes
from .Categories import Ui_Dialog_cats
from .FileCategories import Ui_Dialog_fcats
from .Settings import Ui_Dialog_settings
from .ManageFiles import Ui_Dialog_manageFiles
from .ManageJournals import Ui_Dialog_manageJournals
from .Cases import Ui_Dialog_cases
from .Memo import Ui_Dialog_memo
from .Codebook import Ui_Dialog_codebook
from .Attributes import Ui_Dialog_Attributes
from .AssignAttributes import Ui_Dialog_assignAttributes
from .ImportAttributes import ImportAttributes
from .Information import Ui_Dialog_information
from .ReportCodings import Ui_Dialog_reportCodings
from .SQL import Ui_Dialog_sql
from .CodingSummary import CodingSummary
from .ViewCodeFrequencies import Ui_Dialog_vcf

class MainView(QtWidgets.QMainWindow):
    """
    Main GUI window.
    SQLite databases need extension .rqda
    """

    qdaFileName = ""  # directory and file name
    logWidget = None

    settings = {"conn": None, "directory": "", "projectName": "", "showIDs":False,
    "codername": "default", "codertable": "coding", "fontSize": 14, "size": ""}
    project = {"databaseversion": "", "date": "", "dateM": "", "memo": "",
    "about": "", "imagDir": ""}

    def __init__(self):
        super(MainView, self).__init__()
        self.statusBar().showMessage('Ready')
        self.move(10, 10)
        self.resize(700, 500)
        self.setWindowTitle('Py3QDA')
        self.menu()
        self.logWidget = MainWidget(self)
        self.setCentralWidget(self.logWidget)
        self.show()

    def menu(self):
        menubar = self.menuBar()

        # project menu
        newProjectAction = QtWidgets.QAction('Create new project', self)
        newProjectAction.triggered.connect(self.newProject)
        newProjectAction.setStatusTip('Create new project')

        openProjectAction = QtWidgets.QAction('Open project', self)
        openProjectAction.triggered.connect(self.openProject)
        openProjectAction.setStatusTip('Open project')

        memoAction = QtWidgets.QAction('Project memo', self)
        memoAction.triggered.connect(self.projectMemo)
        memoAction.setStatusTip('Project memo')

        closeProjectAction = QtWidgets.QAction('Close project', self)
        closeProjectAction.triggered.connect(self.closeProject)
        closeProjectAction.setStatusTip('Close current project')

        settingsAction = QtWidgets.QAction('Settings', self)
        settingsAction.triggered.connect(self.setSettings)
        settingsAction.setStatusTip('Settings')

        exitAction = QtWidgets.QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit')
        exitAction.triggered.connect(self.quitApplication)

        projectMenu = menubar.addMenu('&Project')
        projectMenu.addAction(newProjectAction)
        projectMenu.addAction(openProjectAction)
        projectMenu.addAction(memoAction)
        projectMenu.addAction(closeProjectAction)
        projectMenu.addAction(settingsAction)
        projectMenu.addAction(exitAction)

        # file cases and journals menu
        manageFileAction = QtWidgets.QAction('Manage files', self)
        manageFileAction.triggered.connect(self.manageFiles)
        manageFileAction.setStatusTip('manage files')

        fileCategoryAction = QtWidgets.QAction('File categories', self)
        fileCategoryAction.triggered.connect(self.fileCategories)
        fileCategoryAction.setStatusTip('manage file categories')

        journalAction = QtWidgets.QAction('Manage journals', self)
        journalAction.triggered.connect(self.journals)
        journalAction.setStatusTip('Manage journals')

        casesAction = QtWidgets.QAction('Manage cases', self)
        casesAction.triggered.connect(self.manageCases)
        casesAction.setStatusTip('Cases')

        fileMenu = menubar.addMenu('&Files and Cases')
        fileMenu.addAction(manageFileAction)
        fileMenu.addAction(casesAction)
        fileMenu.addAction(fileCategoryAction)
        fileMenu.addAction(journalAction)

        # codes menu
        codesAction = QtWidgets.QAction('Codes', self)
        codesAction.triggered.connect(self.manageCodes)
        codesAction.setStatusTip('Codes')

        categoriesAction = QtWidgets.QAction('Categories', self)
        categoriesAction.triggered.connect(self.codeCategories)
        categoriesAction.setStatusTip('Categories')

        codebookAction = QtWidgets.QAction('Codebook', self)
        codebookAction.triggered.connect(self.showCodebook)
        codebookAction.setStatusTip('Codebook')

        codesMenu = menubar.addMenu('&Coding')
        codesMenu.addAction(codesAction)
        codesMenu.addAction(categoriesAction)
        codesMenu.addAction(codebookAction)

        #attributes menu
        attrAction = QtWidgets.QAction('Manage attributes', self)
        attrAction.triggered.connect(self.manageAttributes)
        attrAction.setStatusTip('Manage Attributes')

        attrAssignAction = QtWidgets.QAction('Assign attributes', self)
        attrAssignAction.triggered.connect(self.assignAttributes)
        attrAssignAction.setStatusTip('Assign Attributes')

        attrImportAction = QtWidgets.QAction('Import attributes', self)
        attrImportAction.triggered.connect(self.importAttributes)
        attrImportAction.setStatusTip('Import Attributes')

        attrMenu = menubar.addMenu('Attributes')
        attrMenu.addAction(attrAction)
        attrMenu.addAction(attrAssignAction)
        attrMenu.addAction(attrImportAction)

        # reports menu
        repCodeAction = QtWidgets.QAction('Coding reports', self)
        repCodeAction.triggered.connect(self.repCoding)
        repCodeAction.setStatusTip('Coding reports')

        repSummaryAction = QtWidgets.QAction('Coding summary', self)
        repSummaryAction.triggered.connect(self.repSummary)
        repSummaryAction.setStatusTip('coding summary')

        repSqlAction = QtWidgets.QAction('SQL statements', self)
        repSqlAction.triggered.connect(self.repSql)
        repSqlAction.setStatusTip('SQL statements')

        repProfileMatrixAction = QtWidgets.QAction('Case profile', self)
        repProfileMatrixAction.triggered.connect(self.repProfileMatrix)
        repProfileMatrixAction.setStatusTip('Case profile matrix')

        reportsMenu = menubar.addMenu('Reports')
        reportsMenu.addAction(repCodeAction)
        reportsMenu.addAction(repSummaryAction)
        reportsMenu.addAction(repProfileMatrixAction)
        reportsMenu.addAction(repSqlAction)


        # help menu
        helpAction = QtWidgets.QAction('Help', self)
        helpAction.triggered.connect(self.help)
        helpAction.setStatusTip('Help')

        aboutAction = QtWidgets.QAction('About', self)
        aboutAction.triggered.connect(self.about)
        aboutAction.setStatusTip('About Py3QDA')

        helpMenu = menubar.addMenu("Help")
        helpMenu.addAction(helpAction)
        helpMenu.addAction(aboutAction)

    def repSql(self):
        """ Run SQL statements on database """

        if self.settings["projectName"] == "":
            QtWidgets.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return
        Dialog_s = QtWidgets.QDialog()
        ui = Ui_Dialog_sql(self.settings)
        ui.setupUi(Dialog_s)
        Dialog_s.exec_()
        if ui.getLog() != "":
            self.logWidget.textEdit.append(ui.getLog())
        self.statusBar().showMessage("SQL statements")


    def repCoding(self):
        """ report on coding dialog """

        if self.settings["projectName"] == "":
            QtWidgets.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return

        self.statusBar().showMessage("Coding report")
        Dialog_c = QtWidgets.QDialog()
        ui = Ui_Dialog_reportCodings(self.settings)
        ui.setupUi(Dialog_c)
        Dialog_c.exec_()
        if ui.getLog() != "":
            self.logWidget.textEdit.append(ui.getLog())
        self.statusBar().showMessage("Ready")

    def repProfileMatrix(self):
        if self.settings["projectName"] == "":
            QtWidgets.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return
        conn = self.settings['conn']
        cur = conn.cursor()
        cur.execute("select name from cases where status=1")
        result = cur.fetchall()
        selectedCases = [ _[0] for _ in result ]
        if len(selectedCases) == 0:
            QtWidgets.QMessageBox.warning(None, "Non cases have been defined.", "You need to define cases.")
            return
        cur.execute("select name, id, cid from freecode, coding where coding.cid=freecode.id and freecode.status=1 group by cid order by name")
        result = cur.fetchall()
        codes = []
        for code in result:
            codes.append(code[0])
        Mat = {}
        for case in selectedCases:
            val = []
            for code in codes:
                cur.execute("select count(coding.fid) as n from coding, freecode where coding.cid=freecode.id and freecode.name=? and coding.fid in \
                    (select fid from caselinkage, cases where caselinkage.caseid=cases.id and cases.name=?)", (code, case))
                result = cur.fetchall()
                for n in result:
                    val.append(str(n[0]))
            Mat[case] = val
        Dialog_vcf = QtWidgets.QDialog()
        ui = Ui_Dialog_vcf(Mat, conn)
        ui.setupUi(Dialog_vcf)
        ui.tableWidget.setVerticalHeaderLabels(codes)
        # hack to display code names
        Dialog_vcf.exec_()

    def repSummary(self):
        """ A summary of each code by code count, average characters and average word count """

        CodingSummary(self.settings)

    def help(self):
        """ Help dialog """

        self.statusBar().showMessage("Help")
        Dialog_help = QtWidgets.QDialog()
        ui = Ui_Dialog_information("Help", "Help.html")
        ui.setupUi(Dialog_help)
        Dialog_help.exec_()
        self.statusBar().showMessage("Ready")

    def about(self):
        """ About dialog """

        self.statusBar().showMessage("About Py3QDA")
        Dialog_about = QtWidgets.QDialog()
        ui = Ui_Dialog_information("About", "About.html")
        ui.setupUi(Dialog_about)
        Dialog_about.exec_()
        self.statusBar().showMessage("Ready")

    def manageAttributes(self):
        """ Create, edit, delete, rename attributes """

        if self.settings["projectName"] == "":
            QtWidgets.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return

        self.statusBar().showMessage("Manage Attributes")
        Dialog_manageAttributes = QtWidgets.QDialog()
        ui = Ui_Dialog_Attributes(self.settings)
        ui.setupUi(Dialog_manageAttributes)
        Dialog_manageAttributes.exec_()
        self.statusBar().showMessage("Ready")

    def assignAttributes(self):
        """ Assign attributes to files and cases """

        if self.settings["projectName"] == "":
            QtWidgets.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return

        self.statusBar().showMessage("Assign Attributes")
        Dialog_assAttributes = QtWidgets.QDialog()
        ui = Ui_Dialog_assignAttributes(self.settings)
        ui.setupUi(Dialog_assAttributes)
        Dialog_assAttributes.exec_()
        self.statusBar().showMessage("Ready")

    def importAttributes(self):
        """ Import attributes and assign to cases or files """

        if self.settings["projectName"] == "":
            QtWidgets.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return
        impAttr = ImportAttributes(self.settings)
        if impAttr.getLog() != "":
            self.logWidget.textEdit.append(impAttr.getLog())

    def manageCases(self):
        """ Create, edit, delete, rename cases, add cases to files or parts of
        files, add memos to cases """

        if self.settings["projectName"] == "":
            QtWidgets.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return

        self.statusBar().showMessage("Manage cases")
        Dialog_manageCases = QtWidgets.QDialog()
        ui = Ui_Dialog_cases(self.settings)
        ui.setupUi(Dialog_manageCases)
        Dialog_manageCases.exec_()
        self.statusBar().showMessage("Ready")

    def manageFiles(self):
        """ Create text files or import files from odt, docx, html and
        plain text. rename, delete and add memos to files """

        if self.settings["projectName"] == "":
            QtWidgets.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return
        self.statusBar().showMessage("Manage files")
        Dialog_manageFiles = QtWidgets.QDialog()
        ui = Ui_Dialog_manageFiles(self.settings)
        ui.setupUi(Dialog_manageFiles)
        Dialog_manageFiles.exec_()
        if ui.getLog() != "":
            self.logWidget.textEdit.append(ui.getLog())
        self.statusBar().showMessage("Ready")

    def fileCategories(self):
        """ Create, edit and delete file categories """

        if self.settings["projectName"] == "":
            QtWidgets.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return
        self.statusBar().showMessage("Manage file categories")
        Dialog_fileCategories = QtWidgets.QDialog()
        ui = Ui_Dialog_fcats(self.settings)
        ui.setupUi(Dialog_fileCategories)
        Dialog_fileCategories.exec_()
        self.statusBar().showMessage("Ready")

    def journals(self):
        """ Create journals """

        if self.settings["projectName"] == "":
            QtWidgets.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return
        self.statusBar().showMessage("Journals")
        Dialog_manageJournals = QtWidgets.QDialog()
        ui = Ui_Dialog_manageJournals(self.settings)
        ui.setupUi(Dialog_manageJournals)
        Dialog_manageJournals.exec_()
        if ui.getLog() != "":
            self.logWidget.textEdit.append(ui.getLog())
        self.statusBar().showMessage("Ready")

    def manageCodes(self):
        """ Create edit and delete codes.
        Apply and remove codes and annotations to the text in text files. """

        if self.settings["projectName"] == "":
            QtWidgets.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return
        self.statusBar().showMessage("Codes")
        Dialog_codes = QtWidgets.QDialog()
        ui = Ui_Dialog_codes(self.settings)
        ui.setupUi(Dialog_codes, self.settings)
        Dialog_codes.exec_()

        self.statusBar().showMessage("Ready")

    def codeCategories(self):
        """ Create, delete and edit code categories """

        if self.settings["projectName"] == "":
            QtWidgets.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return
        self.statusBar().showMessage("Categories")
        Dialog_cats = QtWidgets.QDialog()
        ui = Ui_Dialog_cats(self.settings)
        ui.setupUi(Dialog_cats)
        Dialog_cats.exec_()
        self.statusBar().showMessage("Ready")

    def showCodebook(self):
        """ A codebook is made up of memos attached to codes - rules when to apply codes. """

        if self.settings["projectName"] == "":
            QtWidgets.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return
        self.statusBar().showMessage("Codebook")
        self.Dialog_codebook = QtWidgets.QDialog()
        ui = Ui_Dialog_codebook(self.settings)
        ui.setupUi(self.Dialog_codebook)
        self.Dialog_codebook.exec_()
        if ui.getLog() != "":
            self.logWidget.textEdit.append(ui.getLog())
        self.statusBar().showMessage("Ready")

    def quitApplication(self):
        """ Quit the application and close database connection """

        quit_msg = "Are you sure you want to quit?"
        reply = QtWidgets.QMessageBox.question(self, 'Message', quit_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            if self.settings['conn'] is not None:
                self.settings['conn'].commit()
                self.settings['conn'].close()
            QtWidgets.qApp.quit()

    def newProject(self):
        """ Create a new Sqlite rqda project """

        if self.settings['projectName'] == "":
            self.statusBar().showMessage("Create new project")
            self.qdaFileName = QtWidgets.QFileDialog.getSaveFileName(self, "Enter project name", self.settings['directory'], ".rqda")[0]
            if self.qdaFileName == "":
                QtWidgets.QMessageBox.warning(None, "Project","No project created.")
                return

            if self.qdaFileName.find(".rqda") == -1:
                self.qdaFileName = self.qdaFileName + ".rqda"

            self.settings['projectName'] = self.qdaFileName.rpartition('/')[2]
            self.settings['directory'] = self.qdaFileName.rpartition('/')[0]

            try:
                self.settings['conn'] = sqlite3.connect(self.qdaFileName)  # create new Db
                cur = self.settings['conn'].cursor()
                cur.execute("CREATE TABLE project (databaseversion text, date text,dateM text, memo text,about text, imageDir text);")
                cur.execute("CREATE TABLE source (name text, id integer, file text, memo text, owner text, date text, dateM text, status integer);")
                cur.execute("CREATE TABLE fileAttr (variable text, value text, fileID integer, date text, dateM text, owner text, status integer);")
                cur.execute("CREATE TABLE filecat  (name text,fid integer, catid integer, owner text, date text, dateM text,memo text, status integer);")
                cur.execute("CREATE TABLE annotation (fid integer,position integer,annotation text, owner text, date text,dateM text, status integer);")
                cur.execute("CREATE TABLE attributes (name text, status integer, date text, dateM text, owner text,memo text, class text);")
                cur.execute("CREATE TABLE caseAttr (variable text, value text, caseID integer, date text, dateM text, owner text, status integer);")
                cur.execute("CREATE TABLE caselinkage  (caseid integer, fid integer, selfirst real, selend real, status integer, owner text, date text, memo text);")
                cur.execute("CREATE TABLE cases  (name text, memo text, owner text,date text,dateM text, id integer, status integer);")
                cur.execute("CREATE TABLE codecat  (name text, cid integer, catid integer, owner text, date text, dateM text,memo text, status integer);")
                cur.execute("CREATE TABLE coding  (cid integer, fid integer,seltext text, selfirst real, selend real, status integer, owner text, date text, memo text);")
                cur.execute("CREATE TABLE coding2  (cid integer, fid integer,seltext text, selfirst real, selend real, status integer, owner text, date text, memo text);")
                cur.execute("CREATE TABLE freecode  (name text, memo text, owner text,date text,dateM text, id integer, status integer, color text);")
                cur.execute("CREATE TABLE image (name text, id integer, date text, dateM text, owner text,status integer);")
                cur.execute("CREATE TABLE imageCoding (cid integer,iid integer,x1 integer, y1 integer, x2 integer, y2 integer, memo text, date text, dateM text, owner text,status integer);")
                cur.execute("CREATE TABLE journal (name text, journal text, date text, dateM text, owner text,status integer);")
                cur.execute("CREATE TABLE treecode  (cid integer, catid integer, date text, dateM text, memo text, status integer, owner text);")
                cur.execute("CREATE TABLE treefile  (fid integer, catid integer, date text,dateM text, memo text, status integer,owner text);")
                cur.execute("INSERT INTO project VALUES(?,?,?,?,?,?)", ('DBVersion:0.1',datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"),'','','Database created by PyQDA based on RQDA',''))
                self.settings['conn'].commit()
                self.logWidget.textEdit.append("\nNew project: "+self.qdaFileName+" created.")
            except:
                self.logWidget.textEdit.append("\nProblems creating Db\n" + self.qdaFileName)
                self.closeProject()
        self.statusBar().showMessage("Ready")

    def setSettings(self):
        """ Change default settings - the coder name, coder table, font**, font size** TODO """

        self.statusBar().showMessage("Settings")
        Dialog_settings = QtWidgets.QDialog()
        ui = Ui_Dialog_settings(self.settings)
        ui.setupUi(Dialog_settings)
        Dialog_settings.exec_()
        self.statusBar().showMessage("Ready")
        msg = "Coder:" + self.settings['codername'] + ", CoderTable:"+  self.settings['codertable'] + ", "
        msg += "Font Size:" + str(self.settings['fontSize'])
        msg += ", ShowIDs:" + str(self.settings['showIDs'])
        self.logWidget.textEdit.append("Settings: " + msg)

    def projectMemo(self):
        """ Give the entire project a memo """

        if self.settings["projectName"] == "":
            QtWidgets.QMessageBox.warning(None, "No Project","You need to load or create a project first.")
            return
        Dialog_memo = QtWidgets.QDialog()
        ui = Ui_Dialog_memo(self.project['memo'])
        ui.setupUi(Dialog_memo, "Project memo " + self.settings['projectName'])
        Dialog_memo.exec_()
        self.project['memo'] = ui.getMemo()
        cur = self.settings['conn'].cursor()
        cur.execute("update project set memo=?", [str(self.project['memo'])])
        self.settings['conn'].commit()
        self.logWidget.textEdit.append("Project memo entered")

    def openProject(self):
        """ Open an existing project """

        if self.settings['projectName'] != "":
            self.closeProject()

        self.statusBar().showMessage("Open project")
        self.qdaFileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', self.settings['directory'])[0] # return a tuple, the first is filepath
        if self.qdaFileName == "":
            return
        if len(self.qdaFileName) > 4 and self.qdaFileName[-5:] == ".rqda":
            try:
                self.settings['conn'] = sqlite3.connect(self.qdaFileName)
            except:
                self.settings['conn'] = None
        if self.settings['conn'] is None:
            QtWidgets.QMessageBox.warning(None, "Cannot open file", self.qdaFileName + " is not an .rqda file")
            self.qdaFileName = ""
        else:
            # get and display some project details
            self.settings['projectName'] = self.qdaFileName.rpartition('/')[2]
            self.logWidget.textEdit.append("Opening: " + self.qdaFileName)
            self.setWindowTitle(self.settings['projectName'])
            cur = self.settings['conn'].cursor()
            cur.execute('select sqlite_version()')
            self.logWidget.textEdit.append("SQLite version: " + str(cur.fetchone()))
            cur.execute("select databaseversion, date, dateM, memo, about, imageDir from project")
            result = cur.fetchone()
            self.project['databaseversion'] = result[0]
            self.project['date'] = result[1]
            self.project['dateM'] = result[2]
            self.project['memo'] = result[3]
            self.project['about'] = result[4]
            self.project['imageDir'] = result[5]
            self.logWidget.textEdit.append("DBVersion:" + str(self.project['databaseversion']) + "\n"
                                            + "Date: " + str(self.project['date']) + "\n"
                                            + "About: " + str(self.project['about']) + "\n"
                                            + "Image Directory: " + str(self.project['imageDir']) + "\n"
                                            + "Coder:" + str(self.settings['codername'])
                                            + "   Table:" + str(self.settings['codertable']) + "\n")

        self.setCentralWidget(self.logWidget)
        self.statusBar().showMessage("Ready")

    def closeProject(self):
        """ CLose an open project """

        if self.settings["projectName"] == "":
            QtWidgets.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return
        self.setCentralWidget(self.logWidget)
        self.logWidget.textEdit.append("Closing project: " + self.settings['projectName'] + "\n")
        try:
            self.settings['conn'].commit()
            self.settings['conn'].close()
        except:
            pass
        self.conn = None
        self.qdaFileName = ""
        self.settings['projectName'] = ""
        self.project = {"databaseversion": "", "date": "", "dateM": "",
        "memo": "", "about": "", "imagDir": ""}
        self.setWindowTitle("Main")


class MainWidget(QtWidgets.QWidget):
    textEdit = None

    def __init__(self, parent):
        super(MainWidget, self).__init__(parent)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.textEdit = QtWidgets.QTextEdit()
        self.textEdit.setReadOnly(True)
        self.layout.addWidget(self.textEdit)


def main():
    app = QtWidgets.QApplication(sys.argv)
    mainview = MainView()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
