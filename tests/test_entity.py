import pytest
import inspect
from tests.fixtures import entity_fixture


def test_entity_schema_documentation(entity_fixture):
    entity, url = entity_fixture
    assert entity.__schema__.mock_me(ent_url=url)


def test_entity_model_defines_schema_fields(entity_fixture):
    entity, _ = entity_fixture

    schema_fields = set(list(entity.__schema__.model_fields.keys()))
    schema_field_info = entity.__schema__.model_fields
    funcs = set([i for i, f in inspect.getmembers(entity)])

    for diff in schema_fields.difference(funcs):
        field_info = schema_field_info[diff]
        assert hasattr(field_info, "default")
