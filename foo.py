from boxsdk import OAuth2, Client
from datetime import datetime, timezone, timedelta


def store_tokens(access_token, refresh_token):
    """
    アクセストークンとリフレッシュトークンを保存するメソッド。
    これらの値は通常、データベースやファイル、または他の永続的なストレージに保存される。
    この例では、シンプルさを保つために、トークンをプリントするだけにしてある。
    """
    print(f'Access Token: {access_token}')
    print(f'Refresh Token: {refresh_token}')


# OAuth2認証オブジェクトの生成
oauth = OAuth2(
    client_id='ここに Client ID',
    client_secret='ここに Client Secret',
    store_tokens=store_tokens
)

# ユーザに認証URLを提示して認証コードを取得
auth_url, csrf_token = oauth.get_authorization_url('http://localhost')
print('Go to this url on your browser: ' + auth_url)

# ユーザが認証した後、リダイレクトURIに付与される認証コードを入力させる
auth_code = input('Enter the auth code: ')

# 認証コードを使ってアクセストークンを取得
# NOTE: ここで上の store_tokens が発火する。
access_token, refresh_token = oauth.authenticate(auth_code)

# Boxクライアントの生成
client = Client(oauth)

# ファイルのアップロード
file_path = './box.png'
folder_id = '0'  # ファイルをアップロードするBoxフォルダーのID。0はルートフォルダーを表す
now_iso = datetime.now(tz=timezone(timedelta(hours=+9), 'JST')).strftime('%Y-%m-%dT%H_%M_%SZ')
file_name = f'box-{now_iso}.png'  # Boxにアップロードした時のファイル名

with open(file_path, 'rb') as file_data:
    box_file = client.folder(folder_id).upload_stream(file_data, file_name)

print(f'File "{box_file.name}" has been uploaded to Box with file ID: {box_file.id}')
