"""AC-016: the launcher binds loopback only, with debug off."""

import pytest

from expense_tracker import __main__ as launcher


class _FakeApp:
    def __init__(self):
        self.kwargs = None

    def run(self, **kwargs):
        self.kwargs = kwargs


@pytest.fixture
def fake_app(monkeypatch):
    app = _FakeApp()
    monkeypatch.setattr(launcher, "create_app", lambda: app)
    return app


def test_binds_loopback_with_debug_off(fake_app):
    launcher.main([])
    assert fake_app.kwargs == {"host": "127.0.0.1", "port": launcher.DEFAULT_PORT, "debug": False}


def test_port_argument_changes_only_the_port(fake_app):
    launcher.main(["--port", "8123"])
    assert fake_app.kwargs == {"host": "127.0.0.1", "port": 8123, "debug": False}


def test_host_and_debug_cannot_be_set_by_argument(fake_app):
    with pytest.raises(SystemExit):
        launcher.main(["--host", "0.0.0.0"])
    with pytest.raises(SystemExit):
        launcher.main(["--debug"])
    assert fake_app.kwargs is None


@pytest.mark.parametrize("bad", ["0", "65536", "abc"])
def test_invalid_port_rejected(fake_app, bad):
    with pytest.raises(SystemExit):
        launcher.main(["--port", bad])
    assert fake_app.kwargs is None
