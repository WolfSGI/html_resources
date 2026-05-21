import os
import base64
import hashlib
import enum
import importlib.resources
from typing import Sequence, Iterable
from pathlib import PurePosixPath, Path
from mimetypes import guess_type
from .resources import Resource
from .store import Filestore


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


class Library(Filestore):

    known_extensions = {
        "js": JSResource,
        "css": CSSResource,
    }

    def bind(
        self,
        path: str | PurePosixPath,
        *,
        name: str | None = None,
        bottom: bool = False,
        dependencies: Sequence[Resource] | None = None,
    ) -> Resource:
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
        return resource
