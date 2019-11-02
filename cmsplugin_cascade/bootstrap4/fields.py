from cmsplugin_cascade.bootstrap4.grid import Breakpoint
from cmsplugin_cascade.fields import MultiSizeField


class BootstrapMultiSizeField(MultiSizeField):
    """
    Some size input fields must be specified per Bootstrap breakpoint. Use this multiple
    input field to handle this.
    """
    def __init__(self, *args, **kwargs):
        properties = [bp.name for bp in Breakpoint]
        super().__init__(properties, *args, **kwargs)
