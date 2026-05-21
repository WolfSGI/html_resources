from pathlib import Path, PurePosixPath
import pytest
from html_resources.static import Filestore, FileInfo, StaticAccessor

HERE = Path(__file__).parent.resolve()
RESOURCES = HERE / "resources"
OTHER_RESOURCES = HERE / "other_resources"


def test_accessor():
    empty = StaticAccessor()
    assert len(empty) == 0


def test_accessor_add():
    static = StaticAccessor()
    assert len(static) == 0

    store = Filestore.from_discovery(OTHER_RESOURCES)
    static.add(store)
    assert len(static) == 5
    assert static == store.get_store()

    store = Filestore.from_discovery(RESOURCES)
    static.add(store)
    assert len(static) == 6


def test_accessor_add_duplicate():
    static = StaticAccessor()
    assert len(static) == 0

    store = Filestore.from_discovery(OTHER_RESOURCES)
    static.add(store)
    static.add(store)

    assert len(static) == 5


def test_accessor_add_with_prefix_root():
    static = StaticAccessor()
    assert len(static) == 0

    store = Filestore.from_discovery(RESOURCES)
    static.add(store, prefix="/")
    assert static == store.get_store()

    static.add(store, prefix="/some_prefix")
    assert static == {
        PurePosixPath('sample.json'): FileInfo(
            content_type='application/json',
            filepath=RESOURCES / 'sample.json',
            last_modified=1779299331.926828,
            size=434
        ),
        PurePosixPath('/some_prefix/sample.json'): FileInfo(
            content_type='application/json',
            filepath=RESOURCES / 'sample.json',
            last_modified=1779299331.926828,
            size=434
        )
    }
