from ttoolly.elements.common import Form, FieldStr


class FormDjango(Form):
    _form_type = "django"
    pass


class FieldStr(FieldStr):
    _form_type = "django"

    def __init__(self, **kwargs):
        if kwargs.get('str_format'):
            str_format = kwargs['str_format']
            if not isinstance(str_format, dict) and not kwargs.get('min_length'):
                kwargs['min_length'] = {"email": 6, "email_simple": 6}.get(
                    str_format, 0
                )
        super().__init__(**kwargs)
