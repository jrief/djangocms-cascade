import json
from cms.utils.plugins import get_plugin_class
from django.utils.translation import override as force_language, ugettext
from django.utils.encoding import force_text
from cms.toolbar.utils import get_toolbar_from_request


def get_plugin_toolbar_info(plugin, children=None, parents=None):
    data = plugin.get_plugin_info(children=children, parents=parents)
    help_text = ugettext(
        'Add plugin to %(plugin_name)s'
    ) % {'plugin_name': data['plugin_name']}

    data['onClose'] = False
    data['addPluginHelpTitle'] = force_text(help_text)
    data['plugin_order'] = ''
    data['plugin_restriction'] = children or []
    data['plugin_parent_restriction'] = parents or []
    return data


def get_plugin_restrictions(plugin, page=None, restrictions_cache=None):
    if restrictions_cache is None:
        restrictions_cache = {}

    plugin_type = plugin.plugin_type
    plugin_class = get_plugin_class(plugin.plugin_type)
    parents_cache = restrictions_cache.setdefault('plugin_parents', {})
    children_cache = restrictions_cache.setdefault('plugin_children', {})

    try:
        parent_classes = parents_cache[plugin_type]
    except KeyError:
        parent_classes = plugin_class.get_parent_classes(
            slot=plugin.placeholder.slot,
            page=page,
            instance=plugin,
        )

    if plugin_class.cache_parent_classes:
        parents_cache[plugin_type] = parent_classes or []

    try:
        child_classes = children_cache[plugin_type]
    except KeyError:
        child_classes = plugin_class.get_child_classes(
            slot=plugin.placeholder.slot,
            page=page,
            instance=plugin,
        )

    if plugin_class.cache_child_classes:
        children_cache[plugin_type] = child_classes or []
    return (child_classes, parent_classes)


def get_plugin_tree_as_json(request, plugins):
    from cms.utils.plugins import (
        build_plugin_tree,
        downcast_plugins,
        get_plugin_restrictions,
    )

    tree_data = []
    tree_structure = []
    restrictions = {}
    toolbar = get_toolbar_from_request(request)
    template = toolbar.templates.drag_item_template
    placeholder = plugins[0].placeholder
    host_page = placeholder.page
    copy_to_clipboard = placeholder.pk == toolbar.clipboard.pk
    plugins = downcast_plugins(plugins, select_placeholder=True)
    plugin_tree = build_plugin_tree(plugins)
    get_plugin_info = get_plugin_toolbar_info

    def collect_plugin_data(plugin):
        child_classes, parent_classes = get_plugin_restrictions(
            plugin=plugin,
            page=host_page,
            restrictions_cache=restrictions,
        )
        plugin_info = get_plugin_info(
            plugin,
            children=child_classes,
            parents=parent_classes,
        )

        tree_data.append(plugin_info)

        for plugin in plugin.child_plugin_instances or []:
            collect_plugin_data(plugin)

    with force_language(toolbar.toolbar_language):
        for root_plugin in plugin_tree:
            collect_plugin_data(root_plugin)
            context = {
                'plugin': root_plugin,
                'request': request,
                'clipboard': copy_to_clipboard,
                'cms_toolbar': toolbar,
            }
            tree_structure.append(template.render(context))
    tree_data.reverse()
    return json.dumps(
        {'html': '\n'.join(tree_structure), 'plugins': tree_data})
