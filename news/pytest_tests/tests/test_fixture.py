import pytest

@pytest.fixture
def sample_data():
    return {'name': 'Pavel', 'age': 30}

def test_sample_data_has_name(sample_data):
    assert 'name' in sample_data

def test_sample_data_age_is_int(sample_data):
    assert isinstance(sample_data['age'], int)