import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import create_autospec

import pytest
from box_sdk_gen import BoxDeveloperTokenAuth, BoxJWTAuth
from box_sdk_gen.managers.uploads import UploadsManager
from box_sdk_gen.schemas.file_full import FileFull
from box_sdk_gen.schemas.files import Files

from box_common import build_auth, upload_file


def test_developer_token_wins() -> None:
    auth = build_auth({'DEVELOPER_TOKEN': 'dummy-token', 'SETTINGS_FILE_SYS_PATH': 'unused.json'})
    assert isinstance(auth, BoxDeveloperTokenAuth)


def test_jwt_config_file(tmp_path: Path) -> None:
    config = tmp_path / 'config.json'
    config.write_text(json.dumps({
        'boxAppSettings': {
            'clientID': 'dummy-client-id',
            'clientSecret': 'dummy-client-secret',
            'appAuth': {'publicKeyID': 'dummy-key-id', 'privateKey': 'dummy-key', 'passphrase': 'dummy'},
        },
        'enterpriseID': '0',
    }))
    auth = build_auth({'DEVELOPER_TOKEN': '', 'SETTINGS_FILE_SYS_PATH': str(config)})
    assert isinstance(auth, BoxJWTAuth)


def test_missing_settings() -> None:
    with pytest.raises(ValueError, match='DEVELOPER_TOKEN or SETTINGS_FILE_SYS_PATH'):
        build_auth({})


def test_upload_file(tmp_path: Path) -> None:
    png = tmp_path / 'box.png'
    png.write_bytes(b'synthetic')
    uploads = create_autospec(UploadsManager, instance=True)
    uploads.upload_file.return_value = Files(entries=[FileFull(id='7', name='x.png')])
    client = SimpleNamespace(uploads=uploads)

    assert upload_file(client, '5', str(png), 'x.png').id == '7'  # type: ignore[arg-type]
    attributes = uploads.upload_file.call_args.args[0]
    assert (attributes.name, attributes.parent.id) == ('x.png', '5')
