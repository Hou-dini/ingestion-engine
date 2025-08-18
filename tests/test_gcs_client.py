import json
from dataclasses import asdict
from unittest.mock import MagicMock

from src.storage.gcs_client import GCSClient
from src.core.models import Post


def test_save_and_load_posts(monkeypatch):
    # Prepare fake bucket/blob
    uploaded = {}

    class FakeBlob:
        def __init__(self, name):
            self.name = name

        def upload_from_string(self, data, content_type=None):
            uploaded['data'] = data
            uploaded['content_type'] = content_type

        def download_as_text(self):
            return uploaded.get('data', '[]')

    class FakeBucket:
        def __init__(self):
            self.blobs = {}

        def blob(self, name):
            return FakeBlob(name)

    class FakeClient:
        def __init__(self):
            pass

        def bucket(self, bucket_name):
            return FakeBucket()

    # Patch storage.Client to return our fake client
    monkeypatch.setattr('src.storage.gcs_client.storage.Client', lambda: FakeClient())

    client = GCSClient('test-bucket')
    client.authenticate()

    posts = [Post(source_id='s1', title='t1', content='c1'), Post(source_id='s1', title='t2', content='c2')]
    client.save_posts_as_json(posts, 'test.json')

    # Ensure data was uploaded and is valid JSON
    assert 'data' in uploaded
    loaded = json.loads(uploaded['data'])
    assert isinstance(loaded, list)
    assert len(loaded) == 2

    # Now ensure load_posts_from_json returns Post objects
    result = client.load_posts_from_json('test.json')
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(p, Post) for p in result)
