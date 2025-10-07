import pytest, fakeredis

@pytest.fixture(autouse=True)
def _patch_redis(monkeypatch):
    r = fakeredis.FakeRedis(decode_responses=True)
    def _from_url(url, decode_responses=True):
        return r
    monkeypatch.setattr("edge_isr.graph.redis.from_url", _from_url, raising=True)
    yield r
    r.flushall()
