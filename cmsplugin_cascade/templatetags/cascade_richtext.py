from django import template

from cms.models.pagemodel import Page as PageModel

register = template.Library()


@register.simple_tag
def page_url(page_id):
    page = PageModel.objects.get(pk=page_id)
    return page.get_absolute_url()
