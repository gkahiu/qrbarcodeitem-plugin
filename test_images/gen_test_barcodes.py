# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : gen_test_barcodes
Description          : Util script for generating barcodes for unit tests.
Date                 : 19-11-2020
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
import os

from qrbarcodeitem.extlibs import barcode


TEST_IMAGE_DIR = '{0}/test_barcodes'.format(os.path.dirname(__file__))


writer_options = {
    'quiet_zone': 1.5,
    'background': '#FFFFFF',
    'foreground': '#000000',
    'write_text': False
}


def create_code39():
    """
    Create test linear barcode for 'code39' type.
    """
    _create_linear_barcode('code39', 'ABCD-123456')


def _create_linear_barcode(type_id, value):
    """
    Create and save supported linear barcode based on the given barcode value.
    """
    abs_file_path = os.path.normpath(
        '{0}/{1}'.format(TEST_IMAGE_DIR, type_id)
    )
    linear_barcode = barcode.get(type_id, value)
    linear_barcode.save(abs_file_path, writer_options)


def create_all():
    """
    Create all supported barcode images.
    """
    create_code39()


if __name__ == '__main__':
    create_all()

