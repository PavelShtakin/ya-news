from time import sleep
import pytest
import sys


def one_more(x):
    return x + 1


@pytest.mark.parametrize(
    'input_arg, expected_result',
    [
        (4, 5),
        pytest.param(3, 5, marks=pytest.mark.xfail(reason="Ожидаемое падение")),
    ],
    ids=["First parameter", "Second parameter"]
)
def test_one_more(input_arg, expected_result):
    assert one_more(input_arg) == expected_result


def get_sort_list(string):
    return sorted(string.split(', '))


def test_sort():
    result = get_sort_list('Яша, Саша, Маша, Даша')
    assert result == ['Даша', 'Маша', 'Саша', 'Яша']


@pytest.mark.skip(reason='Что-то не работает')
def test_fail():
    assert one_more(3) == 5


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="На Windows временно не работает"
)
def test_not_on_windows():
    assert True


@pytest.mark.xfail(reason="Функция ещё не реализована")
def test_expected_to_fail():
    assert one_more(0) == 0

@pytest.mark.slow
def test_type():
    sleep(3)
    assert isinstance(["a", "b"], list)