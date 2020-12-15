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
import shutil
from zipfile import (
    is_zipfile,
    ZipFile
)


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

    if source is None:
        print('Source file is not defined.')
        return

    if not is_zipfile(source):
        print('Input file is not a valid zip file.')
        return

    plugin_name = os.getenv('PLUGIN_NAME')

    # Extract plugin files
    root_path = ''
    with ZipFile(source, 'r') as zf:
        if len(zf.namelist()) == 0:
            print('The zip package is empty.')
            return

        root_path = zf.namelist()[0]
        base_dir = '{0}{1}'.format(root_path, plugin_name)
        test_dir = '{0}/test'.format(base_dir)
        for fi in zf.namelist():
            if base_dir in fi:
                # Exclude test dir
                if test_dir in fi:
                    continue
                zf.extract(fi)

    plugin_package = os.getenv('PLUGIN_PACKAGE').replace('.zip', '')

    # Create archive
    shutil.make_archive(
        plugin_package,
        'zip',
        root_dir=root_path,
        base_dir=plugin_name
    )


if __name__ == '__main__':
    repackage_plugin()