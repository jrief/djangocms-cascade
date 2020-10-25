from distutils.version import LooseVersion
from django.db import OperationalError
from django.db.models import Q
from cms import __version__ as CMS_VERSION
from cms.models.pagemodel import Page
from cms.sitemaps import CMSSitemap

CMS_ = LooseVersion(CMS_VERSION) < LooseVersion('4.0')


def get_page_from_path(site, path):
    if CMS_:
        from cms.utils.page import get_page_from_path as get_page_from_path_CMS_
        page = get_page_from_path_CMS_(site, path)
    else:
        from cms.models import PageUrl
        page_urls = (
            PageUrl
            .objects
            .get_for_site(site)
            .filter(path=path)
            .select_related('page__node')
        )
        page_urls = list(page_urls)
        page = page_urls.page
    return page


def get_matching_published_pages(query_term, language):
    # otherwise resolve by search term
    if CMS_:
        matching_published_pages = Page.objects.published().public().filter(
            Q(title_set__title__icontains=query_term, title_set__language=language)
            | Q(title_set__path__icontains=query_term, title_set__language=language)
            | Q(title_set__menu_title__icontains=query_term, title_set__language=language)
            | Q(title_set__page_title__icontains=query_term, title_set__language=language)
        ).distinct().order_by('title_set__title').iterator()
    else:
        matching_published_pages = Page.objects.filter(
            Q(pagecontent_set__title__icontains=query_term, pagecontent_set__language=language)
            | Q(urls__path__icontains=query_term, pagecontent_set__language=language)
            | Q(pagecontent_set__menu_title__icontains=query_term, pagecontent_set__language=language)
            | Q(pagecontent_set__page_title__icontains=query_term, pagecontent_set__language=language)
        ).distinct().order_by('pagecontent_set__title').iterator()
    return matching_published_pages


def get_qs_pages_public():
    if CMS_:
        queryset = Page.objects.public()
    else:
        try:
            name_page_public = [str(page_url.page) for page_url in CMSSitemap().items()[:15]]
            queryset = Page.objects.filter(pagecontent_set__title__in=name_page_public)
        except OperationalError:
            #init db migrations
            queryset = Page.objects
    return queryset


def get_plugins_as_layered_tree(plugins):
    if CMS_:
       from cms.utils.plugins import build_plugin_tree
       return build_plugin_tree(plugins)
    else:
       from cms.utils.plugins import get_plugins_as_layered_tree as _get_plugins_as_layered_tree
       return _get_plugins_as_layered_tree(plugins)


def get_ancestor(list_plugins_name, plugin=False, _cms_initial_attributes=False):
    if _cms_initial_attributes and  'parent' in _cms_initial_attributes and _cms_initial_attributes['parent']:
        ancestor_plugin = _cms_initial_attributes['placeholder'].get_plugins().filter(
                 plugin_type__in=list_plugins_name,
                 position__range=[0,_cms_initial_attributes['position']]).order_by('position')[0]
    else:
        ancestor_plugin = plugin.placeholder.get_plugins().filter(
                             plugin_type__in=list_plugins_name,
                             position__range=[0, plugin.position]).order_by('position')[0]
    return ancestor_plugin


def get_prev_sibling(plugin):
    prev_sibling = None
    if CMS_:
        ordered_siblings = plugin.get_siblings().filter(placeholder=plugin.placeholder).order_by('position')
        pos = list(ordered_siblings).index(plugin.cmsplugin_ptr)
        if pos > 0:
            prev_sibling = ordered_siblings[pos - 1]
    else:
        if plugin.parent:
            prev_sibling = plugin.parent.get_children().order_by('position').filter(id__lt=plugin.id).last()
        else:
            prev_sibling = plugin.placeholder.get_plugin_tree_order(language=plugin.language).filter(id__lt=plugin.id).last()
    if prev_sibling:
        prev_sibling = prev_sibling.get_bound_plugin()
    return prev_sibling
