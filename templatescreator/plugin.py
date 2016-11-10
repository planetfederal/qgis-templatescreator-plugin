# -*- coding: utf-8 -*-

"""
***************************************************************************
    plugin.py
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

import os
import webbrowser

from PyQt4.QtCore import (QCoreApplication,
                          QSettings,
                          QLocale,
                          QTranslator
                         )
from PyQt4.QtGui import (QAction,
                         QIcon
                        )

from qgis.core import QgsApplication

from templatescreator.gui.composersdialog import ComposersDialog

pluginPath = os.path.dirname(__file__)


class PrintTemplatesCreator:
    def __init__(self, iface):
        self.iface = iface
        try:
            from .tests import testerplugin
            from qgistester.tests import addTestModule
            addTestModule(testerplugin, "Print Templates Creator")
        except:
            pass

        try:
            from lessons import addLessonsFolder
            folder = os.path.join(os.path.dirname(__file__), "_lessons")
            addLessonsFolder(folder)
        except:
            pass

        overrideLocale = QSettings().value("locale/overrideFlag", False, bool)
        if not overrideLocale:
            locale = QLocale.system().name()[:2]
        else:
            locale = QSettings().value("locale/userLocale", "")

        qmPath = "{}/i18n/templatescreator_{}.qm".format(pluginPath, locale)

        if os.path.exists(qmPath):
            self.translator = QTranslator()
            self.translator.load(qmPath)
            QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        self.runAction = QAction(
            self.tr("Print templates creator"), self.iface.mainWindow())
        self.runAction.setIcon(
            QIcon(os.path.join(pluginPath, "icons", "print.svg")))
        self.runAction.setWhatsThis(
            self.tr("Generate Print JSON from QGIS composer layout"))
        self.runAction.setObjectName("printTemplatesCreatorRun")
        self.runAction.triggered.connect(self.run)

        self.helpAction = QAction(self.tr("Help"), self.iface.mainWindow())
        self.helpAction.setIcon(
            QgsApplication.getThemeIcon('/mActionHelpAPI.png'))
        self.helpAction.setObjectName("printTemplatesCreatorHelp")
        self.helpAction.triggered.connect(lambda: webbrowser.open_new(
                        "file://{}".format(os.path.join(os.path.dirname(__file__), "docs", "html", "index.html"))))

        self.iface.addWebToolBarIcon(self.runAction)
        self.iface.addPluginToWebMenu(self.tr("Print templates creator"), self.runAction)
        self.iface.addPluginToWebMenu(self.tr("Print templates creator"), self. helpAction)

    def unload(self):
        try:
            from .tests import testerplugin
            from qgistester.tests import removeTestModule
            removeTestModule(testerplugin, "Print Templates Creator")
        except:
            pass

        self.iface.removeWebToolBarIcon(self.runAction)
        self.iface.removePluginWebMenu(self.tr("Print templates creator"), self.runAction)
        self.iface.removePluginWebMenu(self.tr("Print templates creator"), self. helpAction)

    def run(self):
        dlg = ComposersDialog(self.iface, self.iface.mainWindow())
        dlg.show()
        dlg.exec_()

    def tr(self, text):
        return QCoreApplication.translate('Print Templates Creator', text)
