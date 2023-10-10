"""
pipenv install boxsdk[jwt]
"""
import os
from boxsdk import OAuth2, JWTAuth, Client
from boxsdk.object.metadata_template import MetadataTemplate, MetadataField, MetadataFieldType

DEVELOPER_TOKEN: str = os.environ['DEVELOPER_TOKEN']
CLIENT_ID: str = os.environ['CLIENT_ID']
CLIENT_SECRET: str = os.environ['CLIENT_SECRET']
ENTERPRISE_ID: str = os.environ['ENTERPRISE_ID']
SETTINGS_FILE_SYS_PATH: str = os.environ['SETTINGS_FILE_SYS_PATH']
METADATA_TEMPLATE_KEY: str = os.environ['METADATA_TEMPLATE_KEY']


def store_tokens_callback(access_token: str, refresh_token: str) -> None:
    print(f'access_token: {access_token}')
    print(f'refresh_token: {refresh_token}')


if DEVELOPER_TOKEN:
    print('OAuth2 使います')
    auth: OAuth2 | JWTAuth = OAuth2(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        access_token=DEVELOPER_TOKEN,
        store_tokens=store_tokens_callback,
    )
else:
    print('JWTAuth 使います')
    auth = JWTAuth.from_settings_file(
        SETTINGS_FILE_SYS_PATH,
        store_tokens=store_tokens_callback,
    )
client: Client = Client(auth)

# メタデータのテンプレートを取得。
template: MetadataTemplate = client.metadata_template('enterprise', METADATA_TEMPLATE_KEY).get()
print(template.fields)  # type: ignore # boxsdk 側の型定義不足のせい。
print(type(template.fields[0]) is not MetadataField)  # type: ignore # boxsdk 側の型定義不足のせい。


def get_options(template: MetadataTemplate, meta_field_key: str) -> list[str]:
    # MetadataField は MetadataTemplate を作るときに使うもの。ゲットするときは無関係。 (わかんねぇ〜)
    field: dict
    for field in template.fields:  # type: ignore # boxsdk 側の型定義不足のせい。
        if field['key'] == meta_field_key:
            if field['type'] != MetadataFieldType.ENUM:
                raise ValueError(f'メタデータテンプレート {METADATA_TEMPLATE_KEY} のフィールド {meta_field_key} は enum ではありません。')
            return [option['key'] for option in field['options']]
    return []


print(get_options(template, 'field1'))
