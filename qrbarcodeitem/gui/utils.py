# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : GUI utils
Description          : GUI utilities
Date                 : 01-10-2020
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
from qgis.PyQt.QtGui import QIcon


def get_icon(icon_name):
    """
    Creates an icon object from the given name contained in the image folder.
    :param icon_name: Icon name.
    :type icon_name: str
    :return: Returns a QIcon object from the given icon name or creates an
    empty icon if the name is not found in the given directory.
    :rtype: QIcon
    """
    path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'images',
        icon_name
    )
    if not os.path.exists(path):
        return QIcon()

    return QIcon(path)
