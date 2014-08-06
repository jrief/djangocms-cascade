# -*- coding: utf-8 -*-
from cmsplugin_cascade import settings


def remove_duplicates(lst):
    """
    Emulate what a Python ``set()`` does, but keeping the element's order.
    """
    dset = set()
    return [l for l in lst if l not in dset and not dset.add(l)]


def resolve_dependencies(filenames):
    """
    Given a filename literal or a list of filenames and a mapping of dependencies (use
    ``settings.CASCADE_PLUGIN_DEPENDENCIES`` to check for details), return a list of other files
    resolving the dependency. The returned list is ordered, so that files having no further
    dependency come as first element and the passed in filenames come as the last element.
    Use this function to automatically resolve dependencies of CSS and JavaScript files in the
    ``Media`` subclasses.
    """
    dependencies = []
    if isinstance(filenames, (list, tuple)):
        for filename in filenames:
            dependencies.extend(resolve_dependencies(filename))
    else:
        filename = filenames
        dependency_list = getattr(settings, 'CASCADE_PLUGIN_DEPENDENCIES', {}).get(filename)
        if dependency_list:
            dependencies.extend(resolve_dependencies(dependency_list))
        dependencies.append(filename)
    return remove_duplicates(dependencies)
