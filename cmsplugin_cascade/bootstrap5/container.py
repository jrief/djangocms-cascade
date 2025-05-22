import re

from django.core.exceptions import ValidationError
from django.forms import widgets
from django.forms.fields import BooleanField, CharField, ChoiceField, MultipleChoiceField
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext, gettext_lazy as _, ngettext, ngettext_lazy

from cms.models import CMSPlugin
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap5.breakpoint import Breakpoint
from cmsplugin_cascade.forms import ManageChildrenFormMixin

from formset.forms import ModelForm
from formset.widgets import Selectize

from .plugin_base import BootstrapPluginBase
from ..models import CascadeElement


def get_widget_choices():
    return [
        (Breakpoint.xs.name, format_html("&ensp;<strong>{}</strong><br>{} (<{}px)", "Extra small", Breakpoint.xs.label, 576)),
        (Breakpoint.sm.name, format_html("&ensp;<strong>{}</strong><br>{} (≥{}px, <{}px)", "Small", Breakpoint.sm.label, 576, 768)),
        (Breakpoint.md.name, format_html("&ensp;<strong>{}</strong><br>{} (≥{}px, <{}px)","Medium ", Breakpoint.md.label, 768, 992)),
        (Breakpoint.lg.name, format_html("&ensp;<strong>{}</strong><br>{} (≥{}px, <{}px)","Large", Breakpoint.lg.label, 992, 1200)),
        (Breakpoint.xl.name, format_html("&ensp;<strong>{}</strong><br>{} (≥{}px, <{}px)", "Extra large", Breakpoint.xl.label, 1200, 1400)),
        (Breakpoint.xxl.name, format_html("&ensp;<strong>{}</strong><br>{} (>{}px)", "XXL", Breakpoint.xxl.label, 1400)),
    ]


class ContainerBreakpointsWidget(widgets.CheckboxSelectMultiple):
    template_name = 'cascade/admin/widgets/bs5_container_breakpoints.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['optgroups'][0][1][0]['attrs']['checked'] = True
        context['widget']['optgroups'][0][1][0]['attrs']['disabled'] = True
        return context


class GridModelForm(ModelForm):
    title_attribute = CharField(
        label=_("Container Title"),
        required=False,
        help_text=_("Caption text added to the 'title' attribute of this container element."),
    )
    show_title = BooleanField(
        label=_("Show Title Attribute"),
        required=False,
        help_text=_("Show the container title as a heading element."),
    )

    class Meta:
        model = CascadeElement
        fields = '__all__'
        widgets = {
            'shared_glossary': Selectize(search_lookup='identifier__icontains')
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['show_title'] and not cleaned_data['title_attribute']:
            self.add_error('title_attribute', _("The title must be set, if the title attribute is shown."))
        return cleaned_data


class ContainerForm(GridModelForm):
    breakpoints = MultipleChoiceField(
        label=_("Available Breakpoints"),
        choices=get_widget_choices(),
        required=False,
        widget=ContainerBreakpointsWidget(choices=get_widget_choices()),
        help_text=_("Supported breakpoints for Bootstrap's grid system."),
    )
    layout = ChoiceField(
        label=_("Container Layout"),
        initial='container',
        choices=[
            ('container', _("Container with fixed widths for all breakpoints")),
            ('container-sm', _("Container with fixed widths starting from small breakpoint")),
            ('container-md', _("Container with fixed widths starting from medium breakpoint")),
            ('container-lg', _("Container with fixed widths starting from large breakpoint")),
            ('container-xl', _("Container with fixed widths starting from extra large breakpoint")),
            ('container-xxl', _("Container with fixed widths starting from XXL breakpoint")),
            ('container-fluid', _("Container with fluid widths for every breakpoint")),
        ],
        help_text=_(
            "Add <code>.container-*</code> class to set the most basic layout element in Bootstrap."
        ),
        widget=Selectize(),
    )

    class Meta(GridModelForm.Meta):
        fields_map = {'glossary': ['title_attribute', 'show_title', 'breakpoints', 'layout']}

    def clean_layout(self):
        pattern = re.compile(r'^container-(sm|md|lg|xl|xxl)$')
        if match := pattern.match(self.cleaned_data['layout']):
            if match.group(1) not in self.cleaned_data['breakpoints']:
                raise ValidationError(_("The selected breakpoints must contain the selected layout."))
        return self.cleaned_data['layout']


class BootstrapContainerPlugin(BootstrapPluginBase):
    name = _("Container")
    parent_classes = None
    require_parent = False
    form = ContainerForm
    footnote_html = """<p>
    For more information about this <strong>Container</strong> component please refer to the
    <a href="https://getbootstrap.com/docs/5.3/layout/containers/" target="_new">Bootstrap documentation</a>.
    </p>"""

    @classmethod
    def get_identifier(cls, obj):
        if title_attribute := obj.glossary.get('title_attribute'):
            return title_attribute
        layout = obj.glossary.get('layout', '')
        return mark_safe(f"<code>{layout}</code>")

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(BootstrapContainerPlugin, cls).get_css_classes(obj)
        css_classes.append(obj.glossary.get('layout', 'container'))
        return css_classes

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.sanitize_children()

plugin_pool.register_plugin(BootstrapContainerPlugin)


class SelectColumnsWidget(widgets.Select):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        try:
            # disable all options for number of columns less than the current number
            for k in range(0, int(value) - 1):
                context['widget']['optgroups'][k][1][0]['attrs'].setdefault('disabled', True)
        except (TypeError, ValueError):
            pass
        return context


class ColumnsChoiceField(ChoiceField):
    ROW_NUM_COLUMNS = [1, 2, 3, 4, 6, 12]

    def __init__(self, *args, **kwargs):
        choices = [
            (i, ngettext_lazy("{0} column", "{0} columns", i).format(i)) for i in self.ROW_NUM_COLUMNS
        ]
        if kwargs.get('required') is False:
            choices.insert(0, (None, gettext("undefined")))
        super().__init__(*args, choices=choices, **kwargs)


class BootstrapRowForm(ManageChildrenFormMixin, GridModelForm):
    """
    Form class to add non-materialized field to count the number of children.
    """
    num_children = ChoiceField(
        label=_("Number of Columns"),
        choices=[
            (i, ngettext_lazy("{0} column", "{0} columns", i).format(i))
            for i in ColumnsChoiceField.ROW_NUM_COLUMNS
        ],
        initial=3,
        widget=SelectColumnsWidget,
        help_text=_("Number of columns to be created with this row."),
    )
    row_columns = ColumnsChoiceField(
        label=_("Row Columns"),
        required=False,
        help_text=_("Add <code>.row-cols-*</code> class to set the number of columns that best render the content (default breakpoint).")
    )

    class Meta(GridModelForm.Meta):
        fields = '__all__'
        fields_map = {'glossary': ['title_attribute', 'show_title', 'row_columns']}


class BootstrapRowPlugin(BootstrapPluginBase):
    name = _("Row")
    default_css_class = 'row'
    parent_classes = ['BootstrapContainerPlugin', 'BootstrapColumnPlugin', 'BootstrapJumbotronPlugin']
    form = BootstrapRowForm
    footnote_html = """<p>
    For more information about this <strong>Row</strong> component please refer to the
    <a href="https://getbootstrap.com/docs/5.3/layout/grid/" target="_new">Bootstrap documentation</a>.
    </p>"""

    @classmethod
    def get_identifier(cls, obj):
        if title_attribute := obj.glossary.get('title_attribute'):
            return title_attribute
        num_cols = obj.get_num_children()
        return ngettext("with {0} column", "with {0} columns", num_cols).format(num_cols)

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(BootstrapRowPlugin, cls).get_css_classes(obj)
        if row_columns := obj.glossary.get('row_columns'):
            css_classes.append(f'row-cols-{row_columns}')
        for bp in cls.get_breakpoints(obj):
            if row_columns := obj.glossary.get(f'row_columns_{bp}'):
                css_classes.append(f'row-cols-{bp}-{row_columns}')
        if align_items := obj.glossary.get('align_items'):
            css_classes.append(f'align-items-{align_items}')
        if justify_content := obj.glossary.get('justify_content'):
            css_classes.append(f'justify-content-{justify_content}')
        return css_classes

    def get_model_form(self):
        if self.object:
            breakpoints = self.get_breakpoints(self.object)
        elif 'plugin_parent' in self.request.GET:
            breakpoints = self.get_breakpoints(CMSPlugin.objects.get(pk=self.request.GET['plugin_parent']))
        else:
            breakpoints = []
        attrs, glossary_fields = {}, []

        # define the Row Columns fields
        for bp in breakpoints:
            if bp == 'xs':
                continue
            field_name = f'row_columns_{bp}'
            attrs[field_name] = ColumnsChoiceField(
                label=_("Row Columns for {}").format(Breakpoint[bp].label),
                required=False,
                help_text=gettext(
                    "Add <code>.row-cols-{}-*</code> class to set the number of columns that best render the content."
                ).format(bp),
            )
            glossary_fields.append(field_name)

        # define the align-items-* content field
        align_items_choices = [
            (None, gettext("No alignment")),
            ('start', gettext("Start")),
            ('center', gettext("Center")),
            ('end', gettext("End")),
        ]
        attrs['align_items'] = ChoiceField(
            label=gettext("Align Items"),
            choices=align_items_choices,
            required=False,
            help_text=gettext("Change the vertical alignment with the responsive <code>align-items-*</code> classes."),
        )
        glossary_fields.append('align_items')

        # define the justify content field
        justify_content_choices = [
            (None, gettext("No justify")),
            ('start', gettext("Start")),
            ('center', gettext("Center")),
            ('end', gettext("End")),
            ('around', gettext("Around")),
            ('between', gettext("Between")),
            ('evenly', gettext("Evenly")),
        ]
        attrs['justify_content'] = ChoiceField(
            label=gettext("Justify Content"),
            choices=justify_content_choices,
            required=False,
            help_text=gettext(
                "Change the horizontal alignment with any of the responsive <code>justify-content-*</code> classes."
            ),
        )
        glossary_fields.append('justify_content')

        model_form = super().get_model_form()
        attrs['Meta'] = type('Meta', (model_form.Meta,), {
            'fields_map': {'glossary': glossary_fields},
        })
        model_form = type(model_form.__name__, model_form.__mro__, attrs)
        if self.object:
            model_form.base_fields['num_children'].initial = self.object.get_num_children()
        return model_form

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super().save_model(request, obj, form, change)
        child_glossary = {'xs-column-width': 'col'}
        self.extend_children(obj, wanted_children, BootstrapColumnPlugin, child_glossary=child_glossary)

plugin_pool.register_plugin(BootstrapRowPlugin)


class BootstrapColumnPlugin(BootstrapPluginBase):
    name = _("Column")
    parent_classes = ['BootstrapRowPlugin']
    child_classes = ['BootstrapJumbotronPlugin']
    alien_child_classes = True
    form = GridModelForm
    footnote_html = """<p>
    For more information about this <strong>Column</strong> component, please refer to the
    <a href="https://getbootstrap.com/docs/5.3/layout/columns/" target="_new">Bootstrap documentation</a>.
    </p>"""

    @classmethod
    def get_identifier(cls, obj):
        if title_attribute := obj.glossary.get('title_attribute'):
            return title_attribute
        return mark_safe(gettext("<code>col-{}</code>").format(obj.glossary.get('column_width', '')))

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(BootstrapColumnPlugin, cls).get_css_classes(obj)
        if column_width := obj.glossary.get(f'column_width'):
            css_classes.append(f'col-{column_width}')
        else:
            css_classes.append('col')
        if column_ordering := obj.glossary.get(f'column_ordering'):
            css_classes.append(f'order-{column_ordering}')
        if margin_utility := obj.glossary.get(f'margin_utility'):
            css_classes.append(f'{margin_utility}-auto')
        for bp in cls.get_breakpoints(obj):
            if column_width := obj.glossary.get(f'column_width_{bp}'):
                css_classes.append(f'col-{bp}-{column_width}')
            if column_ordering := obj.glossary.get(f'column_ordering_{bp}'):
                css_classes.append(f'order-{bp}-{column_ordering}')
            if column_offset := obj.glossary.get(f'column_offset_{bp}'):
                css_classes.append(f'offset-{bp}-{column_offset}')
            if margin_utility := obj.glossary.get(f'margin_utility_{bp}'):
                css_classes.append(f'{margin_utility}-{bp}-auto')
        if align_self := obj.glossary.get('align_self'):
            css_classes.append(f'align-self-{align_self}')
        return css_classes

    def get_model_form(self):
        if self.object:
            breakpoints = self.get_breakpoints(self.object)
        elif 'plugin_parent' in self.request.GET:
            breakpoints = self.get_breakpoints(CMSPlugin.objects.get(pk=self.request.GET['plugin_parent']))
        else:
            breakpoints = []
        attrs, glossary_fields = {}, []

        # define the width fields
        attrs['column_width'] = ColumnsChoiceField(
            label=_("Column width"),
            help_text=gettext("Set the column width using <code>col-*</code> (default breakpoint)."),
        )
        glossary_fields.append('column_width')
        for bp in breakpoints:
            field_name = f'column_width_{bp}'
            attrs[field_name] = ColumnsChoiceField(
                label=_("Column width for {}").format(Breakpoint[bp].label),
                required=False,
                help_text=gettext("Set the column width using <code>col-{}-*</code>.").format(bp),
            )
            glossary_fields.append(field_name)

        # define the reordering fields
        ordering_choices = [
            (None, _("No reordering")),
            ('last', _("Reorder to last")),
            ('first', _("Reorder to first")),
            *((str(i), gettext("Reorder to {}").format(i)) for i in range(1, 6))
        ]
        attrs['column_ordering'] = ChoiceField(
            label=_("Column ordering"),
            choices=ordering_choices,
            required=False,
            help_text=gettext("Control the ordering of columns using the <code>.order-*</code> class (default breakpoint)."),
        )
        glossary_fields.append('column_ordering')
        for bp in breakpoints:
            field_name = f'column_ordering_{bp}'
            attrs[field_name] = ChoiceField(
                label=_("Column ordering for {}").format(Breakpoint[bp].label),
                choices=ordering_choices,
                required=False,
                help_text=gettext(
                    "Control the ordering of columns using the <code>.order-{}-*</code> class."
                ).format(bp),
            )
            glossary_fields.append(field_name)

        # define the offsetting fields
        offset_choices = [
            (None, _("No offset")),
            *((str(i), gettext("Offset to {}").format(i)) for i in range(0, 10))
        ]
        for bp in breakpoints:
            field_name = f'column_offset_{bp}'
            attrs[field_name] = ChoiceField(
                label=_("Column offset for {}").format(Breakpoint[bp].label),
                choices=offset_choices,
                required=False,
                help_text=gettext("Move columns to the right using <code>.offset-{}-*</code> classes.").format(bp),
            )
            glossary_fields.append(field_name)

        # define the margin utility fields
        margin_choices = [
            (None, gettext("No margin")),
            ('ms', gettext("From previous")),
            ('me', gettext("Till next")),
        ]
        attrs['margin_utility'] = ChoiceField(
            label=gettext("Auto Margin"),
            choices=margin_choices,
            required=False,
            help_text=gettext(
                "Add margin utility <code>.*-auto</code> to force sibling columns away from one another (default breakpoint)."
            ),
        )
        glossary_fields.append('margin_utility')
        for bp in breakpoints:
            field_name = f'margin_utility_{bp}'
            attrs[field_name] = ChoiceField(
                label=gettext("Auto Margin for {}").format(Breakpoint[bp].label),
                choices=margin_choices,
                required=False,
                help_text=mark_safe(
                    gettext(
                        "Add margin utility <code>.*-{}-auto</code> to force sibling columns away from one another."
                    ).format(bp)
                ),
            )
            glossary_fields.append(field_name)

        # define the align-self-* content field
        align_self_choices = [
            (None, gettext("No alignment")),
            ('start', gettext("Start")),
            ('center', gettext("Center")),
            ('end', gettext("End")),
        ]
        attrs['align_self'] = ChoiceField(
            label=gettext("Align Self"),
            choices=align_self_choices,
            required=False,
            help_text=mark_safe(gettext("Change the vertical alignment with the responsive <code>align-self-*</code> classes.")),
        )
        glossary_fields.append('align_self')

        model_form = super().get_model_form()
        attrs['Meta'] = type('Meta', (model_form.Meta,), {
            'fields_map': {'glossary': glossary_fields},
        })
        model_form = type(model_form.__name__, model_form.__mro__, attrs)
        return model_form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.sanitize_children()

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = super().sanitize_model(obj)
        return sanitized

plugin_pool.register_plugin(BootstrapColumnPlugin)
