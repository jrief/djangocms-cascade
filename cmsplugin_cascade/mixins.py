from cmsplugin_cascade.models import InlineCascadeElement, SortableInlineCascadeElement


class CascadePluginMixin:
    """
    This is the common mixin class used for both, the :class:`cmsplugin_cascade.plugin_base.CascadePluginBase`
    and the :class:`cmsplugin_cascade.strides.StridePluginBase`.
    """

    @classmethod
    def XXXget_child_classes(cls, slot, page, instance=None, only_uncached=False):
        child_classes = super().get_child_classes(slot, page, instance, only_uncached)
        print(f"{cls.__name__}(id={instance.pk}).get_child_classes: {child_classes}")
        return child_classes

        plugin_type = cls.__name__
        for child_class in cls.get_child_plugin_candidates(slot, page):
            if issubclass(child_class, CascadePluginMixin):
                child_parent_classes = child_class._get_parent_classes_transparent(slot, page, instance)
                if isinstance(child_parent_classes, (list, tuple)) and plugin_type in child_parent_classes:
                    child_classes.add(child_class)
                elif plugin_type in own_child_classes:
                    child_classes.add(child_class)
                elif child_parent_classes is None:
                    child_classes.add(child_class)
            # else:
            #     if cls.alien_child_classes and child_class.__name__ in app_settings.CMSPLUGIN_CASCADE['alien_plugins']:
            #         child_classes.add(child_class)

        return list(cc.__name__ for cc in child_classes)

    @classmethod
    def XXXget_parent_classes(cls, slot, page, instance=None):
        parent_classes = super().get_parent_classes(slot, page, instance)
        print(f"{cls.__name__}.get_parent_classes: {parent_classes}")
        return parent_classes

        if parent_classes is None:
            if cls.get_require_parent(slot, page) is False:
                return
            parent_classes = []
        return parent_classes

    @classmethod
    def get_tag_type(self, instance):
        """
        Return the tag_type used to render this plugin.
        """

        return instance.glossary.get('tag_type', getattr(self, 'tag_type', 'div'))

    @classmethod
    def get_css_classes(cls, instance):
        """
        Returns a list of CSS classes to be added as class="..." to the current HTML tag.
        """

        css_classes = []
        if hasattr(cls, 'default_css_class'):
            css_classes.append(cls.default_css_class)
        default_css_attributes = getattr(cls, 'default_css_attributes', [])
        for attr in default_css_attributes:
            css_class = instance.glossary.get(attr)
            if isinstance(css_class, str):
                css_classes.append(css_class)
            elif isinstance(css_class, list):
                css_classes.extend(css_class)
        return css_classes

    @classmethod
    def get_inline_styles(cls, instance):
        """
        Returns a dictionary of CSS attributes to be added as style="..." to the current HTML tag.
        """

        inline_styles = getattr(cls, 'default_inline_styles', {})
        css_style = instance.glossary.get('inline_styles')
        if css_style:
            inline_styles.update(css_style)
        return inline_styles

    @classmethod
    def get_html_tag_attributes(cls, instance):
        """
        Returns a dictionary of attributes, which shall be added to the current HTML tag.
        This method normally is called by the models's property method ``html_tag_ attributes``,
        which enriches the HTML tag with those attributes converted to a list as
        ``attr1="val1" attr2="val2" ...``.
        """

        attributes = getattr(cls, 'html_tag_attributes', {})
        return dict((attr, instance.glossary.get(key, '')) for key, attr in attributes.items())


class WithInlineElementsMixin:
    """
    Plugins wishing to allow child elements as inlines, shall inherit from this
    mixin class, in order to override the serialize and deserialize methods.
    """
    @classmethod
    def get_data_representation(cls, instance):
        data = super().get_data_representation(instance)
        data.update(inlines=[ie.glossary for ie in instance.inline_elements.all()])
        return data

    @classmethod
    def add_inline_elements(cls, instance, inlines):
        for inline_glossary in inlines:
            InlineCascadeElement.objects.create(
                cascade_element=instance, glossary=inline_glossary)


class WithSortableInlineElementsMixin:
    """
    Plugins wishing to allow child elements as sortable inlines, shall inherit from this
    mixin class, in order to override the serialize and deserialize methods.
    """
    @classmethod
    def get_data_representation(cls, instance):
        data = super().get_data_representation(instance)
        data.update(inlines=[ie.glossary for ie in instance.sortinline_elements.all()])
        return data

    @classmethod
    def add_inline_elements(cls, instance, inlines):
        for order, inline_glossary in enumerate(inlines, 1):
            SortableInlineCascadeElement.objects.create(
                cascade_element=instance,
                glossary=inline_glossary,
                order=order,
            )


class ManageChildrenMixin:
    """
    Classes derived from ``CascadePluginBase`` can optionally add this mixin class to their form,
    offering the input field ``num_children`` in their plugin editor. The content of this field is
    not persisted in the plugin's model.
    It allows the client to modify the number of children attached to this plugin.
    """

    def extend_children(self, parent, wanted_children, child_class, child_glossary=None):
        """
        Extend the number of children so that the parent object contains wanted children.
        No child will be removed if wanted_children is smaller than the current number of children.
        """
        from cms.api import add_plugin

        current_children = parent.get_num_children()
        for _ in range(current_children, wanted_children):
            child = add_plugin(parent.placeholder, child_class, parent.language, target=parent)
            if isinstance(child_glossary, dict):
                child.glossary.update(child_glossary)
            child.save()
