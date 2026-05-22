from pathlib import PurePosixPath
from .store import Filestore, FileInfo


class StaticAccessor(dict[PurePosixPath, FileInfo]):

    def add(self, filestore: Filestore):
        self |= filestore

    def match(self, path: str | PurePosixPath) -> FileInfo:
        path = PurePosixPath(path)
        if (info := self.get(path, None)) is not None:
            return info
        raise KeyError(path)
