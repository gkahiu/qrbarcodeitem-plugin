# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : AbstractLayoutItemBarcode
Description          : Abstract implementation of barcode layout
Date                 : 04-08-2020
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
from qgis.PyQt.QtCore import (
    QCoreApplication,
    QPointF,
    QRect,
    QStandardPaths,
    QSize,
    QTemporaryFile,
    Qt,
    QUuid
)
from qgis.PyQt.QtGui import (
    QFont,
    QPainter
)
from qgis.PyQt.QtSvg import QSvgGenerator
from qgis.core import (
    Qgis,
    QgsExpression,
    QgsLayoutItemPicture,
    QgsMessageLog
)


class BarcodeException(Exception):
    """Exception when generating barcode images."""
    pass


class AbstractBarcodeLayoutItem(QgsLayoutItemPicture):
    """Base class for barcode layout."""

    def __init__(self, layout):
        super().__init__(layout)
        self._code_value = ''
        self._temp_dir = '{0}/qrbarbarcode'.format(
            QStandardPaths.standardLocations(QStandardPaths.TempLocation)
        )

        # Set picture properties
        self.setResizeMode(QgsLayoutItemPicture.Zoom)

    @property
    def temp_image_dir(self):
        """
        :return: Returns the temp dir where the generated SVG files will be
        saved.
        :rtype: str
        """
        return self._temp_dir

    @property
    def code_value(self):
        """
        :return: Returns the absolute value as specified by the user, may
        include the expression text if specified.
        :rtype
        """
        return self._code_value

    @code_value.setter
    def code_value(self, value):
        """
        Sets the code value and generates the corresponding barcode.
        :param value: Absolute value or expression text.
        :type value: str
        """
        if value == self._code_value:
            return

        self.generate_code()

    def _gen_svg_path(self):
        """Generate a file path in temp folder."""
        return '{0}/{1}.svg'.format(
            self._temp_dir,
            QUuid.createUuid().toString()
        )

    def computed_value(self):
        """
        :return: Returns a value based on an evaluation of the code_value
        using the current expression context.
        :rtype: str
        """
        exp_ctx = self.createExpressionContext()

        return QgsExpression.replaceExpressionText(
            self._code_value,
            exp_ctx
        )

    def update_item(self):
        """
        Generates the barcode and refreshes the item if data has been
        specified.
        """
        if self.computed_value():
            self.generate_code()

    def refreshPicture(self, exp_ctx=None): # pylint: disable=unused-argument
        """Override default behaviour for refreshing the item."""
        self.update_item()

    def generate_code(self):
        """
        Generates the barcode image and sets the image in the picture item.
        :return: Returns True if the code was successfully generated, else
        False.
        :rtype: bool
        """
        status = False
        if not self.computed_value():
            return status

        svg_file = QTemporaryFile('qrbarcode_temp.XXXXXX')
        try:
            if svg_file.open():
                svg_path = '{0}.svg'.format(svg_file.fileName())
                self._gen_image(svg_path)
                self.setPicturePath(svg_path)
                status = True
        except BarcodeException as bc_ex:
            # Set error image
            self.set_error_image()
            QgsMessageLog.logMessage(
                repr(bc_ex),
                'QRBarcodeItem',
                level=Qgis.Critical
            )
        finally:
            svg_file.close()

        return status

    def _gen_image(self, file_path):
        """
        Generate barcode image and save in the temp dir. To be implemented
        by subclasses.
        :param file_path: File path to be used for generating the temp SVG.
        :type file_path: str
        """
        raise NotImplementedError

    def writePropertiesToElement(self, el, document, context):
        """Override saving of item properties."""
        status = super().writePropertiesToElement(el, document, context)
        if status:
            self._write_base_properties_to_el(el)
            status = self._write_props_to_el(el, document, context)

        return status

    def _write_base_properties_to_el(self, el):
        """Write base properties to DOM element."""
        el.setAttribute('codeValue', self._code_value)

    def _write_props_to_el(self, el, document, context):
        """
        Write custom properties for implementation by subclass, should
        return True or False.
        """
        raise NotImplementedError

    # def readPropertiesFromElement(self, element, document, context):
    #     """Override reading of item properties."""
    #     status = super().readPropertiesFromElement(element, document, context)
    #
    #     if status:
    #         self._code_value = element.attribute('codeValue')
    #         status = self._read_props_from_el(element, document, context)
    #
    #     return status

    def _read_props_from_el(self, el, document, context):
        """Read properties from subclass. Should return True of False."""
        raise NotImplementedError

    def set_error_image(self):
        """
        Insert 'Error!' text in the item to indicate an error occurred during
        the process of generating the code.
        """
        error_txt = QCoreApplication.translate(
            'QrBarCodeLayoutItem',
            'Error!'
        )
        self.set_text_image(error_txt, Qt.red)

    def set_text_image(self, text, color=Qt.gray):
        """
        Set the item picture based on an SVG file created from the given text.
        :param text: Text to be rendered as SVG.
        :type text: str
        :param color: Font color
        :type color: QColor
        """
        w, h = 200, 50
        svg_path = self._gen_svg_path()
        svg_gen = QSvgGenerator()
        svg_gen.setFileName(svg_path)
        svg_gen.setTitle('QrBarCodeLayoutItem')
        svg_gen.setDescription(
            'Image generated by QrBarCodeLayoutItem plugin'
        )
        svg_gen.setSize(QSize(w, h))
        svg_gen.setViewBox(QRect(0, 0, w, h))

        # Paint text
        font = QFont('Arial', 14, QFont.Bold)
        p = QPainter()
        p.begin(svg_gen)
        p.setFont(font)
        p.setPen(color)
        p.drawText(QPointF(10, 20), text)
        p.end()

        # Set picture path
        self.setPicturePath(svg_path)
