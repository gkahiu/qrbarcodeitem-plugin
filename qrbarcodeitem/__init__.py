# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : QRBarCodePlugin
Description          : Plugin for adding Qr Code and barcode layout in a print
                       layout
Date                 : 07-07-2020
copyright            : (C) 2020 by John Gitau
                       See the accompanying file CONTRIBUTORS.txt in the root
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
from .plugin import QRBarCodePluginLoader


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load the plugin loader class

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    return QRBarCodePluginLoader(iface)
