# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.template.loader import get_template
from classytags.helpers import InclusionTag

register = template.Library()


class SectionSelector(InclusionTag):
    """
    Inclusion tag for displaying cart summary.
    """
    def get_template(self, context, **kwargs):
        template = get_template([
            'cascade/templatetags/section-selector.html',
        ])
        return template.template.name

    def get_context(self, context):
        request = context['request']
        return context

register.tag(SectionSelector)
