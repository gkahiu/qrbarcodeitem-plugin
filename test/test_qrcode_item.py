# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Test QRCode item
Description          : Unit tests for the QRCode item
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


class QRCodeItemTests(unittest.TestCase):
    """Test QRCode item"""

    def test_name(self):
        self.assertEqual('QRCode', 'QRCode')


if __name__ == '__main__':
    unittest.main()