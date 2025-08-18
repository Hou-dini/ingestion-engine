from src.core.models import Source, Post, Insight


def test_models_defaults():
    s = Source(name='n', url='u', type='reddit')
    assert s.id is not None

    p = Post(source_id=s.id, title='t', content='c')
    assert p.id is not None
    assert isinstance(p.metadata, dict)

    ins = Insight(title='title', summary='sum')
    assert isinstance(ins.source_ids, list)
    assert isinstance(ins.key_points, list)
