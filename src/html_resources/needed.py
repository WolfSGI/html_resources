from functools import lru_cache
from collections.abc import Hashable, MutableSet, Iterable
from orderedsets import OrderedSet
from .resources import InlineResource, Resource, JSResource, CSSResource


def lineage(resource: Resource | InlineResource):
    if resource.dependencies:
        for dependency in resource.dependencies:
            yield from lineage(dependency)
            yield dependency


@lru_cache(maxsize=100)
def expand_resource(resource: Resource | InlineResource):
    return tuple(lineage(resource))


def expand_resources(resources: Iterable[Resource | InlineResource]):
    seen = set()
    for resource in resources:
        for parent in expand_resource(resource):
            if parent not in seen:
                seen.add(parent)
                yield parent
        if resource not in seen:
            yield resource
    del seen


class NeededResources(Hashable, MutableSet[InlineResource | Resource]):

    __hash__ = MutableSet._hash

    known_extensions = {
        "js": JSResource,
        "css": CSSResource,
    }

    def __init__(self, *args, **kwargs):
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
        return NeededResources(self.data | other)

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

    def unfold(self) -> tuple[Resource | InlineResource, ...]:
        return tuple(expand_resources(self.data))

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
        if factory := self.known_extensions.get(rtype):
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
