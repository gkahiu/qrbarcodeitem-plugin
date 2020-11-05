# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Test suite
Description          : Aggregated plugin tests
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
import sys

from qrbarcodeitem.test.test_qrcode_item import QRCodeItemTests
from qrbarcodeitem.test.test_linear_barcode_item import LinearBarcodeItemTests


def run_all():
    """Run all tests."""
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(QRCodeItemTests))
    suite.addTests(unittest.makeSuite(LinearBarcodeItemTests))

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    runner.run(suite)


if __name__ == '__main__':
    run_all()