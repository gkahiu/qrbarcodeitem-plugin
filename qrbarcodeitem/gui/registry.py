# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Item Gui Registry
Description          : Registers GUI metadata for QR and barcode items.
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
from qgis.PyQt.QtCore import QCoreApplication
from qgis.gui import (
    QgsGui,
    QgsLayoutItemAbstractGuiMetadata,
    QgsLayoutItemBaseWidget,
    QgsLayoutItemGuiGroup
)
from qrbarcodeitem.layout.qrcode_item import (
    QR_CODE_TYPE,
    QrCodeLayoutItem
)
from qrbarcodeitem.utils import (
    get_icon
)
from qrbarcodeitem.gui.qrcode_widget import QrCodeLayoutItemWidget

ITEM_CATEGORY = 'qrbarcodeitem'


class QrCodeLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):
    """Stores GUI metadata for a QR code layout item."""
    def __init__(self):
        super().__init__(
            QR_CODE_TYPE,
            QCoreApplication.translate('QrBarCodeLayoutItem', 'QR Code'),
            ITEM_CATEGORY
        )

    def createItemWidget(self, item): # pylint: disable=missing-function-docstring, no-self-use
        return QrCodeLayoutItemWidget(None, item)

    def creationIcon(self): # pylint: disable=missing-function-docstring, no-self-use
        return get_icon('qrcode_plus.svg')


class BarCodeLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):
    """Stores GUI metadata for a barcode layout item."""
    def __init__(self):
        super().__init__(
            234567,
            QCoreApplication.translate(
                'QrBarCodeLayoutItem',
                'Linear Barcode'
            ),
            ITEM_CATEGORY
        )

    def createItemWidget(self, item): # pylint: disable=missing-function-docstring, no-self-use
        return QgsLayoutItemBaseWidget(item)

    def createItem(self, layout): # pylint: disable=missing-function-docstring, no-self-use
        return QrCodeLayoutItem(layout)

    def creationIcon(self): # pylint: disable=missing-function-docstring, no-self-use
        return get_icon('barcode_plus.svg')


def register_items_gui_metadata():
    """Registers GUI metadata for QR and barcode items."""
    item_registry = QgsGui.layoutItemGuiRegistry()

    # Create menu group
    item_registry.addItemGroup(
        QgsLayoutItemGuiGroup(
            ITEM_CATEGORY,
            QCoreApplication.translate('QrBarCodeLayoutItem', 'Barcode Item'),
            get_icon('qr_barcode.svg')
        )
    )

    # Add barcode gui metadata
    barcode_meta = BarCodeLayoutItemGuiMetadata()
    item_registry.addLayoutItemGuiMetadata(barcode_meta)

    # Add QR Code gui metadata
    qr_code_meta = QrCodeLayoutItemGuiMetadata()
    item_registry.addLayoutItemGuiMetadata(qr_code_meta)
