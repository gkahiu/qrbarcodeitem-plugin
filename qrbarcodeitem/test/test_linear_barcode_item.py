# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Test Linear Barcode item
Description          : Unit tests for the linear barcode item
Date                 : 05-11-2020
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

from qrbarcodeitem.layout.linear_barcode_item import (
    LINEAR_BARCODE_TYPE,
    LinearBarcodeLayoutItem
)
from qrbarcodeitem.layout.registry import register_barcode_items
from qrbarcodeitem.test.utilities import (
    create_layout
)


class LinearBarcodeItemTests(unittest.TestCase):
    """Test linear barcode item."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._item_registry = QgsApplication.layoutItemRegistry()

    def setUp(self) -> None:
        """Register items in app registry."""
        register_barcode_items()

    def test_item_registered(self):
        """Test linear barcode item exist in the registry."""
        items = self._item_registry.itemTypes()
        self.assertIn(LINEAR_BARCODE_TYPE, items)

    def test_item_properties(self):
        """Test default values of custom item properties."""
        layout = create_layout('Test Linear barcode Item Properties')
        item = LinearBarcodeLayoutItem(layout)

        # Assert default item properties
        self.assertEqual(
            item.barcode_type,
            LinearBarcodeLayoutItem.DEF_BARCODE_TYPE
        )

    def test_read_write(self):
        """Test read/write of custom properties from/to XML."""
        doc = QDomDocument('LinearBarcodeProperties')
        el = doc.createElement('Items')
        barcode_type = 'ean13'

        layout = create_layout('Test Linear Barcode Item Properties')
        item = LinearBarcodeLayoutItem(layout)
        item.barcode_type = barcode_type

        # Test write
        status = item.writeXml(el, doc, QgsReadWriteContext())
        self.assertTrue(status)

        # Test read
        self.assertTrue(el.hasChildNodes())
        item_el = el.firstChildElement()
        self.assertFalse(item_el.isNull())
        read_layout = create_layout('Test XML read')
        read_item = LinearBarcodeLayoutItem(read_layout)
        read_status = read_item.readXml(item_el, doc, QgsReadWriteContext())
        self.assertTrue(read_status)

