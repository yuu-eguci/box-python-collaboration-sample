import socket

import pytest


@pytest.fixture(autouse=True)
def block_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """本物の Box に繋がらないように、テスト中はネットワークを塞ぐ。"""
    def deny(*args: object, **kwargs: object) -> None:
        raise RuntimeError('network is blocked in tests')

    monkeypatch.setattr(socket.socket, 'connect', deny)
    monkeypatch.setattr(socket, 'create_connection', deny)
    monkeypatch.setattr(socket, 'getaddrinfo', deny)
