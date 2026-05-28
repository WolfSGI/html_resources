from pathlib import Path, PosixPath
import importlib.resources

import pytest
from orderedsets import OrderedSet
from html_resources.store import Filestore, FileInfo
from html_resources.library import Library
from html_resources.resources import Resource, JSResource, CSSResource
from html_resources.needed import NeededResources, expand_resources


HERE = Path(__file__).parent.resolve()
THERE = Path(importlib.resources.files("html_resources") / "testing")
RESOURCES = HERE / "resources"
OTHER_RESOURCES = HERE / "other_resources"


def test_expand_single():
    resource = Resource(
        path="/whatever"
    )
    expanded = expand_resources([resource])
    assert tuple(expanded) == (resource,)


def test_expand_complex():
    resource1 = Resource(path="/1")
    resource2 = Resource(path="/2", dependencies=(resource1,))
    resource3 = Resource(path="/3", dependencies=(resource2,))
    resource4 = Resource(path="/4", dependencies=(resource2, resource3))

    expanded = expand_resources([resource4, resource2])
    assert tuple(expanded) == (resource1,resource2, resource3, resource4)


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
    assert needed.unfold() == (
        js_resource,
        css_resource,
    )
