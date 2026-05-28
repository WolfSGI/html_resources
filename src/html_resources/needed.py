from functools import lru_cache
from pathlib import PurePosixPath
from collections.abc import Hashable, MutableSet, Iterable
from orderedsets import OrderedSet
from html_resources.resources import Resource


@lru_cache(maxsize=100)
def lineage(resource: Resource):
    if resource.dependencies:
        for dependency in resource.dependencies:
            yield from lineage(dependency)
            yield dependency


def expand_resources(resources: Iterable[Resource]):
    seen = set()
    for resource in resources:
        for parent in lineage(resource):
            if parent not in seen:
                seen.add(parent)
                yield parent
        if resource not in seen:
            yield resource
    del seen


class NeededResources(Hashable, MutableSet[Resource]):

    __hash__ = MutableSet._hash

    def __init__(self, root: str | PurePosixPath, *args, **kwargs):
        self.root = root
        self.data = OrderedSet(*args, **kwargs)

    def __contains__(self, value):
        return value in self.data

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return repr(self.data)

    def __or__(self, other: set):
        return NeededResources(self.root, self.data | other)

    def __ior__(self, other: set):
        self.data |= other
        return self

    def add(self, value):
        self.data.add(value)

    def discard(self, value):
        self.data.discard(value)

    def update(self, other: set):
        self.data.update(other)

    def precede(self, other: set):
        self.data = OrderedSet((*other, *self.data))
        return self

    def add_resource(
        self,
        path: str,
        rtype: str,
        *,
        root: str | None = None,
        bottom: bool = False,
        integrity: str | None = None,
        crossorigin: str | None = None,
    ):
        if factory := known_extensions.get(rtype):
            resource = factory(
                path,
                root=root,
                bottom=bottom,
                integrity=integrity,
                crossorigin=crossorigin,
            )
            self.add(resource)
        else:
            raise KeyError(f"Unknown resource type: {rtype}.")

    def unfold(self) -> tuple[Resource, ...]:
        return tuple(expand_resources(self.data))

    def apply(self, body: str | bytes, application_uri: str = "") -> bytes:
        if len(self) == 0:
            return body

        if isinstance(body, str):
            body = body.encode()

        top = b""
        bottom = b""
        base_uri = multi_urljoin(application_uri, self.root)
        for resource in self.unfold():
            if resource.bottom:
                bottom += resource.render(base_uri)
            else:
                top += resource.render(base_uri)
        if top:
            body = body.replace(b"</head>", top + b"</head>", 1)
        if bottom:
            body = body.replace(b"</body>", bottom + b"</body>", 1)
        return body
