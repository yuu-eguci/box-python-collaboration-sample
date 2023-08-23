import os
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from boxsdk import OAuth2, JWTAuth, Client
from boxsdk.object.folder import Folder
from boxsdk.object.item import Item
from boxsdk.object.user import User
from boxsdk.object.metadata_template import MetadataTemplate

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
user: User = client.user().get()
print(f'My User is {user}')

# ルートフォルダと、その中身。
root_folder: Folder = client.root_folder().get()
# NOTE: Folder の親クラスである Item には、name を持つ。
print(f'Root folder: {root_folder}')  # type: ignore # boxsdk 側の型定義不足のせい。
print(f'Root folder items: {list(root_folder.get_items())}')


# 1. フルパス指定したフォルダの存在確認 + ID を得る
def get_box_folder_by_path(folder_names: list) -> Folder | None:
    target_folder: Folder = root_folder
    for folder_name in folder_names:
        found_folder: Folder | None = None
        for item in target_folder.get_items(limit=100, offset=0):
            if item.name == folder_name and item.type == 'folder':
                found_folder = item
                break
        if found_folder is not None:
            target_folder = found_folder
        else:
            return None
    return target_folder


target_folder: Folder | None = get_box_folder_by_path([
    '電子帳簿保存',
    '電子帳簿保存_公開',
    '電子帳簿保存_受領',
])
print(f'Target folder: {target_folder}')


# 2. ID 指定したフォルダの中身を見る
def get_box_folder_by_id(folder_id: str) -> list[Item]:
    items = client.folder(folder_id=folder_id).get_items()
    return list(items)


if target_folder:
    target_folder_items: list[Item] = get_box_folder_by_id(target_folder.id)  # type: ignore # boxsdk 側の型定義不足のせい。
    print(f'Target folder items: {target_folder_items}')
else:
    print('Target folder not found.')


# 3. ID 指定したフォルダの中にサブフォルダを作る
def create_box_subfolder(folder_id: str, subfolder_name: str) -> Folder:
    subfolder = client.folder(folder_id).create_subfolder(subfolder_name)
    return subfolder


def is_box_folder(item: Item) -> bool:
    return type(item) == Folder


subfolder: Folder | None = None
if target_folder:
    target_folder_subfolders: Iterable[Folder] = filter(is_box_folder, target_folder_items)  # type: ignore # ちょっとよくわからん
    for target_folder_item in target_folder_subfolders:
        if target_folder_item.name == 'サブフォルダ':  # type: ignore # boxsdk 側の型定義不足のせい。
            subfolder = target_folder_item
            break
    if subfolder is None:
        subfolder = create_box_subfolder(target_folder.id, 'サブフォルダ')  # type: ignore # boxsdk 側の型定義不足のせい。
    print(f'Subfolder: {subfolder}')
else:
    print('Target folder not found.')


# 4. ID 指定したフォルダの中に、名前を指定してファイルをアップロード
def upload_file_to_box(folder_id: str, file_path: str, file_name: str) -> Item:
    new_file = client.folder(folder_id).upload(file_path, file_name)
    return new_file


new_file: Item | None = None
JST = timezone(timedelta(hours=+9), 'JST')
current_jst: str = datetime.now(tz=JST).strftime('%Y%m%d_%H%M%S')
if subfolder:
    new_file: Item = upload_file_to_box(subfolder.id,  # type: ignore # boxsdk 側の型定義不足のせい。
                                        './box.png', f'box_logo_{current_jst}.png')
    print(f'New file: {new_file}')
else:
    print('Subfolder not found.')


# 5. ID 指定したファイルの URL を取得
def get_box_file_url(file_id: str) -> str:
    return f'https://yuu-eguci.box.com/file/{file_id}'


if new_file:
    new_file_url = get_box_file_url(new_file.id)  # type: ignore # boxsdk 側の型定義不足のせい。
    print(f'New file URL: {new_file_url}')
else:
    print('New file not found.')


# 6.0. メタデータのテンプレートを取得
template: MetadataTemplate = client.metadata_template('enterprise', METADATA_TEMPLATE_KEY).get()
print(f'The {template.displayName} template has {len(template.fields)} fields')  # type: ignore # boxsdk 側の型定義不足のせい。


# 6.1. ID 指定したファイルのメタデータを登録
JST = timezone(timedelta(hours=+9), 'JST')
metadata = {
    'field': datetime(2023, 8, 22, tzinfo=JST).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
    'field1': '帳票区分の値',
    'no': '帳票No.の値',
    'field2': '登録事業者番号の値',
    'field3': '取引先コードの値',
    'field4': '取引先名称の値',
    'field5': 12345.67,
    'field6': 8.0,
    'field7': 987.65,
    'field8': '部署コードの値',
    'field9': '部署名の値',
    'field10': datetime(2023, 8, 23, tzinfo=JST).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
    'field11': '社員番号の値',
    'url': 'https://example.com'
}
if new_file:
    applied_metadata = new_file.metadata(scope='enterprise', template='template').set(metadata)
    print(applied_metadata)
else:
    print('New file not found.')

# 7. ID 指定したファイルのメタデータを更新
# いや、更新は不要そう。
