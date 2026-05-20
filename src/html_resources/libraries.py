import os
import base64
import hashlib
import enum
import importlib.resources
from typing import Sequence, Iterable
from pathlib import PurePosixPath, Path
from mimetypes import guess_type
from autoroutes import Routes


class HashAlgorithm(enum.Enum):
    sha256 = hashlib.sha256
    sha384 = hashlib.sha384
    sha512 = hashlib.sha512


def generate_hash(filepath: Path, algorithm: HashAlgorithm) -> str:
    hashed = algorithm.value()
    with filepath.open("rb") as f:
        while True:
            data = f.read(1024 * 32)
            if not data:
                break
            hashed.update(data)
    return hashed.digest()


class Library(dict[Path, Path]):
    name: str
    base_path: Path

    def __init__(self, name: str, base_path: str | Path):
        resource = Path(base_path)
        if not resource.exists():
            raise OSError(f"{resource} does not exist.")
        if not resource.is_dir():
            raise TypeError("Library base path must be a directory.")
        if not base_path.is_absolute():
            raise ValueError("Base path needs to be absolute.")
        self.name = name
        self.base_path = base_path

    def bind(
        self,
        path: str | PurePosixPath,
        *,
        name: str | None = None,
        bottom: bool = False,
        dependencies: Sequence[Resource] | None = None,
    ):
        fullpath = self.base_path / path
        if not fullpath.is_file():
            raise TypeError(f"{path} is not a file.")

        if not fullpath.suffix:
            raise NameError("Filename needs an extension.")

        ext = fullpath.suffix[1:]
        cls = known_extensions.get(ext)
        if not cls:
            raise TypeError("Unknown extension.")

        hash_base64 = base64.b64encode(
            generate_hash(fullpath, HashAlgorithm.sha256),
        ).decode("utf-8")
        integrity = f"sha256-{hash_base64}"

        if dependencies is not None:
            dependencies = tuple(dependencies)
        resource = cls(
            f"/{self.name}/{path}",
            bottom=bottom,
            integrity=integrity,
            dependencies=dependencies,
        )
        self._resources.add(resource)
        return resource

    def discover(self, restrict=("*",)):
        for matcher in restrict:
            for path in self.base_path.rglob(matcher):
                self.bind(path.relative_to(self.base_path))

    @classmethod
    def from_discovery(
            cls, name: str, base_path: str | Path, restrict=("*",)):
        library = cls(name, base_path)
        library.discover(restrict=restrict)
        return library

    @classmethod
    def from_package_static(cls, package_static: str, restrict=("*",)):
        """Creates a Library object from a package_static string.
        package_static of form:  package_name:path
        """
        pkg, _, resource_name = package_static.partition(':')
        resource = Path(
            importlib.resources.files(pkg) / resource_name
        )
        return cls.from_discovery(
            package_static,
            resource,
            restrict=restrict
        )



class Library(BaseLibrary):
    _resources: set[Resource]

    def __init__(self, name: str, base_path: str | Path):
        self._resources = set()
        super().__init__(name, base_path)

    def __iter__(self):
        for resource in self._resources:
            yield self.name / path.relative_to(self.base_path), source.path




class StaticAccessor(Routes):
