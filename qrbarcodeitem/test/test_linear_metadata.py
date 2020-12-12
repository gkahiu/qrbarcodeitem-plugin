# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Test linear metadata
Description          : Unit tests for the linear metadata registry and items
Date                 : 23-11-2020
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


from qrbarcodeitem.layout.linear_metadata import (
    LinearBarcodeMetadataRegistry,
    register_linear_barcode_metadata
)


class LinearBarcodeMetadataTests(unittest.TestCase):
    """Tests for linear barcode metadata API."""

    def test_metadata_registry(self):
        # Test LinearBarcodeMetadataRegistry
        register_linear_barcode_metadata()
        registry = LinearBarcodeMetadataRegistry.instance()
        self.assertEqual(len(registry), 1)

        # Test search function
        metadata = registry.metadata_by_typeid('code39')
        self.assertIsNotNone(metadata)

        # Test remove function
        status = registry.remove_metadata('code39')
        self.assertTrue(status)

        # Test clear function
        registry.clear()
        self.assertEqual(len(registry), 0)


if __name__ == '__main__':
    suite = unittest.makeSuite(LinearBarcodeMetadataTests)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)