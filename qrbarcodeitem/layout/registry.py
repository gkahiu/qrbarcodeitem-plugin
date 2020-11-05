# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Item Registry
Description          : Registers barcode items in app item registry.
Date                 : 10-08-2020
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
from qgis.core import QgsApplication

from qrbarcodeitem.layout.qrcode_item import (
    QrCodeLayoutItemMetadata
)
from qrbarcodeitem.layout.linear_barcode_item import (
    LinearBarcodeLayoutItemMetadata
)


def register_barcode_items():
    """Register barcode items in the app item registry."""
    QgsApplication.layoutItemRegistry().addLayoutItemType(
        QrCodeLayoutItemMetadata()
    )
    QgsApplication.layoutItemRegistry().addLayoutItemType(
        LinearBarcodeLayoutItemMetadata()
    )
