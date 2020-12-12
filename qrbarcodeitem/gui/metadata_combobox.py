# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : LinearMetadataCombobox
Description          : Combobox for selecting the type of linear barcode
                       metadata object.
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
from qgis.PyQt.QtWidgets import QComboBox
from qgis.PyQt.QtCore import pyqtSignal

from qrbarcodeitem.layout.linear_metadata import (
    AbstractLinearBarcodeMetadata,
    LinearBarcodeMetadataRegistry
)


class LinearMetadataCombobox(QComboBox):
    """
    Combobox for selecting the type of linear barcode metadata object.
    """
    metadata_changed = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Stores the item index based on the metadata id i.e. [meta_id] = idx
        self._meta_idx = {}
        self._populate_metadata_items()
        self.currentIndexChanged.connect(
            self._on_index_changed
        )

    def _populate_metadata_items(self):
        # Add metadata objects to the list of combobox items.
        meta_items = LinearBarcodeMetadataRegistry.instance().items()
        for i, meta in enumerate(meta_items):
            self.insertItem(i, meta.display_name(), meta)
            self._meta_idx[meta.type_id()] = i

    def _on_index_changed(self, idx):
        """
        Slot raised when current index has changed. This raised a custom
        signal containing the metadata_id.
        """
        self.metadata_changed.emit(self.current_typeid())

    def current_metadata(self):
        """
        :return: Returns the current metadata object or None if there is
        no user selection.
        :rtype: AbstractLinearBarcodeMetadata
        """
        return self.itemData(self.currentIndex())

    def current_typeid(self):
        """
        :return: Returns the linear barcode typeid of the current items or
        an empty string if there is no user selection.
        :rtype: str
        """
        meta = self.current_metadata()
        if meta is None:
            return ''

        return meta.type_id()

    def metadata_index(self, metadata_id):
        """
        Gets the index of the metadata object with given id.
        :param metadata_id: Metadata id
        :type metadata_id: str
        :return: Returns the index (in the combobox) of the metadata item,
        else -1 if not found.
        :rtype: int
        """
        return self._meta_idx.get(metadata_id, -1)

    def set_current_metadata(self, metadata):
        """
        Sets the current linear barcode metadata item.
        :param metadata: Id of the metadata item or metadata object.
        :type metadata: str or AbstractLinearBarcodeMetadata
        :return: Returns True if the operation succeeded, else False if
        the id does not exist in the metadata registry.
        :rtype: bool
        """
        if isinstance(metadata, AbstractLinearBarcodeMetadata):
            metadata = metadata.type_id()

        reg = LinearBarcodeMetadataRegistry.instance()
        status = reg.has_metadata_id(metadata)
        if not status:
            return False

        idx = self.metadata_index(metadata)
        self.setCurrentIndex(idx)

        return True
