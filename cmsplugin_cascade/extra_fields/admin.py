# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from django.core.exceptions import ValidationError
from django.contrib import admin
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.forms import widgets
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade import settings
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.models import PluginExtraFields
from cmsplugin_cascade.extra_fields.mixins import ExtraFieldsMixin
from cmsplugin_cascade.widgets import JSONMultiWidget, MultipleCascadingSizeWidget
from cmsplugin_cascade.utils import rectify_partial_form_field


class ClassNamesWidget(widgets.TextInput):
    """
    Use this field to enter a list of comma separated CSS class names.
    """
    DEFAULT_ATTRS = {'style': 'width: 35em;'}
    validation_pattern = re.compile(r'^[A-Za-z0-9_-]+$')
    invalid_message = _("In '%(label)s': Value '%(value)s' is not a valid color.")

    def __init__(self, attrs=DEFAULT_ATTRS, required=False):
        self.required = required
        super(ClassNamesWidget, self).__init__(attrs=attrs)

    def validate(self, value):
        for val in value.split(','):
            if val and not self.validation_pattern.match(val.strip()):
                raise ValidationError(_("'%s' is not a valid CSS class name.") % val)


class PluginExtraFieldsAdmin(admin.ModelAdmin):
    list_display = ('name', 'module', 'site', 'allowed_classes_styles')
    DISTANCE_UNITS = (('px,em,%', _("px, em and %")), ('px,em', _("px and em")),
                      ('px,%', _("px and %")), ('px', _("px")), ('%', _("%")),)
    classname_fields = ((
        GlossaryField(
            ClassNamesWidget(),
            label=_("CSS class names"),
            name='class_names',
            help_text=_("Freely selectable CSS classnames for this Plugin, separated by commas."),
        ),
        GlossaryField(
            widgets.CheckboxInput(),
            label=_("Allow multiple"),
            name='multiple'
        ),
    ),)

    class Media:
        css = {'all': ('cascade/css/admin/partialfields.css',)}

    def __init__(self, model, admin_site):
        super(PluginExtraFieldsAdmin, self).__init__(model, admin_site)
        self.style_fields = []
        for style, choices_tuples in settings.CMSPLUGIN_CASCADE['extra_inline_styles'].items():
            extra_field = GlossaryField(
                widgets.CheckboxSelectMultiple(choices=((c, c) for c in choices_tuples[0])),
                label=_("Customized {0} Fields:").format(style),
                name='extra_fields:{0}'.format(style)
            )
            Widget = choices_tuples[1]
            if issubclass(Widget, MultipleCascadingSizeWidget):
                self.style_fields.append((
                    extra_field,
                    GlossaryField(
                        widgets.Select(choices=self.DISTANCE_UNITS),
                        label=_("Units for {0} Fields:").format(style),
                        name='extra_units:{0}'.format(style),
                        initial=self.DISTANCE_UNITS[0][0],
                    ),
                ))
            else:
                self.style_fields.append(extra_field)

    @cached_property
    def plugins_for_site(self):
        def show_in_backend(plugin):
            try:
                config = settings.CMSPLUGIN_CASCADE['plugins_with_extra_fields'][plugin.__name__]
            except KeyError:
                return False
            else:
                assert issubclass(plugin, ExtraFieldsMixin)
                return config.allow_override

        cascade_plugins = set([p for p in plugin_pool.get_all_plugins() if show_in_backend(p)])
        return [(p.__name__, '{}: {}'.format(p.module, force_text(p.name))) for p in cascade_plugins]

    def get_form(self, request, obj=None, **kwargs):
        """
        Build the form used for changing the model.
        """
        kwargs.update(widgets={
            'plugin_type': widgets.Select(choices=self.plugins_for_site),
            'css_classes': JSONMultiWidget(self.classname_fields),
            'inline_styles': JSONMultiWidget(self.style_fields)
        })
        form = super(PluginExtraFieldsAdmin, self).get_form(request, obj, **kwargs)
        rectify_partial_form_field(form.base_fields['css_classes'], self.classname_fields)
        form.classname_fields = self.classname_fields
        rectify_partial_form_field(form.base_fields['inline_styles'], self.style_fields)
        form.style_fields = self.style_fields
        return form

    def has_add_permission(self, request):
        """
        Only if at least one plugin uses the class ExtraFieldsMixin, allow to add an instance.
        """
        return len(self.plugins_for_site) > 0

    def module(self, obj):
        return plugin_pool.get_plugin(obj.plugin_type).module
    module.short_description = _("Module")

    def allowed_classes_styles(self, obj):
        clsn = [cn for cn in obj.css_classes.get('class_names', '').split(',') if cn]
        sef = [len(group) for ef, group in obj.inline_styles.items() if ef.startswith('extra_fields:')]
        return "{} / {}".format(len(clsn), sum(sef))
    allowed_classes_styles.short_description = _("Allowed Classes and Styles")

admin.site.register(PluginExtraFields, PluginExtraFieldsAdmin)
