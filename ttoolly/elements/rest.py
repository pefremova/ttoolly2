from datetime import date, datetime
from .common import Form as BaseForm


def to_json(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: to_json(v) for k, v in value.items()}
    return value


class Form(BaseForm):
    def get_random_data(self, *args, **kwargs) -> dict:
        params = super().get_random_data(*args, **kwargs)
        return to_json(params)
