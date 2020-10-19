# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : QrCodeLayoutItemWidget
Description          : Widget for configuring a QrCodeLayoutItem.
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
from qgis.PyQt.QtWidgets import (
    QGridLayout,
    QLabel,
    QVBoxLayout
)
from qgis.PyQt.QtGui import (
    QTextCursor
)
from qgis.gui import (
    QgsCollapsibleGroupBoxBasic,
    QgsColorButton,
    QgsLayoutItemBaseWidget,
    QgsLayoutItemPropertiesWidget
)
from qgis.core import (
    QgsLayoutItem
)
from qrbarcodeitem.layout.qrcode_item import QR_CODE_TYPE
from qrbarcodeitem.gui.code_value_widget import CodeValueWidget
from qrbarcodeitem.utils import color_from_name


class QrCodeLayoutItemWidget(QgsLayoutItemBaseWidget): # pylint: disable=too-few-public-methods
    """Widget for configuring a QrCodeLayoutItem."""
    def __init__(self, parent, layout_object):
        super().__init__(parent, layout_object)
        self._qrcode_item = layout_object
        self.message_bar = None

        self.setPanelTitle(self.tr('QR Code Properties'))
        self._init_widgets(layout_object)
        self._update_gui_values()

    def _init_widgets(self, layout_object):
        """Initialize widgets"""
        lbl_title = QLabel()
        lbl_title.setStyleSheet(
            'padding: 2px; font-weight: bold; background-color: '
            'rgb(200, 200, 200);'
        )
        lbl_title.setText(self.tr('QR Code'))
        self._cd_value_widget = CodeValueWidget(self)
        self._cd_value_widget.value_changed.connect(
            self._on_code_value_changed
        )
        value_groupbox = QgsCollapsibleGroupBoxBasic(self.tr('Item Value'))
        gp_layout = QVBoxLayout()
        gp_layout.setContentsMargins(0, 0, 0, 0)
        gp_layout.addWidget(self._cd_value_widget)
        value_groupbox.setLayout(gp_layout)

        # Item appearance
        appearance_groupbox = QgsCollapsibleGroupBoxBasic(
            self.tr('Appearance')
        )
        appearance_layout = QGridLayout()

        # Data color
        lbl_data_clr = QLabel(self.tr('Data color'))
        self._data_clr_btn = QgsColorButton()
        self._data_clr_btn.setColorDialogTitle(self.tr('Select Data Color'))
        self._data_clr_btn.setContext('composer')
        self._data_clr_btn.setAllowOpacity(False)
        self._data_clr_btn.colorChanged.connect(self.on_data_color_changed)
        appearance_layout.addWidget(lbl_data_clr, 0, 0)
        appearance_layout.addWidget(self._data_clr_btn, 0, 1)
        appearance_layout.setColumnStretch(2, 1)

        # Background color
        lbl_background_clr = QLabel(self.tr('Background color'))
        self._background_clr_btn = QgsColorButton()
        self._background_clr_btn.setColorDialogTitle(
            self.tr('Select Background Color')
        )
        self._background_clr_btn.setContext('composer')
        self._background_clr_btn.setAllowOpacity(False)
        self._background_clr_btn.colorChanged.connect(
            self.on_background_color_changed
        )
        appearance_layout.addWidget(lbl_background_clr, 1, 0)
        appearance_layout.addWidget(self._background_clr_btn, 1, 1)

        appearance_groupbox.setLayout(appearance_layout)

        # Properties widget
        self._prop_widget = QgsLayoutItemPropertiesWidget(self, layout_object)
        self._prop_widget.showBackgroundGroup(False)

        # Add widgets to layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(lbl_title)
        layout.addWidget(value_groupbox)
        layout.addWidget(appearance_groupbox)
        layout.addWidget(self._prop_widget)

        # Set layout
        self.setLayout(layout)

    def _on_code_value_changed(self, txt):
        # Slot raised when the code value changes.
        self._qrcode_item.beginCommand(
            self.tr('Change code value'),
            QgsLayoutItem.UndoLabelText
        )
        self._qrcode_item.blockSignals(True)
        self._qrcode_item.code_value = txt
        self._qrcode_item.blockSignals(False)
        self._qrcode_item.endCommand()

    def setNewItem(self, item):
        """
        Set widget properties to sync with item properties.
        """
        if item.type() != QR_CODE_TYPE:
            return False

        self._qrcode_item = item
        self._prop_widget.setItem(self._qrcode_item)
        self._update_gui_values()

        return True

    def _update_gui_values(self):
        # Updates values of widgets based on item properties.
        self._cd_value_widget.block_value_widget_signals(True)
        self._cd_value_widget.code_value = self._qrcode_item.code_value
        self._cd_value_widget.value_text_edit.moveCursor(
            QTextCursor.End,
            QTextCursor.MoveAnchor
        )
        self._cd_value_widget.block_value_widget_signals(False)

        self._data_clr_btn.blockSignals(True)
        self._data_clr_btn.setColor(
            color_from_name(self._qrcode_item.data_color, '#000000')
        )
        self._data_clr_btn.blockSignals(False)

        self._background_clr_btn.blockSignals(True)
        self._background_clr_btn.setColor(
            color_from_name(self._qrcode_item.bg_color, '#FFFFFF')
        )
        self._background_clr_btn.blockSignals(False)

    def setDesignerInterface(self, iface):
        """
        Use iface to set the message_bar.
        """
        super().setDesignerInterface(iface)
        self.message_bar = iface.messageBar()

    def on_data_color_changed(self, color):
        """
        Slot raised when new data color is set.
        """
        self._qrcode_item.beginCommand(
            self.tr('Change data color'),
            QgsLayoutItem.UndoPictureFillColor
        )
        self._qrcode_item.blockSignals(True)
        self._qrcode_item.data_color = color.name()
        self._qrcode_item.blockSignals(False)
        self._qrcode_item.endCommand()

    def on_background_color_changed(self, color):
        """
        Slot raised when new background color is set.
        """
        self._qrcode_item.beginCommand(
            self.tr('Change background color'),
            QgsLayoutItem.UndoPictureFillColor
        )
        self._qrcode_item.blockSignals(True)
        self._qrcode_item.bg_color = color.name()
        self._qrcode_item.blockSignals(False)
        self._qrcode_item.endCommand()
