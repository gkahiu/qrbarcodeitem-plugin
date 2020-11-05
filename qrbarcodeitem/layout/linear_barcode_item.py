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

LINEAR_BARCODE_TYPE = QgsLayoutItemRegistry.PluginItem + 2345


class LinearBarcodeLayoutItem(AbstractBarcodeLayoutItem):
    """Item for rendering a linear barcode."""

    _ATTR_BG_COLOR = 'codeBackgroundColor'
    _ATTR_DATA_COLOR = 'dataColor'
    _ATTR_BARCODE_TYPE = 'linearBarcodeType'
    _DEF_BG_COLOR = '#FFFFFF'
    _DEF_DATA_COLOR = '#000000'
    DEF_BARCODE_TYPE = 'code128'

    def __init__(self, *args):
        super().__init__(*args)
        self._barcode_type = self.DEF_BARCODE_TYPE

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

    def icon(self): # pylint: disable=no-self-use
        """Return item's icon."""
        return get_icon('barcode.svg')

    def _gen_image(self, file_path):
        """Generate QR Code based on the computed value."""
        try:
            linear_barcode = barcode.get(
                self._barcode_type,
                self.computed_value()
            )
            linear_barcode.save(file_path)
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

        return True

    def _read_props_from_el(self, el, document, context):
        """Reads item attributes."""
        self._barcode_type = str(
            el.attribute(self._ATTR_BARCODE_TYPE, self._DEF_BARCODE_TYPE)
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
