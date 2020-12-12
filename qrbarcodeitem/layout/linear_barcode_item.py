# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : LayoutItemLinearBarcode
Description          : Linear barcode item for use in QGIS print layout
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
from qgis.PyQt.QtCore import (
    QCoreApplication
)
from qgis.core import (
    QgsLayoutItemAbstractMetadata,
    QgsLayoutItemRegistry
)

from qrbarcodeitem.extlibs import barcode
from qrbarcodeitem.extlibs.barcode.errors import BarcodeError
from qrbarcodeitem.layout.abstract_barcode import (
    AbstractBarcodeLayoutItem,
    BarcodeException
)
from qrbarcodeitem.utils import (
    get_icon
)

LINEAR_BARCODE_TYPE = QgsLayoutItemRegistry.PluginItem + 2346


class LinearBarcodeLayoutItem(AbstractBarcodeLayoutItem):
    """Item for rendering a linear barcode."""

    _ATTR_BG_COLOR = 'backColor'
    _ATTR_FG_COLOR = 'foreColor'
    _ATTR_BARCODE_TYPE = 'linearBarcodeType'
    _ATTR_INCLUDE_TEXT = 'renderText'
    _ATTR_CHECKSUM = 'addChecksum'
    _ATTR_MANUAL_CHECKSUM = 'manualChecksum'
    _DEF_BG_COLOR = '#FFFFFF'
    _DEF_FG_COLOR = '#000000'
    _DEF_BARCODE_TYPE = 'code39'

    def __init__(self, *args):
        super().__init__(*args)
        self._barcode_type = self._DEF_BARCODE_TYPE
        self._background_color = self._DEF_BG_COLOR
        self._foreground_color = self._DEF_FG_COLOR
        self._add_checksum = False
        self._supports_manual_checksum = False
        self._render_text = True

    @property
    def barcode_type(self):
        """
        :return: Returns the unique type identifier of the linear barcode.
        :rtype: str
        """
        return self._barcode_type

    @barcode_type.setter
    def barcode_type(self, type_id):
        """
        Sets the linear barcode type identifier as supported by the
        'python-barcode' library.
        :param type_id: Unique type identifier of the linear barcode.
        :type type_id: str
        """
        if self._barcode_type != type_id:
            self._barcode_type = type_id
            self.update_item()

    @property
    def add_checksum(self):
        """
        :return: Returns True if a checksum value should be included in the
        barcode data, else False. This only applies to those linear barcode
        types that support a checksum.
        :rtype: bool
        """
        return self._add_checksum

    @add_checksum.setter
    def add_checksum(self, status):
        """
        Set True to add checksum value in the barcode data, else False. This
        only applies to those linear barcode
        types that support a checksum.
        :param status: Flag to add a checksum value, if supported for the
        given linear barcode type.
        :type status: bool
        """
        if self._add_checksum != status:
            self._add_checksum = status
            self.update_item()

    @property
    def supports_manual_checksum(self):
        """
        :return: Returns True if the given linear barcode type supports the
        inclusion of a checksum.
        :rtype: bool
        """
        return self._supports_manual_checksum

    @supports_manual_checksum.setter
    def supports_manual_checksum(self, status):
        """
        Specify whether a given linear barcode type supports the inclusion
        of a checksum. This is not defined in the UI but rather by the
        metadata definition for each supported linear barcode type.
        :param status: Flag to indicate whether the given barcode type
        supports a checksum.
        :type status: bool
        """
        if self._supports_manual_checksum != status:
            self._supports_manual_checksum = status

    @property
    def render_text(self):
        """
        :return: Returns True if text should be rendered below the barcode
        modules.
        :rtype: bool
        """
        return self._render_text

    @render_text.setter
    def render_text(self, render):
        """
        Set if the barcode text should be drawn below the barcode modules.
        :param render: True to render, False to exclude barcode text.
        :type render: bool
        """
        if self._render_text != render:
            self._render_text = render
            self.update_item()

    def barcode_gen_options(self):
        """
        :return: Returns the custom options for generating the linear barcode.
        :rtype: dict
        """
        opts = {}

        # For checksum
        if self._supports_manual_checksum:
            opts['add_checksum'] = self._add_checksum

        return opts

    def icon(self): # pylint: disable=no-self-use
        """Return item's icon."""
        return get_icon('barcode.svg')

    def _gen_image(self, file_path):
        """Generate QR Code based on the computed value."""
        # Options for the barcode SVG writer
        writer_options = {
            'quiet_zone': 1.5,
            'font_size': 4,
            'background': self._background_color,
            'foreground': self._foreground_color,
            'write_text': self._render_text
        }
        build_opts = self.barcode_gen_options()

        try:
            linear_barcode = barcode.get(
                self._barcode_type,
                self.computed_value(),
                options=build_opts
            )

            # barcode lib automatically add '.svg' suffix
            linear_barcode.save(
                file_path.replace('.svg', ''),
                writer_options
            )
        except BarcodeError as bce:
            raise BarcodeException(
                str(bce)
            ) from bce

    def type(self): # pylint: disable=no-self-use
        """Return item's unique type identifier."""
        return LINEAR_BARCODE_TYPE

    def _write_props_to_el(self, el, document, context):
        """Write attributes to document."""
        el.setAttribute(
            self._ATTR_BARCODE_TYPE, str(self._barcode_type)
        )
        el.setAttribute(self._ATTR_FG_COLOR, str(self._foreground_color))
        el.setAttribute(self._ATTR_BG_COLOR, str(self._background_color))
        el.setAttribute(self._ATTR_INCLUDE_TEXT, str(self._render_text))
        el.setAttribute(self._ATTR_CHECKSUM, str(self._add_checksum))
        el.setAttribute(
            self._ATTR_MANUAL_CHECKSUM,
            str(self._supports_manual_checksum)
        )

        return True

    def _read_props_from_el(self, el, document, context):
        """Reads item attributes."""
        self._barcode_type = str(
            el.attribute(self._ATTR_BARCODE_TYPE, self._DEF_BARCODE_TYPE)
        )
        self._background_color = str(
            el.attribute(self._ATTR_BG_COLOR, self._DEF_BG_COLOR)
        )
        self._foreground_color = str(
            el.attribute(self._ATTR_FG_COLOR, self._DEF_FG_COLOR)
        )
        self._render_text = self._str_to_bool(
            el.attribute(self._ATTR_INCLUDE_TEXT, 'True')
        )
        self._add_checksum = self._str_to_bool(
            el.attribute(self._ATTR_CHECKSUM, 'False')
        )
        self._supports_manual_checksum = self._str_to_bool(
            el.attribute(self._ATTR_MANUAL_CHECKSUM, 'False')
        )
        self.update_item()

        return True


# pylint: disable=too-few-public-methods
class LinearBarcodeLayoutItemMetadata(QgsLayoutItemAbstractMetadata):
    """Metadata info of the linear barcode item."""
    def __init__(self):
        super().__init__(
            LINEAR_BARCODE_TYPE,
            QCoreApplication.translate(
                'QrBarCodeLayoutItem', 'Linear Barcode'
            )
        )

    def createItem(self, layout): # pylint: disable=no-self-use
        """Factory method that return the QR Code Item."""
        return LinearBarcodeLayoutItem(layout)
