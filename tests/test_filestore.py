from pathlib import Path, PosixPath
import importlib.resources

import pytest
from html_resources.static import Filestore, FileInfo


HERE = Path(__file__).parent.resolve()
THERE = Path(importlib.resources.files("html_resources") / "testing")
RESOURCES = HERE / "resources"
OTHER_RESOURCES = HERE / "other_resources"


def test_filestore():
    empty = Filestore(RESOURCES)


def test_filestore_add_not_in_tree():
    empty = Filestore(RESOURCES)

    with pytest.raises(ValueError):
        empty.add('/something')

    with pytest.raises(OSError):
        empty.add('something')


def test_filestore_add():
    store = Filestore(RESOURCES)
    info = store.add('sample.json')
    assert info == FileInfo(
        content_type='application/json',
        filepath=RESOURCES / 'sample.json',
        last_modified=1779299331.926828,
        size=434
    )
    assert PosixPath('sample.json') in store.get_store()


def test_filestore_discovery():
    store = Filestore.from_discovery(OTHER_RESOURCES)
    assert dict(store) == {
        PosixPath('img/border.jpg'): FileInfo(
            content_type='image/jpeg',
            filepath=OTHER_RESOURCES / 'img' / 'border.jpg',
            last_modified=1779298176.7173798,
            size=364563,
        ),
        PosixPath('resources/example.css'): FileInfo(
            content_type='text/css',
            filepath=OTHER_RESOURCES / 'resources' / 'example.css',
            last_modified=1779298099.4646437,
            size=38,
        ),
        PosixPath('resources/hello.js'): FileInfo(
            content_type='text/javascript',
            filepath=OTHER_RESOURCES / 'resources' / 'hello.js',
            last_modified=1779297986.238115,
            size=55,
        ),
        PosixPath('docs/user.json'): FileInfo(
            content_type='application/json',
            filepath=OTHER_RESOURCES / 'docs' / 'user.json',
            last_modified=1779298750.9644542,
            size=92,
        ),
        PosixPath('docs/french.txt'): FileInfo(
            content_type='text/plain',
            filepath=OTHER_RESOURCES / 'docs' / 'french.txt',
            last_modified=1779298712.8505802,
            size=39,
        ),
    }


def test_filestore_discovery_restrict():
    store = Filestore.from_discovery(OTHER_RESOURCES, restrict=("*.js",))
    assert dict(store) == {
        PosixPath('resources/hello.js'): FileInfo(
            content_type='text/javascript',
            filepath=OTHER_RESOURCES / 'resources' / 'hello.js',
            last_modified=1779297986.238115,
            size=55,
        )
    }


def test_filestore_package_directory():
    store = Filestore.from_package_directory("html_resources:testing")
    assert dict(store) == {
        PosixPath('whatever.txt'): FileInfo(
            content_type='text/plain',
            filepath=THERE / 'whatever.txt',
            last_modified=1779307220.7250397,
            size=29,
        )
    }
