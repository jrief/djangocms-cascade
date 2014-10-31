# -*- coding: utf-8 -*-
from django.forms import widgets
from cmsplugin_cascade.plugin_base import CascadePluginBase


def reduce_breakpoints(plugin, field_name):
    """
    Narrow down the number of breakpoints in the widget of the named glossary_field. This is useful
    in case the container was defined with a subset of these breakpoints: xs, sm, md, lg.
    """
    if not isinstance(plugin, CascadePluginBase):
        raise ValueError('Plugin is not of type CascadePluginBase')
    complete_glossary = plugin.get_parent_instance().get_complete_glossary()
    if 'breakpoints' not in complete_glossary:
        return
    # find the glossary_field named 'responsive-heights' and restrict its breakpoint to the available ones
    widget = [f for f in plugin.glossary_fields if f.name == field_name][0].widget
    if not isinstance(widget, widgets.MultiWidget):
        raise ValueError('Widget for glossary_field {0} does not a multiple values')
    temp = [(l, widget.widgets[k]) for k, l in enumerate(widget.labels) if l in complete_glossary['breakpoints']]
    widget.labels, widget.widgets = (list(t) for t in zip(*temp))
