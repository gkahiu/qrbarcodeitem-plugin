# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : CodeValueWidget
Description          : Widget for specifying plain barcode values or use of
                       expressions.
Date                 : 02-10-2020
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
    QDialog,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget
)
from qgis.PyQt.QtCore import (
    pyqtSignal
)
from qgis.gui import (
    QgsExpressionBuilderDialog,
    QgsLayoutItemBaseWidget
)
from qgis.core import QgsApplication


class CodeValueWidget(QWidget):
    """Widget for specifying barcode or QR code values."""
    value_changed = pyqtSignal(str)

    def __init__(self, item_widget):
        super().__init__(item_widget)
        self._item_widget = item_widget
        self._value_text_edit = QTextEdit()
        self._value_text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        self._value_text_edit.textChanged.connect(
            self._on_code_value_changed
        )
        self._exp_btn = QPushButton(
            self.tr('Insert expression...')
        )
        self._exp_btn.setIcon(
            QgsApplication.getThemeIcon('/mIconExpression.svg')
        )
        self._exp_btn.clicked.connect(
            self._on_insert_expression
        )
        layout = QVBoxLayout()
        layout.addWidget(self._value_text_edit)
        layout.addWidget(self._exp_btn)
        self.setLayout(layout)

    @property
    def value_text_edit(self):
        """
        :return: Returns text edit widget for entering code values.
        :rtype: QPlainTextEdit
        """
        return self._value_text_edit

    @property
    def code_value(self):
        """
        :return: Returns the value in the text widget.
        :rtype: str
        """
        return self._value_text_edit.toPlainText()

    @code_value.setter
    def code_value(self, val):
        """
        Sets the text widget to the given value.
        :param val: Value to set in the text widget.
        :type val: str
        """
        if self.code_value == val:
            return

        self._value_text_edit.setPlainText(val)

    def highlight_invalid_data(self, invalid):
        """
        Highlights barcode data in red to indicate invalidity.
        :param invalid: True to highlight in red, else False to restore
        default color.
        :type invalid: bool
        """
        if invalid:
            stylesheet = 'color:#ff0000; font-weight: bold;'
        else:
            stylesheet = ''

        self._value_text_edit.setStyleSheet(stylesheet)

    def _on_code_value_changed(self):
        # Slot raised when the code value changes.
        code_txt = self.code_value
        self.value_changed.emit(code_txt)

    def _on_insert_expression(self):
        # Slot raised to insert an expression.
        if not isinstance(self._item_widget, QgsLayoutItemBaseWidget):
            return

        qrcode_item = self._item_widget.layoutObject()
        if not qrcode_item:
            return

        sel_txt = self._value_text_edit.textCursor().selectedText()
        # Edit expression text if specified
        if sel_txt.startswith('[%') and sel_txt.endswith('%]'):
            sel_txt = sel_txt.lstrip('[%')
            sel_txt = sel_txt.rstrip('%]')

        cov_layer = self._item_widget.coverageLayer()
        exp_ctx = qrcode_item.createExpressionContext()
        exp_dlg = QgsExpressionBuilderDialog(
            cov_layer,
            sel_txt,
            self,
            'generic',
            exp_ctx
        )
        exp_dlg.setWindowTitle(self.tr('Insert Expression for Barcode Data'))
        exp_dlg.setAllowEvalErrors(False)
        if exp_dlg.exec_() == QDialog.Accepted:
            exp = exp_dlg.expressionText()
            if exp:
                self._value_text_edit.setPlainText('[%{0}%]'.format(exp))

    def block_value_widget_signals(self, status):
        """
        Set True to block all signals emitted by the code value widget,
        else False to restore.
        :param status: True to block signals, False to restore.
        :type status: bool
        """
        self._value_text_edit.blockSignals(status)
