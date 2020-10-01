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
from qgis.gui import (
    QgsLayoutItemBaseWidget
)


class QrCodeLayoutItemWidget(QgsLayoutItemBaseWidget): # pylint: disable=too-few-public-methods
    """Widget for configuring a QrCodeLayoutItem."""
    def __init__(self, parent, layout_object):
        super().__init__(parent, layout_object)
        self._name = ''
