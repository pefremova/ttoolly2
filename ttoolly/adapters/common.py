from ttoolly.asserts.common import (
    assert_status_code,
    assert_objects_count,
    assert_no_form_errors,
)


class Actions:
    status_code_add_success = 200

    def prepare_for_add(self) -> None:
        raise NotImplementedError

    def take_snapshot(self) -> dict:
        initial_count = self.get_objects_count()
        old_pks = list(self.get_objects_pks())
        return locals()

    def send_add(self, params: dict):
        raise NotImplementedError

    def check_success_add(self, response, snapshot):
        assert_no_form_errors(form_errors=self.get_all_form_errors(response))
        assert_status_code(response.status_code, self.status_code_add_success)
        assert_objects_count(
            self.get_objects_count(),
            snapshot["initial_count"],
            1,
            "After successful creating",
        )

    def get_objects_count(self):
        raise NotImplemented

    def get_objects_pks(self):
        raise NotImplemented

    def get_all_form_errors(self, response):
        raise NotImplemented
