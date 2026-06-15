import re
from typing import Optional

from django.core.exceptions import ValidationError
from django.forms import widgets
from django.forms.fields import BooleanField, CharField, ChoiceField, MultipleChoiceField
from django.utils.safestring import mark_safe
from django.utils.translation import gettext, gettext_lazy as _, ngettext, ngettext_lazy

from cms.models import CMSPlugin, Page
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap5.breakpoint import Breakpoint, get_widget_choices
from cmsplugin_cascade.forms import ManageChildrenFormMixin

from formset.forms import ModelForm
from formset.widgets import Selectize

from .plugin_base import BootstrapPluginBase
from ..models import CascadeElement


class GridModelForm(ModelForm):
    title_attribute = CharField(
        label=_("Internal Title"),
        required=False,
        help_text=_("Internal title attribute to organize components in the structure editor."),
    )

    class Meta:
        model = CascadeElement
        exclude = ['shared_glossary']
        fields_map = {'glossary': ['title_attribute']}


class ContainerBreakpointsWidget(widgets.CheckboxSelectMultiple):
    template_name = 'cascade/admin/widgets/bs5_container_breakpoints.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['optgroups'][0][1][0]['attrs']['checked'] = True
        context['widget']['optgroups'][0][1][0]['attrs']['disabled'] = True
        return context


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
        fields_map = {'glossary': ['title_attribute', 'breakpoints', 'layout']}

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
        empty_label = kwargs.pop('empty_label', gettext("undefined"))
        if kwargs.get('required') is False:
            choices.insert(0, (None, empty_label))
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
        label=_("Row Columns for ‘{}’").format(Breakpoint.xs.label),
        required=False,
        empty_label=_("Unset"),
        help_text=_("Add <code>.row-cols-*</code> class to set the number of columns that best render the content (default breakpoint).")
    )

    class Meta(GridModelForm.Meta):
        fields = '__all__'
        fields_map = {'glossary': ['title_attribute', 'row_columns']}

    def save(self):
        super().save()
        child_glossary = {'column_width': '1'}
        self.extend_children(BootstrapColumnPlugin, child_glossary=child_glossary)
        return self.instance


class BootstrapRowPlugin(BootstrapPluginBase):
    name = _("Row")
    default_css_class = 'row'
    parent_classes = ['BootstrapContainerPlugin', 'BootstrapColumnPlugin', 'BootstrapJumbotronPlugin']
    form = BootstrapRowForm

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

        model_form = super().get_model_form()
        glossary_fields = list(model_form._meta.fields_map['glossary'])
        attrs, prev_bp = {}, 'xs'

        # define the Row Columns fields
        for bp in breakpoints:
            if bp == 'xs':
                continue
            field_name = f'row_columns_{bp}'
            attrs[field_name] = ColumnsChoiceField(
                label=_("Row Columns for ‘{}’").format(Breakpoint[bp].label),
                required=False,
                empty_label=_("Inherit from “Row Columns for ‘{}’”").format(Breakpoint[prev_bp].label),
                help_text=gettext(
                    "Add <code>.row-cols-{}-*</code> class to set the number of columns that best render the content."
                ).format(bp),
            )
            glossary_fields.append(field_name)
            prev_bp = bp

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

        attrs['Meta'] = type('Meta', (model_form.Meta,), {
            'fields_map': {'glossary': glossary_fields},
        })
        model_form = type(model_form.__name__, model_form.__mro__, attrs)
        if self.object and self.object.pk:
            model_form.base_fields['num_children'].initial = self.object.get_num_children()
        return model_form

plugin_pool.register_plugin(BootstrapRowPlugin)


class BootstrapColumnForm(GridModelForm):
    column_width = ColumnsChoiceField(
        label=_("Column Width"),
        required=False,
        empty_label=_("Auto"),
        help_text=gettext("Set the column width using <code>col-*</code> (default breakpoint)."),
    )
    ORDERING_CHOICES = [
        (None, _("No reordering")),
        ('last', _("Reorder to last")),
        ('first', _("Reorder to first")),
        *((str(i), gettext("Reorder to {}").format(i)) for i in range(1, 6))
    ]
    column_ordering = ChoiceField(
        label=_("Column ordering"),
        choices=ORDERING_CHOICES,
        required=False,
        help_text=gettext(
            "Control the ordering of columns using the <code>.order-*</code> class (default breakpoint)."),
    )
    MARGIN_CHOICES = [
        (None, gettext("No margin")),
        ('ms', gettext("From previous")),
        ('me', gettext("Till next")),
    ]
    margin_utility = ChoiceField(
        label=gettext("Auto Margin"),
        choices=MARGIN_CHOICES,
        required=False,
        help_text=gettext(
            "Add margin utility <code>.*-auto</code> to force sibling columns away from one another (default breakpoint)."
        ),
    )
    ALIGN_SELF_CHOICES = [
        (None, gettext("No alignment")),
        ('start', gettext("Start")),
        ('center', gettext("Center")),
        ('end', gettext("End")),
    ]
    align_self = ChoiceField(
        label=gettext("Align Self"),
        choices=ALIGN_SELF_CHOICES,
        required=False,
        help_text=mark_safe(
            gettext("Change the vertical alignment with the responsive <code>align-self-*</code> classes.")),
    )

    class Meta(GridModelForm.Meta):
        fields = '__all__'
        fields_map = {'glossary': [
            'title_attribute', 'column_width', 'column_ordering', 'margin_utility', 'align_self',
        ]}


class BootstrapColumnPlugin(BootstrapPluginBase):
    name = _("Column")
    parent_classes = ['BootstrapRowPlugin']
    alien_child_classes = True
    form = BootstrapColumnForm
    footnote_html = """<p>
    For more information about this <strong>Column</strong> component, please refer to the
    <a href="https://getbootstrap.com/docs/5.3/layout/columns/" target="_new">Bootstrap documentation</a>.
    </p>"""

    @classmethod
    def get_identifier(cls, obj):
        if title_attribute := obj.glossary.get('title_attribute'):
            return title_attribute
        col = 'col-{column_width}'.format(**obj.glossary) if obj.glossary.get('column_width') else 'col'
        return mark_safe(gettext("with <code>{}</code>").format(col))

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
        if self.object and self.object.pk:
            breakpoints = self.get_breakpoints(self.object)
        elif 'plugin_parent' in self.request.GET:
            breakpoints = self.get_breakpoints(CMSPlugin.objects.get(pk=self.request.GET['plugin_parent']))
        else:
            breakpoints = []
        if 'xs' in breakpoints:
            breakpoints.remove('xs')

        model_form = super().get_model_form()
        glossary_fields = list(model_form._meta.fields_map['glossary'])
        attrs = {}

        # define the width fields
        prev_bp = 'xs'
        for index, bp in enumerate(breakpoints, glossary_fields.index('column_width') + 1):
            field_name = f'column_width_{bp}'
            attrs[field_name] = ColumnsChoiceField(
                label=_("Column Width for ‘{}’").format(Breakpoint[bp].label),
                required=False,
                empty_label=_("Inherit from “Column Width for ‘{}’”").format(Breakpoint[prev_bp].label),
                help_text=gettext("Set the column width using <code>col-{}-*</code>.").format(bp),
            )
            glossary_fields.insert(index, field_name)
            prev_bp = bp

        # add reordering fields for extra breakpoints
        prev_bp = 'xs'
        index = glossary_fields.index('column_ordering')
        for index, bp in enumerate(breakpoints, index + 1):
            field_name = f'column_ordering_{bp}'
            ordering_choices = BootstrapColumnForm.ORDERING_CHOICES.copy()
            ordering_choices[0] = (
                None, gettext("Inherit from “Column Ordering for ‘{}’”").format(Breakpoint[prev_bp].label)
            )
            attrs[field_name] = ChoiceField(
                label=gettext("Column Ordering for ‘{}’").format(Breakpoint[bp].label),
                choices=ordering_choices,
                required=False,
                help_text=gettext(
                    "Control the ordering of columns using the <code>.order-{}-*</code> class."
                ).format(bp),
            )
            glossary_fields.insert(index, field_name)
            prev_bp = bp

        # add offsetting fields for extra breakpoints
        offset_choices = [
            (None, _("No offset")),
            *((str(i), gettext("Offset to {}").format(i)) for i in range(0, 10))
        ]
        for index, bp in enumerate(breakpoints, index + 1):
            field_name = f'column_offset_{bp}'
            attrs[field_name] = ChoiceField(
                label=_("Column offset for {}").format(Breakpoint[bp].label),
                choices=offset_choices,
                required=False,
                help_text=gettext("Move columns to the right using <code>.offset-{}-*</code> classes.").format(bp),
            )
            glossary_fields.insert(index, field_name)

        # define the margin utility fields
        index = glossary_fields.index('margin_utility')
        for index, bp in enumerate(breakpoints, index + 1):
            field_name = f'margin_utility_{bp}'
            attrs[field_name] = ChoiceField(
                label=gettext("Auto Margin for {}").format(Breakpoint[bp].label),
                choices=BootstrapColumnForm.MARGIN_CHOICES,
                required=False,
                help_text=mark_safe(
                    gettext(
                        "Add margin utility <code>.*-{}-auto</code> to force sibling columns away from one another."
                    ).format(bp)
                ),
            )
            glossary_fields.insert(index, field_name)

        attrs['Meta'] = type('Meta', (model_form.Meta,), {
            'fields_map': {'glossary': glossary_fields},
        })
        model_form = type(model_form.__name__, model_form.__mro__, attrs)
        return model_form

    @classmethod
    def get_child_classes(cls, slot, page: Optional[Page] = None, instance: Optional[CMSPlugin] = None, only_uncached: bool = False):
        child_classes = cls.super(BootstrapColumnPlugin, cls).get_child_classes(slot, page, instance, only_uncached)
        return child_classes

plugin_pool.register_plugin(BootstrapColumnPlugin)
