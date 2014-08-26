# -*- coding: utf-8 -*-
from django import template
from menus.menu_pool import menu_pool
from classytags.arguments import IntegerArgument, StringArgument, Argument
from classytags.helpers import InclusionTag
from classytags.core import Options
from menus.templatetags.menu_tags import flatten, remove

register = template.Library()


def cut_levels(nodes, start_level):
    """
    cutting nodes away from menus
    """
    final = []
    removed = []
    for node in nodes:
        if not hasattr(node, 'level'):
            # remove and ignore nodes that don't have level information
            remove(node, removed)
            continue
        if node.attr.get('soft_root', False):
            # remove and ignore nodes that are behind a node marked as 'soft_root'
            remove(node, removed)
            continue
        if node.level == start_level:
            # turn nodes that are on from_level into root nodes
            final.append(node)
            node.parent = None
            if not node.visible and not node.children:
                remove(node, removed)
        elif node.level == start_level + 1:
            # remove nodes that are deeper than one level
            node.children = []
        else:
            remove(node, removed)
        if not node.visible:
            keep_node = False
            for child in node.children:
                keep_node = keep_node or child.visible
            if not keep_node:
                remove(node, removed)
    for node in removed:
        if node in final:
            final.remove(node)
    return final


class MainMenu(InclusionTag):
    name = 'main_menu'
    template = 'menu/dummy.html'

    options = Options(
        StringArgument('template', default='cascade/bootstrap3/navbar-menu.html', required=False),
        StringArgument('namespace', default=None, required=False),
        StringArgument('root_id', default=None, required=False),
    )

    def get_context(self, context, template, namespace, root_id):
        try:
            # If there's an exception (500), default context_processors may not be called.
            request = context['request']
        except KeyError:
            return {'template': 'menu/empty.html'}

        start_level = 0
        nodes = menu_pool.get_nodes(request, namespace, root_id)
        if root_id:
            # find the root id and cut the nodes
            id_nodes = menu_pool.get_nodes_by_attribute(nodes, "reverse_id", root_id)
            if id_nodes:
                node = id_nodes[0]
                nodes = node.children
                for remove_parent in nodes:
                    remove_parent.parent = None
                start_level = node.level + 1
                nodes = flatten(nodes)
            else:
                nodes = []
        children = cut_levels(nodes, start_level)
        children = menu_pool.apply_modifiers(children, request, namespace, root_id, post_cut=True)
        context.update({'children': children, 'template': template})
        return context

register.tag(MainMenu)


class MainMenuBelowId(MainMenu):
    name = 'main_menu_below_id'
    options = Options(
        Argument('root_id', default=None, required=False),
        StringArgument('template', default='cascade/bootstrap3/navbar-menu.html', required=False),
        StringArgument('namespace', default=None, required=False),
    )

register.tag(MainMenuBelowId)


class Paginator(InclusionTag):
    name = 'paginator'
    template = 'cascade/bootstrap3/paginator.html'

    options = Options(
        IntegerArgument('page_range', default=5, required=False),
        StringArgument('template', default=None, required=False),
    )

    def get_context(self, context, page_range, template):
        try:
            current_page = int(context['request'].GET['page'])
        except (KeyError, ValueError):
            current_page = 1
        page_range -= 1
        paginator = context.get('paginator')
        first_page = max(1, min(current_page - page_range / 2, paginator.num_pages - page_range))
        last_page = min(first_page + page_range, paginator.num_pages)
        template = template or self.template
        context.update({
            'template': template,
            'show_paginator': paginator.num_pages > 1,
            'show_aquos': paginator.num_pages > page_range + 1,
            'pages': [{'num': p, 'active': p == current_page} for p in range(first_page, last_page + 1)],
            'laquo': {'num': first_page - 1, 'paginate': first_page > 1},
            'raquo': {'num': last_page + 1, 'paginate': last_page < paginator.num_pages},
        })
        return context

register.tag(Paginator)
