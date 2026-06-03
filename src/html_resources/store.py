import os
import importlib.resources
from typing import Mapping, NamedTuple
from pathlib import PurePosixPath, Path
from mimetypes import guess_type
from types import MappingProxyType


class FileInfo(NamedTuple):
    filepath: Path
    size: int
    last_modified: float
    content_type: str
    digest: str | None = None


class Filestore:
    name: PurePosixPath
    base_path: Path
    _store: dict[PurePosixPath, FileInfo]

    def __init__(self, name: str | PurePosixPath, base_path: str | Path):
        directory = Path(base_path)
        if not directory.exists():
            raise OSError(f"{directory} does not exist.")
        if not directory.is_dir():
            raise TypeError("Library base path must be a directory.")
        if not base_path.is_absolute():
            raise ValueError("Base path needs to be absolute.")
        self.name = PurePosixPath(name)
        self.base_path = directory
        self._store = dict()

    @property
    def store(self) -> Mapping[PurePosixPath, Path]:
        return MappingProxyType(self._store)

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
        self._store[self.name / uri] = info
        return info

    @classmethod
    def from_discovery(
            cls,
            name: str | PurePosixPath,
            base_path: str | Path,
            restrict=("*",)
    ):
        store = cls(name, base_path)
        for matcher in restrict:
            for path in store.base_path.rglob(matcher):
                if not path.is_dir():
                    store.add(path)
        return store

    @classmethod
    def from_package_directory(
            cls,
            name: str | PurePosixPath,
            package_dir: str,
            restrict=("*",)
    ):
        # package_dir of form:  package_name:path
        pkg, resource_name = package_dir.split(":")
        resource = Path(
            importlib.resources.files(pkg) / resource_name
        )
        return cls.from_discovery(name, resource, restrict=restrict)


class Repository(dict[PurePosixPath, FileInfo]):

    def add(self, filestore: Filestore):
        self |= filestore

    def match(self, path: str | PurePosixPath) -> FileInfo:
        path = PurePosixPath(path)
        if (info := self.get(path, None)) is not None:
            return info
        raise KeyError(path)
