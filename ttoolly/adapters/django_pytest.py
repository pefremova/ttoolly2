from ttoolly.adapters.django import Actions as DjangoActions


class Actions(DjangoActions):
    def prepare_for_add(self, **kwargs):
        pass

    def send_add(self, params, **kwargs):
        return kwargs["client"].post(self.url_add, params)
