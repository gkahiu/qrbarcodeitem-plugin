# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : repackage_plugin
Description          : Repackage the zip file in the repo to only contain
                       core plugin files prior to uploading to QGIS plugins
                       repo.
Date                 : 15-12-2020
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


def repackage_plugin(source=None):
    """
    Create ZIP file that only contains the core files for uploading to QGIS
    plugins repo.
    :param source: Absolute or relative path of the source ZIP file. If not
    specified, then will attempt to extract it from the system environment
    variables.
    :type source: str
    """
    if source is None:
        source = os.getenv('REPO_PACKAGE')

    print(source)

    if source is None:
        print('Source file is not defined.')
        return


if __name__ == '__main__':
    repackage_plugin()