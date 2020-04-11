
class PluginExtraFieldsConfig:
    """
    Each Cascade Plugin can be configured to accept extra fields, such as an ID tag, one or more
    CSS classes or inlines styles. It is possible to configure these fields globally using an
    instance of this class, or to configure them on a per site base using the appropriate
    admin's backend interface at:
    ```
    *Start › django CMS Cascade › Custom CSS classes and styles › PluginExtraFields*
    ```
    :param allow_id_tag:
        If ``True``, allows to set the ``id`` attribute in HTML elements.

    :param css_classes:
        A dictionary containing:
          ``class_names`` a comma separated string of allowed class names.
          ``multiple`` a Boolean indicating if more multiple classes are allowed concurrently.

    :param inline_styles:
        A dictionary containing:

    :param allow_override:
        If ``True``, allows to override this configuration using the admin's backend interface.
    """
    def __init__(self, allow_id_tag=False, css_classes=None, inline_styles=None, allow_override=True):
        self.allow_id_tag = allow_id_tag
        self.css_classes = dict(multiple='', class_names='') if css_classes is None else dict(css_classes)
        self.inline_styles = {} if inline_styles is None else dict(inline_styles)
        self.allow_override = allow_override
