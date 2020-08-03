# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Test suite
Description          : Aggregated plugin tests
Date                 : 03-08-2020
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
import unittest

from .test_qrcode_item import QRCodeItemTests


def run_all():
    """Run all tests."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(QRCodeItemTests))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)