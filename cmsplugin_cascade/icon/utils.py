import os, io, json, shutil
from django.core.exceptions import SuspiciousFileOperation
from cmsplugin_cascade import app_settings

import tempfile
try:
    import czipfile as zipfile
except ImportError:
    import zipfile


def unzip_archive(label, zip_ref):
    common_prefix = os.path.commonprefix(zip_ref.namelist())
    if not common_prefix:
        raise SuspiciousFileOperation("The zip archive {} is not packed correctly".format(label))
    icon_font_root = app_settings.CMSPLUGIN_CASCADE['icon_font_root']
    try:
        try:
            os.makedirs(icon_font_root)
        except os.error:
            pass  # the directory exists already
        temp_folder = tempfile.mkdtemp(prefix='', dir=icon_font_root)
        for member in zip_ref.infolist():
            zip_ref.extract(member, temp_folder)
        font_folder = os.path.join(temp_folder, common_prefix)

        # this is specific to fontello
        with io.open(os.path.join(font_folder, 'config.json'), 'r') as fh:
            config_data = json.load(fh)
    except Exception as exc:
        shutil.rmtree(temp_folder, ignore_errors=True)
        raise SuspiciousFileOperation("Can not unzip uploaded archive {}: {}".format(label, exc))
    return os.path.relpath(font_folder, icon_font_root), config_data
