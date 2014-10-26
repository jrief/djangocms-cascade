# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db.models import get_model
from django.core.exceptions import ObjectDoesNotExist
from django_select2.fields import AutoModelSelect2Field
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.link.forms import TextLinkForm
from cmsplugin_cascade.link.models import SimpleLinkElement
from cmsplugin_cascade.link.plugin_base import TextLinkPluginBase
from cmsplugin_cascade.utils import resolve_dependencies
from shop.models.product import Product


class ProductSearchField(AutoModelSelect2Field):
    empty_value = []
    search_fields = ['product_code__startswith', 'translations__name__startswith']
    queryset = Product.objects.all()

    def security_check(self, request, *args, **kwargs):
        user = request.user
        if user and not user.is_anonymous() and user.is_staff:
            return True
        return False

    def prepare_value(self, value):
        if not value:
            return None
        return super(ProductSearchField, self).prepare_value(value)


class LinkForm(TextLinkForm):
    LINK_TYPE_CHOICES = (('cmspage', _("CMS Page")), ('product', _("Product")), ('exturl', _("External URL")), ('email', _("Mail To")),)
    product = ProductSearchField(required=False, label='',
        help_text=_("An internal link onto a product from the shop"))

    def clean_product(self):
        if self.cleaned_data.get('link_type') == 'product':
            self.cleaned_data['link_data'] = {
                'type': 'product',
                'model': 'shop.Product',
                'pk': self.cleaned_data['product'] and self.cleaned_data['product'].pk or None,
            }

    def set_initial_product(self, initial):
        try:
            Model = get_model(*initial['link']['model'].split('.'))
            initial['product'] = Model.objects.get(pk=initial['link']['pk'])
        except (KeyError, ObjectDoesNotExist):
            pass


class LinkPlugin(TextLinkPluginBase):
    model = SimpleLinkElement
    fields = ('link_content', ('link_type', 'cms_page', 'product', 'ext_url', 'mail_to'), 'glossary',)
    form = LinkForm

    class Media:
        js = resolve_dependencies('shop/js/admin/linkplugin.js')

plugin_pool.register_plugin(LinkPlugin)
