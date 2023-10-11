# ttoolly2
[![codecov](https://codecov.io/github/pefremova/ttoolly2/graph/badge.svg?token=KAOH672HZM)](https://codecov.io/github/pefremova/ttoolly2)


# About
ttoolly provides tests generation based on form and fields params. 
There are two main ways how to use it: 
1. [generate tests code](#generate-test-cases)
2. [run tests directly](#create-test)

# Getting started

For example we have a functinality of creating a product with two attributes: name and count

### Generate form description template
Generate template for field "name" with type str and field "count" with type int:
```
tt_get_field_template name:str count:int
```
The result:
```
{'count': {'lt': [],
           'lte': [],
           'max_value': 9223372036854775807,
           'min_value': -9223372036854775808,
           'not_empty': False,
           'only': None,
           'required': False,
           'step': 1,
           'type': 'int',
           'unique': False},
 'name': {'max_length': None,
          'min_length': 0,
          'not_empty': False,
          'null_allowed': True,
          'only': None,
          'required': False,
          'str_format': None,
          'type': 'str',
          'unique': False}}
```

### Create form description based on template
We can left only valuable attributes
```
form_data = {'fields':
    {'count': {'max_value': 1000,
           'min_value': 0,
           'not_empty': True,
           'required': True,
           'type': 'int'},
'name': {'max_length': 500,
          'not_empty': True,
          'required': True,
          'type': 'str'}}}
```

### Create test
This example uses pytest
```
from ttoolly.adapters.pytest import Actions
from ttoolly.generator import TestCaseMeta
from ttoolly.testcases import CasesAdd

class TestPytest(Actions, metaclass=TestCaseMeta):
    cases = [
        CasesAdd,
    ]
    form = Form(**form_data)
    
    def send_add(self, params: dict):
        <...>
    
    def get_objects_count(self):
        <...>

    def get_objects_pks(self):
        <...>

    def get_all_form_errors(self, response):
        <...>

    def prepare_for_add(self, **kwargs):
        <...>
```

These methods must be defined in the test class:
1. ```send_add``` - should send data to the create object endpoint, return response
2. ```get_objects_count``` - should return count of existing objects
3. ```get_objects_pks``` - should return a list of identificators of existing objects
4. ```get_all_form_errors``` - should parse and return errors from the response
5. ```prepare_for_add``` - should contains any preparation actions, like remove old objects, authorize user, etc.

If create tests for a Django project, use ```from ttoolly.adapters.django import Actions``` for Django TestCase  or ```from ttoolly.adapters.django_pytest import Actions``` for pytest, where most of these methods already defined.

Run tests as usual:
```pytest tests.py```

### Generate test cases
If you prefer more explicit result, you might want to use test code generation:
```tt_generate_cases form_description.json```

The output will contain code:
```
def test_add_all_filled_0_count_name(self):
    kwargs = {}
    fields = ('count', 'name')
    self.prepare_for_add(**kwargs)
    params = {'count': 588, 'name': 'TvGomekHwcTvGomekHwcTvGomekHwczsAjEvn'}
    snapshot = self.take_snapshot()
    response = self.send_add(params, **kwargs)
    self.check_success_add(response, snapshot)


def test_add_without_not_required_0_name_count(self):
    kwargs = {}
    additional = {}
    fields = ('name', 'count')
    self.prepare_for_add(**kwargs)
    params = {'count': 248, 'name': 'DGtbxEpStFDGtbxEpStFDGtbxEpStFDGtbxEpStF'}
    snapshot = self.take_snapshot()
    response = self.send_add(params, **kwargs)
    self.check_success_add(response, snapshot)
```
Note that in this case tests contain hardcoded input data for form.

More human readable output also available with parameter ```--humanable```:
```
NAME: All possible fields are filled

DETAILS: Send create request with filled fields:
* count
* name

RESULT: Object should be created successfully


NAME: Non required fields are not filled

DETAILS: Send create request with
# fields filled with any correct data:
* count
* name

RESULT: Object should be created successfully
```


### More examples
[Django](test_projects/django_project/tests/tests.py)

[Fast api](test_projects/fast_api_project/tests/tests.py)

