from pathlib import PurePosixPath
from .store import Filestore, FileInfo


class StaticAccessor(dict[PurePosixPath, FileInfo]):

    def add(
            self,
            filestore: Filestore,
            prefix: str | PurePosixPath | None = None
    ):
        if prefix:
            prefix = PurePosixPath(prefix)

        if not prefix or not prefix.name:
            self |= filestore.get_store()
        else:
            for uri, info in filestore:
                self[prefix / uri] = info

    def match(self, path: str | PurePosixPath) -> FileInfo:
        path = PurePosixPath(path)
        if (info := self.get(path, None)) is not None:
            return info
        raise KeyError(path)
