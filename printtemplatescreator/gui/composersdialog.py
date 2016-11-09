# -*- coding: utf-8 -*-

"""
***************************************************************************
    __init__.py
    ---------------------
    Date                 : November 2016
    Copyright            : (C) 2016 Boundless, http://boundlessgeo.com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Alexander Bruy'
__date__ = 'November 2016'
__copyright__ = '(C) 2016 Boundless, http://boundlessgeo.com'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'


import os
import webbrowser

from PyQt4 import uic
from PyQt4.QtCore import Qt, QSettings
from PyQt4.QtGui import QApplication, QListWidgetItem, QPushButton, QDialogButtonBox, QFileDialog

from qgis.core import QgsApplication
from qgis.gui import QgsMessageBar

pluginPath = os.path.split(os.path.dirname(__file__))[0]
WIDGET, BASE = uic.loadUiType(
    os.path.join(pluginPath, "ui", "composersdialogbase.ui"))


class ComposersDialog(BASE, WIDGET):
    def __init__(self, iface, parent=None):
        super(ComposersDialog, self).__init__(parent)
        self.setupUi(self)

        self.iface = iface
        
        self.btnSave = QPushButton(self.tr("Save"))
        self.btnSave.setIcon(QgsApplication.getThemeIcon("/mActionFileSave.svg"))
        self.btnSave.clicked.connect(self.saveToFile)
        #self.btnCopy = QPushButton(self.tr("Copy"))
        #self.btnCopy.setIcon(QgsApplication.getThemeIcon("/mActionEditCopy.svg"))
        #self.btnCopy.clicked.connect(self.copyToClipboard)

        self.buttonBox.addButton(self.btnSave, QDialogButtonBox.ActionRole)
        #self.buttonBox.addButton(self.btnCopy, QDialogButtonBox.ActionRole)

        #self.buttonBox.helpRequested.connect()

        self.composers = None
        self.loadComposers()

    def loadComposers(self):
        self.lstComposers.clear()

        self.composers = {c.composerWindow().windowTitle(): c for c in  self.iface.activeComposers()}
        if len(self.composers) > 0:
            self.lstComposers.addItems(self.composers.keys())
            self.lstComposers.sortItems()
        else:
            item = QListWidgetItem(self.tr("No composers found"))
            item.setFlags(item.flags() ^ Qt.ItemIsEnabled)
            self.lstComposers.addItem(item)
        self.toggleButtons()

    def saveToFile(self):
        settings = QSettings("Boundless", "PrintTemplatesCreator")
        lastDirectory = settings.value("lastUsedDirectory", "")
        filePath = QFileDialog.getSaveFileName(self,
                                               self.tr("Save file"),
                                               lastDirectory,
                                               self.tr("JSON files (*.json *.JSON)")
                                              )
        if filePath == "":
            return

        if not filePath.lower().endswith(".json"):
            filePath += ".json"

        settings.setValue("lastUsedDirectory", os.path.abspath(os.path.dirname(filePath)))

        # TODO: export to JSON

    def copyToClipboard(self):
        # TODO: export to JSON
        clipboard = QApplication.clipboard()
        clipboard.setText()
        self.showMessage(self.tr("Selected composers sucessfully exported and copied to clipboard."))

    def exportToJson(self, composers):
        # TODO: export to JSON
        self.showMessage(self.tr("Selected composers successfully exported and saved."))

    def toggleButtons(self):
        if self.composers is None or len(self.composers) == 0:
            self.btnSave.setEnabled(False)
            #self.btnCopy.setEnabled(False)
        else:
            self.btnSave.setEnabled(True)
            #self.btnCopy.setEnabled(True)

    def showMessage(self, msg, level=QgsMessageBar.INFO):
        self.iface.messageBar.pushMessage(
                msg, level, self.iface.messageTimeout())
