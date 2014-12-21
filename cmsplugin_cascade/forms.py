# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from cmsplugin_cascade.models import CascadeElement


class ManageChildrenFormMixin(object):
    """
    Classes derived from ``CascadePluginBase`` may optionally declare a class derived from
    ``forms.models.ModelForm`` offering one or more temporary input fields in their plugin
    editor, which are not managed by the plugin's model.
    This FormMixin handles one such a field, namely the number of child plugins.
    It allows the client to modify the number of children attached to this plugin.
    """
    class Meta:
        model = CascadeElement
        fields = ('glossary',)

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = {'num_children': instance.get_children().count()}
            kwargs.update(initial=initial)
        super(ManageChildrenFormMixin, self).__init__(*args, **kwargs)
