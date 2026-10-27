from collections.abc import Mapping

from box_sdk_gen import (BoxClient, BoxDeveloperTokenAuth, BoxJWTAuth, JWTConfig, UploadFileAttributes,
                         UploadFileAttributesParentField)
from box_sdk_gen.networking.auth import Authentication
from box_sdk_gen.schemas.file_full import FileFull


def build_auth(env: Mapping[str, str]) -> Authentication:
    """DEVELOPER_TOKEN があればそれを、なければ JWT の設定ファイルを使う。"""
    if env.get('DEVELOPER_TOKEN'):
        print('Developer Token 使います')
        return BoxDeveloperTokenAuth(env['DEVELOPER_TOKEN'])
    if env.get('SETTINGS_FILE_SYS_PATH'):
        print('JWTAuth 使います')
        return BoxJWTAuth(JWTConfig.from_config_file(env['SETTINGS_FILE_SYS_PATH']))
    raise ValueError('Set DEVELOPER_TOKEN or SETTINGS_FILE_SYS_PATH.')


def upload_file(client: BoxClient, folder_id: str, file_path: str, file_name: str) -> FileFull:
    """ID 指定したフォルダの中に、名前を指定してファイルをアップロードする。"""
    attributes = UploadFileAttributes(name=file_name, parent=UploadFileAttributesParentField(id=folder_id))
    with open(file_path, 'rb') as file:
        files = client.uploads.upload_file(attributes, file)
    if not files.entries:
        raise RuntimeError('Box returned no uploaded file.')
    return files.entries[0]
