from functools import lru_cache
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

    def unfold(self) -> tuple[Resource, ...]:
        return tuple(expand_resources(self.data))
