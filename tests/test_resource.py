from html_resources.resources import Resource, CSSResource, JSResource



def test_resource():

    resource = Resource(
        path="/whatever"
    )

    assert resource.root is None
    assert resource.bottom is False
    assert resource.integrity is None
    assert resource.crossorigin is None
    assert resource.dependencies is None


def test_css_resource_rendering():
    css = CSSResource("some_path")
    assert css.render() == b'<link rel="stylesheet" href="some_path" />\n'


def test_js_resource_rendering():
    js = JSResource("some_path")
    assert js.render() == b'<script src="some_path"></script>\n'
