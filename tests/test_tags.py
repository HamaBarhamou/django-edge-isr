from edge_isr import tag
def test_tag_format():
    assert tag("post", 42) == "post:42"
