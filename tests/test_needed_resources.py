from pathlib import Path, PosixPath
import importlib.resources

import pytest
from orderedsets import OrderedSet
from html_resources.store import Filestore, FileInfo
from html_resources.library import Library
from html_resources.resources import JSResource, CSSResource, NeededResources


HERE = Path(__file__).parent.resolve()
THERE = Path(importlib.resources.files("html_resources") / "testing")
RESOURCES = HERE / "resources"
OTHER_RESOURCES = HERE / "other_resources"


def test_needed_with_dependency():
    store = Library.from_discovery("my_lib", OTHER_RESOURCES)
    js_resource = store.bind('resources/hello.js')
    assert js_resource == JSResource(
        path=PosixPath('my_lib/resources/hello.js'),
        root=None,
        bottom=False,
        integrity='sha256-yFZn6wscZfgJynmR6A9NFVN6HMNUwHhfE1TrMnJ2HPA=',
        crossorigin=None,
        dependencies=None
    )

    css_resource = store.bind('resources/example.css',
                              dependencies=[js_resource])
    assert css_resource == CSSResource(
        path=PosixPath('my_lib/resources/example.css'),
        root=None,
        bottom=False,
        integrity='sha256-ogCX0ULq8M9SOMyenKNy8HjkPNfr9lNokjg7i09IUBs=',
        crossorigin=None,
        dependencies=(js_resource,)
    )

    needed = NeededResources("/resources")
    needed.add(css_resource)
    assert needed.unfold() == [
        js_resource,
        css_resource,
    ]
