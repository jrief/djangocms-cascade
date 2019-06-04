from django.forms.fields import CharField, MultiValueField


class MultipleSizeField(MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = [
            CharField(),
        ]
        super().__init__(fields=fields, *args, **kwargs)

    def compress(self, data_list):
        return data_list