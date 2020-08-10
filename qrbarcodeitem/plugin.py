# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : QRBarCodePluginLoader
Description          : Loader for the QR and bar code layout layout
Date                 : 07-07-2020
copyright            : (C) 2020 by John Gitau
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
import os.path

from qgis.PyQt.QtCore import (
    QSettings,
    QTranslator,
    qVersion,
    QCoreApplication
)

from qrbarcodeitem.layout.registry import register_barcode_items


class QRBarCodePluginLoader:
    """QGIS plugin loader."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'qrc_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

    # noinspection PyMethodMayBeStatic
    def tr(self, message): # pylint: disable=no-self-use
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('QrBarCodeLayoutItem', message)

    def initGui(self): # pylint: disable=no-self-use
        """Register QR and barcode layout items in the QGIS layout
        item registry.
        """
        register_barcode_items()

    def unregister_layout_items(self):
        """Unregister QR and bar code layout."""
        pass

    def unload(self):
        """Removes the qr and bar code layout from the QGIS layout registry."""
        self.unregister_layout_items()
