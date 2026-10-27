from types import SimpleNamespace
from unittest.mock import create_autospec

from box_sdk_gen import CreateFileMetadataByIdScope
from box_sdk_gen.managers.file_metadata import FileMetadataManager
from box_sdk_gen.managers.folders import FoldersManager
from box_sdk_gen.schemas.file_full import FileFull
from box_sdk_gen.schemas.folder_full import FolderFull
from box_sdk_gen.schemas.folder_mini import FolderMini
from box_sdk_gen.schemas.items import Items
from box_sdk_gen.schemas.web_link import WebLink

from jwt_sample import apply_metadata, build_sample_metadata, file_url, find_folder_by_path, get_or_create_subfolder


def fake_folders(tree: dict[str, list[FileFull | FolderMini | WebLink]]) -> FoldersManager:
    """folder_id -> 中身 の辞書から、offset ページングする偽 FoldersManager を作る。"""
    folders = create_autospec(FoldersManager, instance=True)

    def get_folder_items(folder_id: str, *, offset: int = 0, limit: int = 100, **_: object) -> Items:
        entries = tree.get(folder_id, [])
        return Items(entries=entries[offset:offset + limit], total_count=len(entries), offset=offset, limit=limit)

    folders.get_folder_items.side_effect = get_folder_items
    return folders


def test_find_folder_by_path() -> None:
    folders = fake_folders({
        '0': [FileFull(id='9', name='a'), FolderMini(id='1', name='a')],
        '1': [FolderMini(id='2', name='b')],
    })
    client = SimpleNamespace(folders=folders)
    assert find_folder_by_path(client, ['a', 'b']) == '2'  # type: ignore[arg-type]
    assert find_folder_by_path(client, ['a', 'x']) is None  # type: ignore[arg-type]


def test_find_folder_by_path_reads_next_pages() -> None:
    noise: list[FileFull | FolderMini | WebLink] = [FolderMini(id=f'n{i}', name=f'noise{i}') for i in range(150)]
    client = SimpleNamespace(folders=fake_folders({'0': [*noise, FolderMini(id='1', name='a')]}))
    assert find_folder_by_path(client, ['a']) == '1'  # type: ignore[arg-type]


def test_get_or_create_subfolder_existing() -> None:
    folders = fake_folders({'1': [FolderMini(id='5', name='サブフォルダ')]})
    client = SimpleNamespace(folders=folders)
    assert get_or_create_subfolder(client, '1', 'サブフォルダ') == '5'  # type: ignore[arg-type]
    folders.create_folder.assert_not_called()  # type: ignore[attr-defined]


def test_get_or_create_subfolder_creates() -> None:
    folders = fake_folders({'1': []})
    folders.create_folder.return_value = FolderFull(id='6', name='サブフォルダ')  # type: ignore[attr-defined]
    client = SimpleNamespace(folders=folders)
    assert get_or_create_subfolder(client, '1', 'サブフォルダ') == '6'  # type: ignore[arg-type]
    name, parent = folders.create_folder.call_args.args  # type: ignore[attr-defined]
    assert (name, parent.id) == ('サブフォルダ', '1')


def test_file_url_is_not_tenant_specific() -> None:
    assert file_url('7') == 'https://app.box.com/file/7'


def test_build_sample_metadata_dates_are_utc() -> None:
    metadata = build_sample_metadata()
    assert metadata['field'] == '2023-08-21T15:00:00.000Z'
    assert metadata['field10'] == '2023-08-22T15:00:00.000Z'


def test_apply_metadata_uses_given_template_key() -> None:
    file_metadata = create_autospec(FileMetadataManager, instance=True)
    client = SimpleNamespace(file_metadata=file_metadata)

    apply_metadata(client, '7', 'myTemplate', {'field1': 'v'})  # type: ignore[arg-type]

    file_metadata.create_file_metadata_by_id.assert_called_once_with(
        '7', CreateFileMetadataByIdScope.ENTERPRISE, 'myTemplate', {'field1': 'v'})
