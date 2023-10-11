from ttoolly.elements.common import Form, FieldStr


class FormDjango(Form):
    _form_type = "django"
    pass


class FieldStr(FieldStr):
    _form_type = "django"

    def __init__(self, **kwargs):
        if not isinstance(self.str_format, dict) and not self.min_length:
            self.min_length = {"email": 6, "email_simple": 6}.get(self.str_format, 0)
        super().__init__(**kwargs)
