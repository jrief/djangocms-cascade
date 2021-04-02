
def find_django_migrations_module(module_name):
    """ Tries to locate <module_name>.migrations_django (without actually importing it).
    Appends either ".migrations_django" or ".migrations" to module_name.
    For details why:
      https://docs.djangoproject.com/en/1.7/topics/migrations/#libraries-third-party-apps
    """
    import imp
    try:
        module_info = imp.find_module(module_name)
        module = imp.load_module(module_name, *module_info)
        imp.find_module('migrations_django', module.__path__)
        return module_name + '.migrations_django'
    except ImportError:
        return module_name + '.migrations'  # conforms to Django 1.7 defaults
