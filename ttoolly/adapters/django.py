from ttoolly.adapters.common import Actions as CommonActions
from ttoolly.utils.django import get_all_form_errors


class Actions(CommonActions):
    def get_objects_count(self):
        return self.get_obj_manager.count()

    @property
    def get_obj_manager(self):
        return getattr(self, "model", None)._base_manager

    def prepare_for_add(self):
        pass

    def get_all_form_errors(self, response):
        return get_all_form_errors(response)

    def get_objects_pks(self):
        return self.get_obj_manager.values_list("pk", flat=True)

    def send_add(self, params):
        return self.client.post(self.url_add, params)
