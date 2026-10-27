import os
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone

from box_sdk_gen import BoxClient, CreateFileMetadataByIdScope, CreateFolderParent
from box_sdk_gen.schemas.file_full import FileFull
from box_sdk_gen.schemas.folder_mini import FolderMini
from box_sdk_gen.schemas.web_link import WebLink

from box_common import build_auth, upload_file

JST = timezone(timedelta(hours=+9), 'JST')
TARGET_FOLDER_PATH = ['電子帳簿保存', '電子帳簿保存_公開', '電子帳簿保存_受領']
SUBFOLDER_NAME = 'サブフォルダ'
PAGE_SIZE = 100


# 1. フルパス指定したフォルダの存在確認 + ID を得る
def find_folder_by_path(client: BoxClient, folder_names: list[str]) -> str | None:
    folder_id = '0'  # ルートフォルダ
    for name in folder_names:
        found = find_subfolder(client, folder_id, name)
        if found is None:
            return None
        folder_id = found
    return folder_id


# 2. ID 指定したフォルダの中身を見る (全ページ)
def iter_folder_items(client: BoxClient, folder_id: str) -> Iterator[FileFull | FolderMini | WebLink]:
    offset = 0
    while True:
        page = client.folders.get_folder_items(folder_id, offset=offset, limit=PAGE_SIZE)
        entries = page.entries or []
        yield from entries
        offset += len(entries)
        if not entries or offset >= (page.total_count or 0):
            return


def find_subfolder(client: BoxClient, folder_id: str, name: str) -> str | None:
    for item in iter_folder_items(client, folder_id):
        if item.type == 'folder' and item.name == name:
            return item.id
    return None


# 3. ID 指定したフォルダの中にサブフォルダを作る (もうあればそれを使う)
def get_or_create_subfolder(client: BoxClient, parent_id: str, name: str) -> str:
    return find_subfolder(client, parent_id, name) or client.folders.create_folder(
        name, CreateFolderParent(id=parent_id)).id


# 5. ID 指定したファイルの URL を取得
def file_url(file_id: str) -> str:
    return f'https://app.box.com/file/{file_id}'


def to_box_datetime(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')


# 6. メタデータの値。フィールドのキーは自分のテンプレートに合わせて書き換える。
def build_sample_metadata() -> dict[str, str | float]:
    return {
        'field': to_box_datetime(datetime(2023, 8, 22, tzinfo=JST)),
        'field1': '帳票区分の値',
        'no': '帳票No.の値',
        'field2': '登録事業者番号の値',
        'field3': '取引先コードの値',
        'field4': '取引先名称の値',
        'field5': 12345.67,
        'field12': '8%',
        'field7': 987.65,
        'field8': '部署コードの値',
        'field9': '部署名の値',
        'field10': to_box_datetime(datetime(2023, 8, 23, tzinfo=JST)),
        'field11': '社員番号の値',
        'url': 'https://example.com',
    }


# 6.1. ID 指定したファイルのメタデータを登録
def apply_metadata(client: BoxClient, file_id: str, template_key: str, metadata: dict[str, str | float]) -> None:
    client.file_metadata.create_file_metadata_by_id(
        file_id, CreateFileMetadataByIdScope.ENTERPRISE, template_key, metadata)


def main() -> None:
    client = BoxClient(build_auth(os.environ))
    print(f'My User is {client.users.get_user_me().name}')

    folder_id = find_folder_by_path(client, TARGET_FOLDER_PATH)
    if folder_id is None:
        print('Target folder not found.')
        return

    subfolder_id = get_or_create_subfolder(client, folder_id, SUBFOLDER_NAME)
    new_file = upload_file(client, subfolder_id, './box.png', f'box_logo_{datetime.now(tz=JST):%Y%m%d_%H%M%S}.png')
    print(f'New file URL: {file_url(new_file.id)}')

    apply_metadata(client, new_file.id, os.environ['METADATA_TEMPLATE_KEY'], build_sample_metadata())
    print('Metadata applied.')


if __name__ == '__main__':
    main()
