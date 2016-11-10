# -*- coding: utf-8 -*-

"""
***************************************************************************
    templatewriter.py
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
import uuid
import json
import shutil
import codecs

from PyQt4.QtCore import pyqtSignal, Qt, QObject, QSize
from PyQt4.QtGui import QImage, QPainter

from qgis.core import (QgsComposerLegend,
                       QgsComposerShape,
                       QgsComposerScaleBar,
                       QgsComposerArrow,
                       QgsComposerLabel,
                       QgsComposerMap,
                       QgsComposerPicture
                      ) 


class TemplateWriter(QObject):
    
    composerExported = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)

    def setFilePath(self, filePath):
        self.filePath = filePath
        self.imagePath = os.path.join(os.path.dirname(filePath), "resources")

    def setComposers(self, composers):
        self.composers = composers

    def export(self):
        if not os.path.isdir(self.imagePath):
            os.mkdir(self.imagePath)
        
        total = 100.0 / len(self.composers)

        dpis = [72, 150, 300]
        layouts = []
        for i, c in enumerate(self.composers):
            name = c.composerWindow().windowTitle()
            safeName = self._safeName(name)
            
            composition = c.composition()
            img = composition.printPageAsRaster(0)
            img = img.scaledToHeight(100, Qt.SmoothTransformation)
            img.save(os.path.join(self.imagePath, "{}_thumbnail.png".format(safeName)))
            
            layoutDef = {}
            layoutDef["name"] = name
            layoutDef["width"] = composition.paperWidth()
            layoutDef["height"] = composition.paperHeight()
            layoutDef["thumbnail"] = "{}_thumbnail.png".format(safeName)
            
            elements = []
            layoutDef["elements"] = elements
            for item in composition.items():
                element = None
                if isinstance(item, (QgsComposerLegend, QgsComposerShape, QgsComposerScaleBar, QgsComposerArrow)):
                    element = self._basicInfo(item)
                    for dpi in dpis:
                        dpmm = dpi / 25.4
                        s = QSize(item.rect().width() * dpmm, item.rect().height() * dpmm)
                        img = QImage(s, QImage.Format_ARGB32_Premultiplied)
                        img.fill(Qt.transparent)
                        painter = QPainter(img)
                        painter.scale(dpmm, dpmm)
                        item.paint(painter, None, None)
                        painter.end()
                        img.save(os.path.join(self.imagePath, "{}_{}_{}.png".format(safeName, element["id"], dpi)))
                elif isinstance(item, QgsComposerLabel):
                    element = self._basicInfo(item)
                    element["name"] = item.text()
                    element["size"] = item.font().pointSize()
                    element["font"] = item.font().rawName()
                elif isinstance(item, QgsComposerMap):
                    element = self._basicInfo(item)
                    grid = item.grid()
                    if grid is not None:
                        element["grid"] = {}
                        element["grid"]["intervalX"] = grid.intervalX()
                        element["grid"]["intervalY"] = grid.intervalY()
                        element["grid"]["crs"] = grid.crs().authid()
                        element["grid"]["annotationEnabled"] = grid.annotationEnabled()
                elif isinstance(item, QgsComposerPicture):
                    filename = os.path.basename(item.picturePath())
                    if os.path.exists(filename):
                        element = self._basicInfo(item)
                        shutil.copy(item.pictureFile(), os.path.join(self.imagePath, filename))
                        element["file"] = filename
                
                if element is not None:
                    element["type"] = item.__class__.__name__[11:].lower()
                    elements.append(element)

            layouts.append(layoutDef)
            self.composerExported.emit(int(i * total))

        with codecs.open(self.filePath, "w", "utf-8") as f:
            f.write(json.dumps(layouts))

        self.finished.emit()
            
    def _basicInfo(self, item):
        coords = {}
        pos = item.pos()
        coords["x"] = pos.x()
        coords["y"] = pos.y()
        rect = item.rect()
        coords["width"] = rect.width()
        coords["height"] = rect.height()
        coords["id"] = uuid.uuid4().hex
        return coords
    
    def _safeName(self, name):
        validChars = "123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
        return "".join(c for c in name if c in validChars).lower()
