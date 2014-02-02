# -*- coding: utf-8 -*-
from django import template
from classytags.arguments import IntegerArgument, Argument, StringArgument
from classytags.core import Options
from menus.templatetags.menu_tags import ShowMenu

register = template.Library()


class MainMenu(ShowMenu):
    name = 'main_menu'

    options = Options(
        IntegerArgument('from_level', default=0, required=False),
        IntegerArgument('to_level', default=100, required=False),
        StringArgument('template', default='cms/bootstrap3/main-menu.html', required=False),
        StringArgument('namespace', default=None, required=False),
        StringArgument('root_id', default=None, required=False),
        Argument('next_page', default=None, required=False),
    )

    def get_context(self, context, from_level, to_level, template, namespace, root_id, next_page):
        return super(MainMenu, self).get_context(context, from_level, to_level, 100, 100, template, namespace, root_id, next_page)

register.tag(MainMenu)
