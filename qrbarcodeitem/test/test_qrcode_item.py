# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Test QRCode item
Description          : Unit tests for the QRCode item
Date                 : 03-08-2020
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
import unittest

from qgis.core import (
    QgsApplication,
    QgsReadWriteContext
)
from qgis.PyQt.QtXml import (
    QDomDocument
)

from qrbarcodeitem.layout.qrcode_item import (
    QR_CODE_TYPE,
    QrCodeLayoutItem
)
from qrbarcodeitem.layout.registry import register_barcode_items
from qrbarcodeitem.test.utilities import (
    create_layout
)

# QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class QRCodeItemTests(unittest.TestCase):
    """Test QRCode item"""

    def __init__(self, *args, **kwargs):
        super(QRCodeItemTests, self).__init__(*args, **kwargs)
        self._item_registry = QgsApplication.layoutItemRegistry()

    def setUp(self) -> None:
        """Register items in app registry."""
        register_barcode_items()

    def test_item_registered(self):
        """Test QR item exist in the registry."""
        items = self._item_registry.itemTypes()
        self.assertIn(QR_CODE_TYPE, items)

    def test_item_properties(self):
        """Test default values of custom item properties."""
        layout = create_layout('Test QR Code Item Properties')
        item = QrCodeLayoutItem(layout)

        # Assert item properties
        self.assertFalse(item.is_micro)
        self.assertEqual(item.bg_color, '#FFFFFF')
        self.assertEqual(item.data_color, '#000000')

    def test_read_write(self):
        """Test read/write of custom properties from/to XML."""
        doc = QDomDocument('QRCodeProperties')
        el = doc.createElement('Items')
        is_micro = True
        bg_color = '#45EB6E'
        data_color = '#B20EC2'

        layout = create_layout('Test QR Code Item Properties')
        item = QrCodeLayoutItem(layout)
        item.is_micro = is_micro
        item.bg_color = bg_color
        item.data_color = data_color

        # Test write
        status = item.writeXml(el, doc, QgsReadWriteContext())
        self.assertTrue(status)

        # Test read
        self.assertTrue(el.hasChildNodes())
        item_el = el.firstChildElement()
        self.assertFalse(item_el.isNull())
        read_layout = create_layout('Test XML read')
        read_item = QrCodeLayoutItem(read_layout)
        read_status = read_item.readXml(item_el, doc, QgsReadWriteContext())
        self.assertTrue(read_status)
        self.assertEqual(read_item.is_micro, is_micro)
        self.assertEqual(read_item.bg_color, bg_color)
        self.assertEqual(read_item.data_color, data_color)


if __name__ == '__main__':
    unittest.main()
