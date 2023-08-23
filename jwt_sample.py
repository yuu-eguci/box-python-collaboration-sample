import os
from boxsdk import OAuth2, JWTAuth, Client
from boxsdk.object.folder import Folder
from boxsdk.object.item import Item
from boxsdk.object.user import User

DEVELOPER_TOKEN: str = os.environ['DEVELOPER_TOKEN']
CLIENT_ID: str = os.environ['CLIENT_ID']
CLIENT_SECRET: str = os.environ['CLIENT_SECRET']
ENTERPRISE_ID: str = os.environ['ENTERPRISE_ID']
SETTINGS_FILE_SYS_PATH: str = os.environ['SETTINGS_FILE_SYS_PATH']


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
    target_folder_items = get_box_folder_by_id(target_folder.id)  # type: ignore # boxsdk 側の型定義不足のせい。
    print(f'Target folder items: {target_folder_items}')
else:
    print('Target folder not found.')


# 3. ID 指定したフォルダの中にフォルダを作る
# 4. ID 指定したフォルダの中に、名前を指定してファイルをアップロード
# 5. ID 指定したファイルの URL を取得
# 6. ID 指定したファイルのメタデータを登録
# 7. ID 指定したファイルのメタデータを更新

# フォルダパスを指定して、その中身。
