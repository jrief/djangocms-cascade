import sys
from importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from . import app_settings


for module in app_settings.CASCADE_PLUGINS:
    try:
        # if a module was specified, load all plugins in module settings
        module_settings = import_module('{}.settings'.format(module))
        module_plugins = getattr(module_settings, 'CASCADE_PLUGINS', [])
        for p in module_plugins:
            try:
                import_module('{}.{}'.format(module, p))
            except ImportError as err:
                traceback = sys.exc_info()[2]
                msg = "Plugin {} as specified in {}.settings.CASCADE_PLUGINS could not be loaded: {}"
                raise ImproperlyConfigured(msg.format(p, module, err.with_traceback(traceback)))
    except ImportError:
        try:
            # otherwise try with cms_plugins in the named module
            import_module('{}.cms_plugins'.format(module))
        except ImportError:
            # otherwise just use the named module as plugin
            import_module('{}'.format(module))
