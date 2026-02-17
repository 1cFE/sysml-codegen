"""Conformance test configuration and fixtures."""


def pytest_configure(config):
    config.addinivalue_line("markers", "req(id): map test to requirement ID")
