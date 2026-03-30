from formset.renderers.admin import FormRenderer


class CascadeFormRenderer(FormRenderer):
    def _amend_form(self, context):
        super()._amend_form(context)
        context['field_group_template'] = 'admin/cmsplugin_cascade/formset/field_group.html'
        return context

    _context_modifiers = dict(FormRenderer._context_modifiers, **{
        'django/forms/div.html': _amend_form,
    })
