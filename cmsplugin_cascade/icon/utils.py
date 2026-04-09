import os, json

from django.core.exceptions import ImproperlyConfigured, SuspiciousFileOperation
from django.core.files.storage import storages

from cmsplugin_cascade import app_settings

try:
    import czipfile as zipfile
except ImportError:
    import zipfile


def unzip_archive(filename, zip_ref):
    icon_font_storage = app_settings.CMSPLUGIN_CASCADE['icon_font_storage']
    if icon_font_storage not in storages.backends:
        raise ImproperlyConfigured("Missing storage backend {} for icon fonts".format(icon_font_storage))
    storage = storages[icon_font_storage]
    common_prefix = os.path.commonprefix(zip_ref.namelist())
    if not common_prefix:
        raise SuspiciousFileOperation("The zip archive {} is not packed correctly".format(filename))
    common_prefix = common_prefix.rstrip('/')
    for zip_info in zip_ref.infolist():
        if zip_info.is_dir():
            continue
        with zip_ref.open(zip_info.filename) as zip_entry:
            storage.save(f'font_icons/{zip_info.filename}', zip_entry)
    with storage.open(f'font_icons/{common_prefix}/config.json', 'r') as fh:
        config_data = json.load(fh)
    return f'font_icons/{common_prefix}', config_data
