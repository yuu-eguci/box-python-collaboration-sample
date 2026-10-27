import pytest
from box_sdk_gen.schemas.metadata_template import (MetadataTemplate, MetadataTemplateFieldsField,
                                                   MetadataTemplateFieldsOptionsField, MetadataTemplateFieldsTypeField)

from jwt_sample_metadata import get_enum_options

TEMPLATE = MetadataTemplate(id='t', template_key='dummyTemplate', fields=[
    MetadataTemplateFieldsField(MetadataTemplateFieldsTypeField.ENUM, 'field1', '帳票区分', options=[
        MetadataTemplateFieldsOptionsField('請求書'), MetadataTemplateFieldsOptionsField('領収書')]),
    MetadataTemplateFieldsField(MetadataTemplateFieldsTypeField.STRING, 'no', '帳票No.'),
])


def test_get_enum_options() -> None:
    assert get_enum_options(TEMPLATE, 'field1') == ['請求書', '領収書']


def test_get_enum_options_not_enum() -> None:
    with pytest.raises(ValueError):
        get_enum_options(TEMPLATE, 'no')


def test_get_enum_options_missing_field() -> None:
    assert get_enum_options(TEMPLATE, 'nope') == []
