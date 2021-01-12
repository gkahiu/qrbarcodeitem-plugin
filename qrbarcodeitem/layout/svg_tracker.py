# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : SvgFileTracker
Description          : Clears SVG files - used to render barcode items - in
                       the temp directory when plugin is being unloaded.
Date                 : 12-01-2021
copyright            : (C) 2021 by John Gitau
email                : gkahiu@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QFile

from qrbarcodeitem.utils import Singleton


@Singleton
class SvgFileTracker:
    """
    Used to track and delete SVG files used to render the barcode items.
    """
    def __init__(self):
        self._files = []

    @property
    def files(self):
        """
        :return: Returns a list containing temporary files which will be
        deleted when plugin is being unloaded.
        :rtype: list
        """
        return self._files

    def add_file(self, file_path):
        """
        Add file path to the collection.
        :param file_path: Path to SVG file.
        :type file_path: str
        """
        if file_path not in self._files:
            self._files.append(file_path)

    def clean_up(self):
        """
        Deletes all the tracked SVG files. Usually called when the plugin is
        being unloaded.
        """
        for sf in self._files:
            if QFile.exists(sf):
                QFile.remove(sf)
