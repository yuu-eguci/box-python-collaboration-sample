import os
import secrets
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

from box_sdk_gen import BoxClient, BoxOAuth, GetAuthorizeUrlOptions, OAuthConfig
from box_sdk_gen.schemas.file_full import FileFull

from box_common import upload_file

REDIRECT_URI = 'http://localhost'
JST = timezone(timedelta(hours=+9), 'JST')


def extract_auth_code(redirected_url: str, expected_state: str) -> str:
    """リダイレクト先の URL から auth code を取り出す。state が違ったら CSRF を疑って止める。"""
    query = parse_qs(urlparse(redirected_url).query)
    if 'error' in query:
        raise ValueError(f'Authorization failed: {query["error"][0]}')
    if not secrets.compare_digest(query.get('state', [''])[0].encode(), expected_state.encode()):
        raise ValueError('state does not match. Paste the whole redirected URL.')
    if 'code' not in query:
        raise ValueError('code not found.')
    return query['code'][0]


def authenticate(oauth: BoxOAuth, read_input: Callable[[str], str], state: str) -> None:
    auth_url = oauth.get_authorize_url(options=GetAuthorizeUrlOptions(redirect_uri=REDIRECT_URI, state=state))
    print(f'Go to this url on your browser: {auth_url}')
    code = extract_auth_code(read_input('Paste the redirected URL: '), state)
    # NOTE: トークンは oauth の token storage (デフォルトはメモリ) に入る。画面には出さない。
    oauth.get_tokens_authorization_code_grant(code)


def upload_png(client: BoxClient, folder_id: str, file_path: str, now: datetime) -> FileFull:
    file_name = f'box-{now.astimezone(JST).strftime("%Y-%m-%dT%H_%M_%SZ")}.png'
    return upload_file(client, folder_id, file_path, file_name)


def main() -> None:
    oauth = BoxOAuth(OAuthConfig(client_id=os.environ['CLIENT_ID'], client_secret=os.environ['CLIENT_SECRET']))
    authenticate(oauth, input, secrets.token_urlsafe(16))
    client = BoxClient(oauth)

    # ルートフォルダ (ID 0) のアイテム一覧
    for item in client.folders.get_folder_items('0').entries or []:
        print(f'{item.type.capitalize()} - {item.name}')

    box_file = upload_png(client, '0', './box.png', datetime.now(tz=JST))
    print(f'File "{box_file.name}" has been uploaded to Box with file ID: {box_file.id}')


if __name__ == '__main__':
    main()
