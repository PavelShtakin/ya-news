import pytest

@pytest.fixture(scope="module")
def some_data():
    print("Создание данных")
    return [1, 2, 3]

def test_first(some_data):
    assert some_data[0] == 1

def test_second(some_data):
    assert len(some_data) == 3
