import re
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.forms.fields import BooleanField, CharField, ChoiceField, MultipleChoiceField
from django.forms.models import ModelForm
from django.http.response import HttpResponse
from django.template.loader import render_to_string
from django.urls import re_path
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from entangled.forms import EntangledModelForm

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade import app_settings
from cmsplugin_cascade.fields import SizeField
from cmsplugin_cascade.models import PluginExtraFields, TextEditorConfigFields, IconFont
from cmsplugin_cascade.extra_fields.mixins import ExtraFieldsMixin


class PluginExtraFieldsForm(EntangledModelForm):
    validation_pattern = re.compile(r'^[A-Za-z0-9_-]+$')

    class_names = CharField(
        label=_("CSS class names"),
        required=False,
        widget=widgets.TextInput(attrs={'style': 'width: 50em;'}),
        help_text=_("Freely selectable CSS classnames for this Plugin, separated by commas."),
    )

    multiple = BooleanField(
        label=_("Allow multiple"),
        required=False,
        help_text=_("Allow to select multiple of the above CSS classes."),
    )

    class Meta:
        untangled_fields = ['plugin_type', 'site']
        entangled_fields = {
            'css_classes': ['class_names', 'multiple'],
            'inline_styles': [],
        }

    def clean_class_names(self):
        value = self.cleaned_data['class_names']
        for val in value.split(','):
            val = val.strip()
            if val and not self.validation_pattern.match(val):
                msg = _("CSS class '{}' contains invalid characters.")
                raise ValidationError(msg.format(val))
        return value


class PluginExtraFieldsAdmin(admin.ModelAdmin):
    list_display = ['name', 'module', 'site', 'allowed_classes_styles']
    DISTANCE_UNITS = [
        ('px,em,rem,%', _("px, em, rem and %")),
        ('px,em,%', _("px, em and %")),
        ('px,rem,em', _("px, rem and em")),
        ('px,em', _("px and em")),
        ('px,rem,%', _("px, rem and %")),
        ('px,%', _("px and %")),
        ('px,rem', _("px and rem")),
        ('px', _("px")),
        ('%,rem', _("% and rem")),
        ('%', _("%")),
        ('px,em,rem,%,auto', _("px, em, rem, % and auto")),
        ('px,em,%,auto', _("px, em, % and auto")),
        ('px,rem,em,auto', _("px, rem, em and auto")),
        ('px,em,auto', _("px, em and auto")),
        ('px,rem,%,auto', _("px, rem, % and auto")),
        ('px,%,,auto', _("px, % and auto")),
        ('px,rem,auto', _("px, rem and auto")),
        ('px,auto', _("px and auto")),
        ('%,rem,auto', _("%, rem and auto")),
        ('%,auto', _("% and auto")),
    ]

    class Media:
        css = {'all': ('cascade/css/admin/partialfields.css',)}

    @cached_property
    def plugins_for_site(self):
        def show_in_backend(plugin):
            try:
                config = app_settings.CMSPLUGIN_CASCADE['plugins_with_extra_fields'][plugin.__name__]
            except KeyError:
                return False
            else:
                assert issubclass(plugin, ExtraFieldsMixin), "Expected plugin to be of type `ExtraFieldsMixin`."
                return config.allow_override

        cascade_plugins = set([p for p in plugin_pool.get_all_plugins() if show_in_backend(p)])
        return [(p.__name__, '{}: {}'.format(p.module, str(p.name))) for p in cascade_plugins]

    def get_form(self, request, obj=None, **kwargs):
        form_fields = {
            'plugin_type': ChoiceField(choices=self.plugins_for_site),
        }
        for style, choices_tuples in app_settings.CMSPLUGIN_CASCADE['extra_inline_styles'].items():
            form_fields['extra_fields:{0}'.format(style)] = MultipleChoiceField(
                label=_("Customized {0} fields:").format(style),
                choices=[(c, c) for c in choices_tuples[0]],
                required=False,
                widget=widgets.CheckboxSelectMultiple,
                help_text=_("Allow these extra inlines styles for the given plugin type."),
            )
            if issubclass(choices_tuples[1], SizeField):
                form_fields['extra_units:{0}'.format(style)] = ChoiceField(
                    label=_("Units for {0} Fields:").format(style),
                    choices=self.DISTANCE_UNITS,
                    required=False,
                    help_text=_("Allow these size units for customized {0} fields.").format(style),
                )
        inline_styles_fields = list(form_fields.keys())
        form = type('PluginExtraFieldsForm', (PluginExtraFieldsForm,), form_fields)
        form._meta.entangled_fields['inline_styles'] = inline_styles_fields
        kwargs.setdefault('form', form)
        return super().get_form(request, obj=None, **kwargs)

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


class TextEditorConfigForm(ModelForm):
    validation_pattern = re.compile(r'^[A-Za-z0-9_-]+$')

    class Meta:
        fields = ['name', 'element_type', 'css_classes']

    def clean_css_classes(self):
        css_classes = []
        for val in self.cleaned_data['css_classes'].split(' '):
            if val:
                if self.validation_pattern.match(val.strip()):
                    css_classes.append(val)
                else:
                    raise ValidationError(_("'%s' is not a valid CSS class name.") % val)
        return ' '.join(css_classes)


class TextEditorConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'element_type']
    form = TextEditorConfigForm

    def get_urls(self):
        return [
            re_path(r'^wysiwig-config\.js$', self.render_texteditor_config,
                name='cascade_texteditor_config'),
        ] + super().get_urls()

    def render_texteditor_config(self, request):
        context = {
            'text_editor_configs': TextEditorConfigFields.objects.all(),
        }
        if 'cmsplugin_cascade.icon' in settings.INSTALLED_APPS:
            context['icon_fonts'] = IconFont.objects.all()
        javascript = render_to_string('cascade/admin/ckeditor.wysiwyg.txt', context)
        return HttpResponse(javascript, content_type='application/javascript')

admin.site.register(TextEditorConfigFields, TextEditorConfigAdmin)
