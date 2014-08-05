# -*- coding: utf-8 -*-
from cmsplugin_cascade import settings


def remove_duplicates(lst):
    dset = set()
    return [l for l in lst if l not in dset and not dset.add(l)]


def resolve_dependencies(filenames):
    """
    Given a single filename or a list of files and a mapping of dependencies,
    see ``settings.CASCADE_PLUGIN_DEPENDENCIES`` for details, return a list of other files
    resolving the dependency. The list is ordered, so that files having no further dependencies
    come first.
    Use this function to automatically resolve JavaScript dependencies in the ``Media`` subclasses.
    """
    dependencies = []
    if isinstance(filenames, (list, tuple)):
        for filename in filenames:
            dependencies.extend(resolve_dependencies(filename))
        return dependencies
    dependency_list = getattr(settings, 'CASCADE_PLUGIN_DEPENDENCIES', {}).get(filenames)
    if dependency_list:
        dependencies.extend(resolve_dependencies(dependency_list))
    return remove_duplicates(dependencies) + [filenames]
