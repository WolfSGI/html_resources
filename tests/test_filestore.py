from pathlib import Path, PurePosixPath
import importlib.resources

import pytest
from html_resources.store import Filestore, FileInfo


HERE = Path(__file__).parent.resolve()
THERE = Path(importlib.resources.files("html_resources") / "testing")
RESOURCES = HERE / "resources"
OTHER_RESOURCES = HERE / "other_resources"


def test_filestore():
    empty = Filestore('/test', RESOURCES)


def test_filestore_add_not_in_tree():
    empty = Filestore('/test', RESOURCES)

    with pytest.raises(ValueError):
        empty.add('/something')

    with pytest.raises(OSError):
        empty.add('something')


def test_filestore_add():
    store = Filestore('/test', RESOURCES)
    info = store.add('sample.json')
    assert info == FileInfo(
        content_type='application/json',
        filepath=RESOURCES / 'sample.json',
        last_modified=1779299331.926828,
        size=434
    )
    assert PurePosixPath('/test/sample.json') in store.store


def test_filestore_discovery():
    store = Filestore.from_discovery('/test', OTHER_RESOURCES)
    assert dict(store) == {
        PurePosixPath('/test/img/border.jpg'): FileInfo(
            content_type='image/jpeg',
            filepath=OTHER_RESOURCES / 'img' / 'border.jpg',
            last_modified=1779298176.7173798,
            size=364563,
        ),
        PurePosixPath('/test/resources/example.css'): FileInfo(
            content_type='text/css',
            filepath=OTHER_RESOURCES / 'resources' / 'example.css',
            last_modified=1779298099.4646437,
            size=38,
        ),
        PurePosixPath('/test/resources/hello.js'): FileInfo(
            content_type='text/javascript',
            filepath=OTHER_RESOURCES / 'resources' / 'hello.js',
            last_modified=1779297986.238115,
            size=55,
        ),
        PurePosixPath('/test/docs/user.json'): FileInfo(
            content_type='application/json',
            filepath=OTHER_RESOURCES / 'docs' / 'user.json',
            last_modified=1779298750.9644542,
            size=92,
        ),
        PurePosixPath('/test/docs/french.txt'): FileInfo(
            content_type='text/plain',
            filepath=OTHER_RESOURCES / 'docs' / 'french.txt',
            last_modified=1779298712.8505802,
            size=39,
        ),
    }


def test_filestore_discovery_restrict():
    store = Filestore.from_discovery('/test', OTHER_RESOURCES, restrict=("*.js",))
    assert dict(store) == {
        PurePosixPath('/test/resources/hello.js'): FileInfo(
            content_type='text/javascript',
            filepath=OTHER_RESOURCES / 'resources' / 'hello.js',
            last_modified=1779297986.238115,
            size=55,
        )
    }


def test_filestore_package_directory():
    store = Filestore.from_package_directory('/test', "html_resources:testing")
    assert dict(store) == {
        PurePosixPath('/test/whatever.txt'): FileInfo(
            content_type='text/plain',
            filepath=THERE / 'whatever.txt',
            last_modified=1779307220.7250397,
            size=29,
        )
    }
