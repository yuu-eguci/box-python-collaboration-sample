import os

from box_sdk_gen import BoxClient, GetMetadataTemplateScope
from box_sdk_gen.schemas.metadata_template import MetadataTemplate, MetadataTemplateFieldsTypeField

from box_common import build_auth


def get_enum_options(template: MetadataTemplate, field_key: str) -> list[str]:
    for field in template.fields or []:
        if field.key == field_key:
            if field.type != MetadataTemplateFieldsTypeField.ENUM:
                raise ValueError(f'メタデータテンプレート {template.template_key} のフィールド {field_key} は enum ではありません。')
            return [option.key for option in field.options or []]
    return []


def main() -> None:
    client = BoxClient(build_auth(os.environ))
    template = client.metadata_templates.get_metadata_template(
        GetMetadataTemplateScope.ENTERPRISE, os.environ['METADATA_TEMPLATE_KEY'])
    print(f'The {template.display_name} template has {len(template.fields or [])} fields')
    print(get_enum_options(template, 'field1'))


if __name__ == '__main__':
    main()
