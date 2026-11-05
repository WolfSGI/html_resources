from dataclasses import dataclass
from typing import NamedTuple, Union
from pathlib import PurePosixPath
from functools import cached_property
from .store import FileInfo


def multi_urljoin(*parts):
    return "/".join(str(part).strip("/") for part in parts if part)


@dataclass(frozen=True)
class InlineResource:
    code: str
    bottom: bool = False
    dependencies: tuple[Union["Resource", "InlineResource"]] | None = None
    fileinfo: FileInfo | None = None

    def render(self, application_uri) -> bytes:
        pass


@dataclass(frozen=True)
class InlineCSSResource(InlineResource):
    type: str = "text/css"

    def render(self, application_uri) -> bytes:
        return f"""<style type="{self.type}">{self.code}</style>\n""".encode()


@dataclass(frozen=True)
class InlineJSResource(InlineResource):
    type: str = "text/javascript"

    def render(self, application_uri) -> bytes:
        return f"""<script type="{self.type}">{self.code}</script>\n""".encode()


@dataclass(frozen=True)
class Resource:
    path: str | PurePosixPath | None = None
    root: str | None = None
    code: str | None = None
    integrity: str | None = None
    crossorigin: str | None = None
    bottom: bool = False
    dependencies: tuple["Resource"] | None = None
    fileinfo: FileInfo | None = None

    @property
    def inline(self):
        return None

    def render(self, application_uri) -> bytes:
        pass


@dataclass(frozen=True)
class JSResource(Resource):

    @cached_property
    def inline(self):
        if self.fileinfo is None:
            raise NotImplementedError(
                'Only local files from a file store can be inlined.')

        with self.fileinfo.filepath.open('r') as fd:
            code = fd.read()
        return InlineJSResource(
            code=code,
            bottom=self.bottom,
            dependencies=self.dependencies,
            fileinfo=self.fileinfo
        )

    def render(self, application_uri: str = "") -> bytes:
        url = multi_urljoin(self.root or application_uri, self.path)
        value = f'src="{url}"'
        if self.crossorigin:
            value += f' crossorigin="{self.crossorigin}"'
        if self.integrity:
            value += f' integrity="{self.integrity}"'
        return f"""<script {value}></script>\n""".encode()


@dataclass(frozen=True)
class CSSResource(Resource):

    @cached_property
    def inline(self):
        if self.fileinfo is None:
            raise NotImplementedError(
                'Only local files from a file store can be inlined.')

        with self.fileinfo.filepath.open('r') as fd:
            code = fd.read()

        return InlineCSSResource(
            code=code,
            bottom=self.bottom,
            dependencies=self.dependencies,
            fileinfo=self.fileinfo
        )

    def render(self, application_uri: str = "") -> bytes:
        url = multi_urljoin(self.root or application_uri, self.path)
        value = f'href="{url}"'
        if self.crossorigin:
            value += f' crossorigin="{self.crossorigin}"'
        if self.integrity:
            value += f' integrity="{self.integrity}"'
        return f"""<link rel="stylesheet" {value} />\n""".encode()
