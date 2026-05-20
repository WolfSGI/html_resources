import os
import base64
import hashlib
import enum
import importlib.resources
from typing import Sequence, Mapping, NamedTuple
from pathlib import PurePosixPath, Path
from mimetypes import guess_type
from types import MappingProxyType


class HashAlgorithm(enum.Enum):
    sha256 = hashlib.sha256
    sha384 = hashlib.sha384
    sha512 = hashlib.sha512


class FileInfo(NamedTuple):
    filepath: Path
    size: int
    last_modified: float
    content_type: str


def generate_hash(filepath: Path, algorithm: HashAlgorithm) -> str:
    hashed = algorithm.value()
    with filepath.open("rb") as f:
        while True:
            data = f.read(1024 * 32)
            if not data:
                break
            hashed.update(data)
    return hashed.digest()


class Filestore:
    base_path: Path
    _store: dict[Path, FileInfo]

    def __init__(self, base_path: str | Path, *args, **kwargs):
        directory = Path(base_path)
        if not directory.exists():
            raise OSError(f"{directory} does not exist.")
        if not directory.is_dir():
            raise TypeError("Library base path must be a directory.")
        if not base_path.is_absolute():
            raise ValueError("Base path needs to be absolute.")
        self.base_path = directory
        self._store = dict()
        super().__init__(*args, **kwargs)

    def __getitem__(self, path: str | Path):
        path = Path(path)
        return self._store.get(path)

    def __len__(self):
        return len(self._store)

    def __iter__(self):
        yield from self._store.items()

    def add(self, path: Path | str):
        path = Path(path)
        if path.is_absolute():
            full_path = path
            uri = full_path.relative_to(self.base_path)
        else:
            full_path = self.base_path / path
            uri = path

        if not full_path.exists():
            raise OSError(f"{full_path} does not exist.")
        if full_path.is_dir():
            raise TypeError("Filestore can only contain files.")
        stats = os.stat(full_path)
        content_type, encoding = guess_type(full_path)
        if not content_type:
            content_type = "octet/steam"
        info = FileInfo(
            filepath=full_path,
            size=stats.st_size,
            last_modified=stats.st_mtime,
            content_type=content_type,
        )
        self._store[uri] = info
        return info

    def get_store(self) -> Mapping[PurePosixPath, Path]:
        return MappingProxyType(self._store)

    @classmethod
    def from_discovery(cls, base_path: str | Path, restrict=("*",)):
        store = cls(base_path)
        for matcher in restrict:
            for path in store.base_path.rglob(matcher):
                if not path.is_dir():
                    store.add(path)
        return store

    @classmethod
    def from_package_directory(cls, package_dir: str, restrict=("*",)):
        # package_dir of form:  package_name:path
        pkg, resource_name = package_dir.split(":")
        resource = Path(
            importlib.resources.files(pkg) / resource_name
        )
        return cls.from_discovery(resource, restrict=restrict)


class StaticAccessor(dict[Path, FileInfo]):

    def add(self, filestore: Filestore, prefix=None):
        if not prefix:
            self |= filestore.get_store()
        else:
            for uri, info in filestore:
                self[prefix / uri] = info

    def match(self, path: str | Path) -> FileInfo:
        path = PurePosixPath(path)
        if (info := self.get(path, None)) is not None:
            return info
        raise KeyError(path)
