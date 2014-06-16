# -*- coding: utf-8 -*-
from django import template
from menus.menu_pool import menu_pool
from classytags.arguments import IntegerArgument, Flag, StringArgument, Argument
from classytags.helpers import InclusionTag
from classytags.core import Options
from menus.templatetags.menu_tags import flatten, remove, cut_after

register = template.Library()


def cut_levels(nodes, from_level, to_level, extra_inactive, extra_active):
    """
    cutting nodes away from menus
    """
    final = []
    removed = []
    selected = None
    for node in nodes:
        if not hasattr(node, 'level'):
            # remove and ignore nodes that don't have level information
            remove(node, removed)
            continue
        if node.level == from_level:
            # turn nodes that are on from_level into root nodes
            final.append(node)
            node.parent = None
        if not node.ancestor and not node.selected and not node.descendant:
            # cut inactive nodes to extra_inactive, but not of descendants of the selected node
            cut_after(node, extra_inactive, removed)
        if node.level > to_level and node.parent:
            # remove nodes that are too deep, but not nodes that are on from_level (local root nodes)
            remove(node, removed)
        if node.selected:
            selected = node
        if not node.visible and not node.children:
            remove(node, removed)
    if selected:
        cut_after(selected, extra_active, removed)
    if removed:
        for node in removed:
            if node in final:
                final.remove(node)
    return final


class MainMenu(InclusionTag):
    name = 'main_menu'
    template = 'menu/dummy.html'

    options = Options(
        IntegerArgument('from_level', default=0, required=False),
        Flag('with_children', default=True, false_values=['without_submenus']),
        StringArgument('template', default='cms/bootstrap3/main-menu.html', required=False),
        StringArgument('namespace', default=None, required=False),
        StringArgument('root_id', default=None, required=False),
        Argument('next_page', default=None, required=False),
    )

    def get_context(self, context, from_level, with_children, template, namespace, root_id, next_page):
        try:
            # If there's an exception (500), default context_processors may not be called.
            request = context['request']
        except KeyError:
            return {'template': 'menu/empty.html'}

        if next_page:
            children = next_page.children
        else:
            # new menu... get all the data so we can save a lot of queries
            nodes = menu_pool.get_nodes(request, namespace, root_id)
            if root_id:
                # find the root id and cut the nodes
                id_nodes = menu_pool.get_nodes_by_attribute(nodes, "reverse_id", root_id)
                if id_nodes:
                    node = id_nodes[0]
                    nodes = node.children
                    for remove_parent in nodes:
                        remove_parent.parent = None
                    from_level += node.level + 1
                    nodes = flatten(nodes)
                else:
                    nodes = []
            children = cut_levels(nodes, from_level, 1, 1, 1)
            children = menu_pool.apply_modifiers(children, request, namespace, root_id, post_cut=True)

        context.update({'children': children, 'template': template})
        return context


register.tag(MainMenu)
