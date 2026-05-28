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
