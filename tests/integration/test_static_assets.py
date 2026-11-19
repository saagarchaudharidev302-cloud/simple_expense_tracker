from html.parser import HTMLParser


class _LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stylesheets = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "link" and attributes.get("rel") == "stylesheet":
            self.stylesheets.append(attributes.get("href"))


def stylesheet_links(html):
    collector = _LinkCollector()
    collector.feed(html)
    return collector.stylesheets


def test_stylesheet_is_served_as_css(client):
    response = client.get("/static/style.css")
    assert response.status_code == 200
    assert response.mimetype == "text/css"


def test_pages_link_stylesheet(client):
    html = client.get("/").get_data(as_text=True)
    assert stylesheet_links(html) == ["/static/style.css"]


def test_error_page_renders_with_stylesheet(client):
    response = client.get("/no-such-page")
    assert response.status_code == 404
    assert stylesheet_links(response.get_data(as_text=True)) == ["/static/style.css"]


def test_static_respects_host_check(client):
    response = client.get("/static/style.css", headers={"Host": "evil.example"})
    assert response.status_code == 400
