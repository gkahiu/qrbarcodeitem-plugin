# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : BarcodeLayoutChecker
Description          : Compares a code-generated layout with a corresponding
                       control image in the test folder.
Date                 : 29-09-2020
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

from qgis.PyQt.QtCore import (
    QDir,
    QFileInfo,
    QSize
)
from qgis.PyQt.QtGui import (
    QImage,
    QPainter
)
from qgis.core import (
    QgsLayoutExporter,
    QgsMultiRenderChecker
)


class BarcodeLayoutChecker(QgsMultiRenderChecker):
    """Compares image from code-generated layout with one in the test folder.
    Code adapted from QgsLayoutChecker in:
    QGIS/tests/src/python/qgslayoutchecker.py.
    Uses images in the 'control_images' folder in the 'test' folder.
    """

    def __init__(self, test_name, layout, control_path_prefix='barcode'):
        super().__init__()
        self.layout = layout
        self.test_name = test_name
        self.dots_per_metre = 96 / 25.4 * 1000
        self.size = QSize(1122, 794)
        self.setColorTolerance(5)
        self.pixel_diff = 5
        self.control_name = 'expected_{0}'.format(self.test_name)
        self.control_path_prefix = control_path_prefix
        self.setControlPathPrefix(self.control_path_prefix)

    def test_layout(self):
        """Test layout with one in the control image in the test folder."""
        if not self.layout:
            return False, 'Layout not valid'

        # Load expected image
        self.setControlName(self.control_name)

        # Create output image
        output_image = QImage(self.size, QImage.Format_RGB32)
        output_image.setDotsPerMeterX(self.dots_per_metre)
        output_image.setDotsPerMeterY(self.dots_per_metre)
        QgsMultiRenderChecker.drawBackground(output_image)

        # Draw layout to image
        p = QPainter(output_image)
        exporter = QgsLayoutExporter(self.layout)
        # Render first page in layout
        exporter.renderPage(p, 0)
        p.end()

        image_path = '{0}{1}{2}.png'.format(
            QDir.tempPath(),
            QDir.separator(),
            QFileInfo(self.test_name).baseName()
        )
        output_image.save(image_path, 'PNG')
        self.setRenderedImage(image_path)

        test_result = self.runTest(self.test_name, self.pixel_diff)

        return test_result, self.report()
