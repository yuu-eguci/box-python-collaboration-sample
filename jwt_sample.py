import os
from boxsdk import OAuth2, JWTAuth, Client
from boxsdk.object.folder import Folder

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
service_account = client.user().get()
print(f'Service Account user is {service_account}')

# ルートフォルダと、その中身。
root_folder: Folder = client.root_folder().get()
# NOTE: Folder の親クラスである Item には、name を持つ。
print(f'Root folder: {root_folder.name}')  # type: ignore # boxsdk 側の型定義不足のせい。
print(f'Root folder items: {list(root_folder.get_items())}')

# フォルダパスを指定して、その中身。
folder_names = [
    '電子帳簿保存',
    '電子帳簿保存_公開',
    '電子帳簿保存_受領',
]
target_folder: Folder = root_folder

for folder_name in folder_names:
    found_folder: Folder | None = None
    print(f"Target folder: {target_folder}")
    for item in target_folder.get_items(limit=100, offset=0):
        if item.name == folder_name and item.type == 'folder':
            found_folder = item
            print(f"Found folder {folder_name}!")
            break
    if found_folder is not None:
        target_folder = found_folder
    else:
        print(f"Folder {folder_name} not found!")
        break

if target_folder:
    print(f"Target folder: {target_folder}")
else:
    print("Could not find the target folder.")
