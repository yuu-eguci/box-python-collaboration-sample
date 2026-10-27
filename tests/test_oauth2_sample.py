from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, create_autospec

import pytest
from box_sdk_gen import BoxOAuth
from box_sdk_gen.managers.uploads import UploadsManager
from box_sdk_gen.schemas.access_token import AccessToken
from box_sdk_gen.schemas.file_full import FileFull
from box_sdk_gen.schemas.files import Files

from oauth2_sample import authenticate, extract_auth_code, upload_png


def test_extract_auth_code() -> None:
    assert extract_auth_code('http://localhost/?state=dummy-state&code=dummy-code', 'dummy-state') == 'dummy-code'


@pytest.mark.parametrize('url', [
    'http://localhost/?state=other&code=dummy-code',
    'http://localhost/?code=dummy-code',
    'http://localhost/?state=dummy-state',
    'http://localhost/?state=dummy-state&error=access_denied',
    'http://localhost/?state=%E3%81%82&code=dummy-code',
])
def test_extract_auth_code_rejects(url: str) -> None:
    with pytest.raises(ValueError):
        extract_auth_code(url, 'dummy-state')


def fake_oauth() -> Mock:
    oauth = create_autospec(BoxOAuth, instance=True)
    oauth.get_authorize_url.return_value = 'https://account.box.com/api/oauth2/authorize?state=dummy-state'
    oauth.get_tokens_authorization_code_grant.return_value = AccessToken(
        access_token='dummy-access-token', refresh_token='dummy-refresh-token')
    return oauth


def test_authenticate_does_not_print_tokens(capsys: pytest.CaptureFixture[str]) -> None:
    oauth = fake_oauth()
    authenticate(oauth, lambda _: 'http://localhost/?state=dummy-state&code=dummy-code', 'dummy-state')

    oauth.get_tokens_authorization_code_grant.assert_called_once_with('dummy-code')
    out = capsys.readouterr().out
    assert 'state=dummy-state' in out
    assert 'dummy-access-token' not in out
    assert 'dummy-refresh-token' not in out


def test_authenticate_stops_on_state_mismatch() -> None:
    oauth = fake_oauth()
    with pytest.raises(ValueError):
        authenticate(oauth, lambda _: 'http://localhost/?state=evil&code=dummy-code', 'dummy-state')
    oauth.get_tokens_authorization_code_grant.assert_not_called()


def test_upload_png(tmp_path: Path) -> None:
    png = tmp_path / 'box.png'
    png.write_bytes(b'synthetic')
    uploads = create_autospec(UploadsManager, instance=True)
    uploads.upload_file.return_value = Files(entries=[FileFull(id='123', name='uploaded.png')])
    client = SimpleNamespace(uploads=uploads)

    now = datetime(2023, 7, 18, 9, 12, 55, tzinfo=timezone.utc)
    uploaded = upload_png(client, '0', str(png), now)  # type: ignore[arg-type]

    assert uploaded.id == '123'
    attributes = uploads.upload_file.call_args.args[0]
    assert attributes.name == 'box-2023-07-18T18_12_55Z.png'
    assert attributes.parent.id == '0'
