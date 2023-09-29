from django.template.context import Context
from django.forms.forms import NON_FIELD_ERRORS
import re


def get_keys_from_context(subcontext):
    context_list = [subcontext]
    all_keys = []
    while context_list:
        subcontext = context_list.pop(0)
        for d in getattr(subcontext, "dicts", []) or [subcontext]:
            if isinstance(d, Context):
                context_list.append(d)
            else:
                all_keys.extend(d.keys())
    return all_keys


def get_all_form_errors(response):
    if not response.context:
        return None

    def get_errors(form):
        """simple form"""
        errors = form._errors
        nested_formsets = getattr(form, "nested_formsets", {})
        for fs in nested_formsets:
            errors.update(get_formset_errors(fs))

        if not errors:
            return {}
        if form.prefix:
            if isinstance(errors, list):
                _errors = {}
                for n, el in enumerate(errors):
                    _errors.update(
                        {
                            "%s-%s-%s" % (form.prefix, n, k)
                            if not k.startswith(form.prefix)
                            else k: v
                            for k, v in el.items()
                        }
                    )
            else:
                _errors = {
                    "%s-%s" % (form.prefix, k)
                    if not k.startswith(form.prefix)
                    else k: v
                    for k, v in errors.items()
                }
            errors = _errors

        """form with formsets"""
        form_formsets = getattr(form, "formsets", {})
        if form_formsets:
            for fs_name, fs in form_formsets.items():
                errors.pop("-".join(filter(None, [form.prefix, fs_name])), None)
                errors.update(get_formset_errors(fs))

        return errors

    def get_formset_errors(formset):
        formset_errors = {}
        non_form_errors = formset._non_form_errors
        if non_form_errors:
            formset_errors.update(
                {"-".join([formset.prefix, NON_FIELD_ERRORS]): non_form_errors}
            )
        for form in getattr(formset, "forms", formset):
            if not form:
                continue
            formset_errors.update(get_errors(form))
        return formset_errors

    form_errors = {}
    forms = []
    try:
        forms.append(response.context["wizard"]["form"])
    except KeyError:
        pass
    try:
        forms.append(response.context["form"])
    except KeyError:
        pass
    try:
        forms.extend([form for form in response.context["forms"].values()])
    except AttributeError:
        forms.extend(response.context["forms"])
    except KeyError:
        pass
    try:
        forms.append(response.context["adminform"].form)
    except KeyError:
        pass
    try:
        if response.context_data:
            forms.append(response.context_data["form"])
    except (KeyError, AttributeError):
        pass

    try:
        for fs in response.context["form_set"]:
            non_form_errors = fs._non_field_errors()
            if non_form_errors:
                form_errors.update(
                    {
                        "-".join(
                            [re.sub(r"-(\d+)$", "", fs.prefix), NON_FIELD_ERRORS]
                        ): non_form_errors
                    }
                )
            errors = fs._errors
            if errors:
                form_errors.update(
                    {"%s-%s" % (fs.prefix, key): value for key, value in errors.items()}
                )
    except KeyError:
        pass
    try:
        for fs in response.context["inline_admin_formsets"]:
            non_form_errors = fs.formset._non_form_errors
            if non_form_errors:
                form_errors.update(
                    {"-".join([fs.formset.prefix, NON_FIELD_ERRORS]): non_form_errors}
                )
            errors = fs.formset._errors
            if errors:
                for n, el in enumerate(errors):
                    for key, value in el.items():
                        form_errors.update(
                            {"%s-%d-%s" % (fs.formset.prefix, n, key): value}
                        )
            forms.extend(fs.formset.forms)
    except KeyError:
        pass

    for subcontext in response.context:
        for key in get_keys_from_context(subcontext):
            value = subcontext[key]
            value = value if isinstance(value, list) else [value]
            for v in value:
                mro_names = [cn.__name__ for cn in getattr(v.__class__, "__mro__", [])]
                if "BaseFormSet" in mro_names:
                    form_errors.update(get_formset_errors(v))
                elif "BaseForm" in mro_names:
                    forms.append(v)

    for form in set(forms):
        if form:
            form_errors.update(get_errors(form))

    return form_errors
