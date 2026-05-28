from typing import NamedTuple
from pathlib import PurePosixPath


def multi_urljoin(*parts):
    return "/".join(part.strip("/") for part in parts if part)


class Resource(NamedTuple):
    path: str | PurePosixPath
    root: str | None = None
    bottom: bool = False
    integrity: str | None = None
    crossorigin: str | None = None
    dependencies: tuple["Resource"] | None = None

    def render(self, application_uri) -> bytes:
        pass


class JSResource(Resource):

    def render(self, application_uri: str = "") -> bytes:
        url = multi_urljoin(self.root or application_uri, self.path)
        value = f'src="{url}"'
        if self.crossorigin:
            value += f' crossorigin="{self.crossorigin}"'
        if self.integrity:
            value += f' integrity="{self.integrity}"'
        return f"""<script {value}></script>\r\n""".encode()


class CSSResource(Resource):

    def render(self, application_uri: str = "") -> bytes:
        url = multi_urljoin(self.root or application_uri, self.path)
        value = f'href="{url}"'
        if self.crossorigin:
            value += f' crossorigin="{self.crossorigin}"'
        if self.integrity:
            value += f' integrity="{self.integrity}"'
        return f"""<link rel="stylesheet" {value} />\r\n""".encode()
