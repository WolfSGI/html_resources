import base64
import hashlib
import enum
from typing import Sequence
from pathlib import PurePosixPath, Path
from .resources import Resource, JSResource, CSSResource
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
        path = PurePosixPath(path)
        if path.is_absolute():
            uri = self.name / path.relative_to(self.base_path)
        else:
            uri = self.name / path

        if not uri in self._store:
            raise KeyError(f"{uri} does not belong to this library.")

        if not uri.suffix:
            raise NameError("Filename needs an extension.")

        ext = uri.suffix[1:]
        cls = self.known_extensions.get(ext)
        if not cls:
            raise TypeError("Unknown extension.")

        info = self._store[uri]
        if not info.digest:
            hash_base64 = base64.b64encode(
                generate_hash(info.filepath, HashAlgorithm.sha256),
            ).decode("utf-8")
            integrity = f"sha256-{hash_base64}"
            info = self._store[uri] = info._replace(digest=integrity)

        if dependencies is not None:
            dependencies = tuple(dependencies)
        resource = cls(
            uri,
            bottom=bottom,
            integrity=info.digest,
            dependencies=dependencies,
        )
        return resource
