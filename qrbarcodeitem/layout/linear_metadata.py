# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : LinearBarcodeMetadata
Description          : Metadata items for linear barcode types.
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
from abc import ABC
from collections import OrderedDict
from qgis.PyQt.QtCore import QCoreApplication

from qrbarcodeitem.extlibs.barcode.charsets.code39 import REF as c39_chars
from qrbarcodeitem.extlibs.barcode.charsets.code128 import ALL as c128_chars
from qrbarcodeitem.utils import Singleton


class AbstractLinearBarcodeMetadata(ABC):
    """
    Abstract class that provides a standard interface for defining the
    properties of different linear barcode types.
    """
    def display_name(self):
        """
        :return: Returns a friendly name of the linear barcode type.
        :rtype: str
        """
        raise NotImplementedError

    def type_id(self):
        """
        :return: Return the code of the specific barcode type as defined in
        the 'barcode' library.
        :rtype: str
        """
        raise NotImplementedError

    def supports_manual_checksum(self):
        """
        :return: Return True if the given type allows a user to manually
        add/remove the checksum, else False.
        :rtype: bool
        """
        raise False

    def is_checksum_automatic(self):
        """
        :return: Return True if the given barcode type has its checksum
        automatically calculated and included in the barcode. This is only
        applicable if 'supports_checksum' is True.
        :rtype: bool
        """
        raise False

    def max_input_length(self):
        """
        :return: Returns the maximum number of characters allowed for the
        given barcode type. -1 if there is no limit.
        :rtype: int
        """
        return -1

    def is_character_allowed(self, data_char): # pylint: disable=no-self-use
        """
        Evaluates if the given character is allowed.
        :param data_char: Character to evaluate if allowed.
        :type data_char: str
        :return: True if the character is allowed by the linear barcode type,
        else False.
        :rtype: bool
        """
        return True


def tr(text):
    """
    Get the translation for a string using Qt translation API.
    :param text: Text to translate.
    :type text: str
    :return: Returns the translated version of the input text.
    :rtype: str
    """
    return QCoreApplication.translate('LinearBarcodeMetadata', text)


@Singleton
class LinearBarcodeMetadataRegistry:
    """
    Collection of linear barcode metadata objects.
    """

    def __init__(self):
        self._metadata = OrderedDict()

    def register_metadata(self, metadata):
        """
        Adds a metadata object to the collection.
        :param metadata: Linear barcode metadata object.
        :type metadata: AbstractLinearBarcodeMetadata
        :return: Returns True if the metadata object was successfully added,
        else False.
        :rtype: bool
        """
        if not isinstance(metadata, AbstractLinearBarcodeMetadata):
            return False

        self._metadata[metadata.type_id()] = metadata

        return True

    def registered_types(self):
        """
        :return: Returns a list of the registered metadata type_ids.
        :rtype: list
        """
        return self._metadata.keys()

    def items(self):
        """
        :return: Returns a list of metadata objects in the collection.
        :rtype: list
        """
        return self._metadata.values()

    def metadata_by_typeid(self, type_id):
        """
        Gets the metadata object corresponding to the given type_id, else
        None if not found.
        :param type_id: Type_id of the metadata object
        :type type_id: str
        :return: Returns the metadata object corresponding to the given
        type_id or None if it does not exist.
        :rtype: AbstractLinearBarcodeMetadata
        """
        return self._metadata.get(type_id, None)

    def has_metadata_id(self, type_id):
        """
        Checks if a metadata item with the given id exists in the registry.
        :param type_id: Unique identifier of the metadata object.
        :type type_id: str
        :return: Returns True if it exists, else False.
        :rtype: bool
        """
        return bool(self.metadata_by_typeid(type_id))

    def clear(self):
        """Removes all metadata objects in the collection."""
        self._metadata.clear()

    def remove_metadata(self, type_id):
        """
        Removes the metadata object with the given type_id.
        :param type_id: Type_id of the metadata object to be removed.
        :type type_id: str
        :return: Returns True if the metadata object was successfully removed,
        else False.
        """
        if type_id in self._metadata:
            del self._metadata[type_id]
            return True

        return False

    def __len__(self):
        """
        :return: Returns number of metadata items in the collection.
        :rtype: int
        """
        return len(self._metadata)


class Code39Metadata(AbstractLinearBarcodeMetadata):
    """Metadata for 'code39' linear barcode type."""

    def display_name(self):
        # Friendly display name.
        return tr('Code 39')

    def type_id(self):
        # Type identifier.
        return 'code39'

    def supports_manual_checksum(self):
        return True

    def is_checksum_automatic(self):
        # Has option of being excluded in the user input.
        return False

    def max_input_length(self):
        return -1

    def is_character_allowed(self, data_char):
        # Check from collection defined in barcode lib.
        if data_char not in c39_chars:
            return False

        return True


class Code128Metadata(AbstractLinearBarcodeMetadata):
    """Metadata for 'code128' linear barcode type."""

    def display_name(self):
        # Friendly display name.
        return tr('Code 128')

    def type_id(self):
        # Type identifier.
        return 'code128'

    def supports_manual_checksum(self):
        return False

    def is_checksum_automatic(self):
        return True

    def max_input_length(self):
        return -1

    def is_character_allowed(self, data_char):
        # Check from collection defined in barcode lib.
        if data_char not in c128_chars:
            return False

        return True


def register_linear_barcode_metadata():
    """
    Register core metadata items.
    """
    meta_registry = LinearBarcodeMetadataRegistry.instance()
    meta_registry.register_metadata(Code39Metadata())
    meta_registry.register_metadata(Code128Metadata())
