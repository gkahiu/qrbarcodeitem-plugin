# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : LinearBarcodeLayoutItemWidget
Description          : Widget for configuring a LinearBarcodeLayoutItem.
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
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QLabel,
    QVBoxLayout
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import (
    QTextCursor
)
from qgis.gui import (
    QgsCollapsibleGroupBoxBasic,
    QgsLayoutItemBaseWidget,
    QgsLayoutItemPropertiesWidget
)
from qgis.core import (
    QgsLayoutItem
)
from qrbarcodeitem.layout.linear_barcode_item import LINEAR_BARCODE_TYPE
from qrbarcodeitem.layout.abstract_barcode import BarcodeException
from qrbarcodeitem.layout.linear_metadata import (
    LinearBarcodeMetadataRegistry
)
from qrbarcodeitem.gui.code_value_widget import CodeValueWidget
from qrbarcodeitem.gui.metadata_combobox import LinearMetadataCombobox


class LinearBarcodeLayoutItemWidget(QgsLayoutItemBaseWidget): # pylint: disable=too-few-public-methods
    """Widget for configuring a LinearBarcodeLayoutItem."""

    def __init__(self, parent, layout_object):
        super().__init__(parent, layout_object)
        self._barcode_item = layout_object
        self.message_bar = None

        self.setPanelTitle(self.tr('Linear Barcode Properties'))
        self._init_widgets(layout_object)
        self._current_meta = self._barcode_cbo.current_metadata()
        self._update_gui_values()

    def _init_widgets(self, layout_object):
        """Initialize widgets"""
        lbl_title = QLabel()
        lbl_title.setStyleSheet(
            'padding: 2px; font-weight: bold; background-color: '
            'rgb(200, 200, 200);'
        )
        lbl_title.setText(self.tr('Linear Barcode'))
        self._cd_value_widget = CodeValueWidget(self)
        self._cd_value_widget.value_changed.connect(
            self._on_code_value_changed
        )
        value_groupbox = QgsCollapsibleGroupBoxBasic(self.tr('Data'))
        gp_layout = QVBoxLayout()
        gp_layout.setContentsMargins(0, 0, 0, 0)
        gp_layout.addWidget(self._cd_value_widget)
        value_groupbox.setLayout(gp_layout)

        # Barcode properties
        barcode_props_groupbox = QgsCollapsibleGroupBoxBasic(
            self.tr('Properties')
        )
        barcode_props_layout = QGridLayout()

        lbl_barcode_type = QLabel(self.tr('Linear barcode type'))
        self._barcode_cbo = LinearMetadataCombobox()
        self._barcode_cbo.metadata_changed.connect(
            self._on_linear_type_changed
        )
        barcode_props_layout.addWidget(lbl_barcode_type, 0, 0)
        barcode_props_layout.addWidget(self._barcode_cbo, 0, 1)
        self._chk_checksum = QCheckBox(self.tr('Add checksum'))
        self._chk_checksum.stateChanged.connect(
            self._on_add_checksum
        )
        barcode_props_layout.addWidget(self._chk_checksum,1, 0, 1, 2)
        self._chk_render_txt = QCheckBox(self.tr('Render barcode text'))
        self._chk_render_txt.stateChanged.connect(
            self._on_render_text_changed
        )
        barcode_props_layout.addWidget(self._chk_render_txt, 2, 0, 1, 2)
        barcode_props_layout.setColumnStretch(1, 1)

        barcode_props_groupbox.setLayout(barcode_props_layout)

        # Properties widget
        self._prop_widget = QgsLayoutItemPropertiesWidget(self, layout_object)
        self._prop_widget.showBackgroundGroup(False)

        # Add widgets to layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(lbl_title)
        layout.addWidget(barcode_props_groupbox)
        layout.addWidget(value_groupbox)
        layout.addWidget(self._prop_widget)

        # Set layout
        self.setLayout(layout)

    def setDesignerInterface(self, iface):
        """
        Use layout iface to set the message_bar.
        """
        super().setDesignerInterface(iface)
        self.message_bar = iface.messageBar()

    def metadata(self, metadata_id):
        """
        Gets the metadata object that corresponds to the given id.
        :param metadata_id: Metadata id.
        :type metadata_id: str
        :return: Returns the metadata object corresponding to the
        given id.
        :rtype: AbstractLinearBarcodeMetadata
        """
        reg = LinearBarcodeMetadataRegistry.instance()

        return reg.metadata_by_typeid(metadata_id)

    def setNewItem(self, item):
        """
        Set widget properties to sync with item properties.
        """
        if item.type() != LINEAR_BARCODE_TYPE:
            return False

        self._barcode_item = item
        self._prop_widget.setItem(self._barcode_item)
        self._update_gui_values()

        return True

    def _on_linear_type_changed(self, metadata_id):
        """
        Slot raised when the linear barcode type has been changed.
        """
        meta = self.metadata(metadata_id)
        if meta is None:
            return

        self._current_meta = meta
        self._adapt_ui_item_checksum_properties()
        self.set_barcode_data()

    def _adapt_ui_item_checksum_properties(self):
        """
        Update UI and barcode item properties based on the properties of the
        current metadata object.
        """
        if self._current_meta is None:
            return

        if self._current_meta.supports_manual_checksum():
            self._barcode_item.supports_manual_checksum = True
            self._chk_checksum.setEnabled(True)
            # Set check status based on barcode properties
            if self._barcode_item.add_checksum:
                self._chk_checksum.setCheckState(Qt.Checked)
            else:
                self._chk_checksum.setCheckState(Qt.Unchecked)
        else:
            self._barcode_item.supports_manual_checksum = False
            self._chk_checksum.setEnabled(False)
            self._barcode_item.add_checksum = False
            if self._current_meta.is_checksum_automatic():
                self._chk_checksum.setCheckState(Qt.Checked)
            else:
                self._chk_checksum.setCheckState(Qt.Unchecked)

    def _on_add_checksum(self, state):
        """
        Slot raised to add checksum to the barcode data.
        """
        add_checksum = False
        if state == Qt.Checked:
            add_checksum = True

        self._barcode_item.beginCommand(
            self.tr('Change add checksum'),
            QgsLayoutItem.UndoCustomCommand
        )
        self._barcode_item.blockSignals(True)
        self._barcode_item.add_checksum = add_checksum
        self._barcode_item.blockSignals(False)
        self._barcode_item.endCommand()

    def _on_code_value_changed(self, value):
        """
        Slot raised when the barcode value changes.
        """
        self.set_barcode_data()

    def set_barcode_data(self):
        """
        Assert if characters (computed from the expression) are valid. If
        not, remove invalid characters then check if the maximum number of
        characters are within the maximum set for the given linear barcode
        type.
        """
        # Flag for the validity of barcode data
        is_invalid = False
        if self._current_meta is None:
            return

        user_value = self._cd_value_widget.code_value
        cd_val = self._barcode_item.evaluate_expression(user_value)

        if not cd_val:
            return

        # Check valid characters
        valid_chars = []
        for ch in cd_val:
            if self._current_meta.is_character_allowed(ch):
                valid_chars.append(ch)

        sanitized_txt = ''.join(valid_chars)

        # Notify user if there were invalid chars
        if len(sanitized_txt) != len(cd_val):
            self.add_warning_message(
                self.tr('Barcode data contains invalid characters.')
            )
            is_invalid = True

        cd_val = sanitized_txt
        # Check max length
        max_length = self._current_meta.max_input_length()
        if max_length != -1 and len(cd_val) > max_length:
            self.add_warning_message(
                self.tr(
                    'Barcode data cannot exceed the maximum length of '
                    '{0} characters for {1} linear barcode type.'.format(
                        max_length,
                        self._current_meta.display_name()
                    )
                )
            )
            is_invalid = True

        # Highlight barcode data based on validity of the input
        self._cd_value_widget.highlight_invalid_data(is_invalid)

        if is_invalid: # pylint: disable=no-else-return
            return
        else:
            # Remove any warning items if still visible
            # Check if message_bar has already been initialized
            if self.message_bar is not None:
                self.message_bar.clearWidgets()

        # Set barcode value
        self._barcode_item.beginCommand(
            self.tr('Change code value'),
            QgsLayoutItem.UndoLabelText
        )
        self._barcode_item.blockSignals(True)
        try:
            self._barcode_item.barcode_type = self._current_meta.type_id()
            self._barcode_item.code_value = user_value
        except BarcodeException as bc_ex:
            self.add_warning_message(str(bc_ex))
            is_invalid = True
        self._barcode_item.blockSignals(False)
        self._barcode_item.endCommand()

    def _on_render_text_changed(self, state):
        """
        Slot raised when render_text has been checked/unchecked.
        """
        render_text = False
        if state == Qt.Checked:
            render_text = True

        self._barcode_item.beginCommand(
            self.tr('Change render text'),
            QgsLayoutItem.UndoCustomCommand
        )
        self._barcode_item.blockSignals(True)
        self._barcode_item.render_text = render_text
        self._barcode_item.blockSignals(False)
        self._barcode_item.endCommand()

    def _update_gui_values(self):
        """
        Update gui items based on the item properties.
        """
        self._current_meta = self.metadata(self._barcode_item.barcode_type)

        # Barcode type in combobox
        self._barcode_cbo.blockSignals(True)
        self._barcode_cbo.set_current_metadata(
            self._barcode_item.barcode_type
        )
        self._barcode_cbo.blockSignals(False)

        # Checksum property
        self._adapt_ui_item_checksum_properties()

        # Render text property
        self._chk_render_txt.blockSignals(True)
        if self._barcode_item.render_text:
            self._chk_render_txt.setCheckState(Qt.Checked)
        else:
            self._chk_render_txt.setCheckState(Qt.Unchecked)
        self._chk_render_txt.blockSignals(False)

        # Barcode value (which could also be an expression)
        self._cd_value_widget.block_value_widget_signals(True)
        self._cd_value_widget.code_value = self._barcode_item.code_value
        self._cd_value_widget.value_text_edit.moveCursor(
            QTextCursor.End,
            QTextCursor.MoveAnchor
        )
        self._cd_value_widget.block_value_widget_signals(False)

        # Now set barcode data
        self.set_barcode_data()

    def add_warning_message(self, msg):
        """
        Add warning message to the layout interface.
        :param msg: Warning message.
        :type msg: str
        """
        self.message_bar.pushWarning(
            self.tr('Linear Barcode'),
            msg
        )
