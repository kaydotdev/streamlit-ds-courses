import pytest

from util import sub_numwords, sub_sepr, sub_space


@pytest.fixture(scope="function", params=[
    ("hello world", "hello world"),
    ("hello\n world", "hello  world"),
    ("\r\t\t\thello\t\t\tworld\n", " hello world ")
])
def sub_sepr_fixture(request):
    return request.param


@pytest.fixture(scope="function", params=[
    ("hello world", "hello world"),
    ("hell0 world", " world"),
    ("1, 2, 3, 4, 5", ", , , , ")
])
def sub_numwords_fixture(request):
    return request.param


@pytest.fixture(scope="function", params=[
    ("hello world", "hello world"),
    ("  he llo      world  ", " he llo world "),
    ("           ", " "),
    ("", "")
])
def sub_space_fixture(request):
    return request.param


def test_sub_sepr(sub_sepr_fixture):
    # arrange
    inp_text, expected_str = sub_sepr_fixture

    # act
    actual_str = sub_sepr(inp_text)

    # assert
    assert expected_str == actual_str


def test_sub_numwords(sub_numwords_fixture):
    # arrange
    inp_text, expected_str = sub_numwords_fixture

    # act
    actual_str = sub_numwords(inp_text)

    # assert
    assert expected_str == actual_str


def test_sub_space(sub_space_fixture):
    # arrange
    inp_text, expected_str = sub_space_fixture

    # act
    actual_str = sub_space(inp_text)

    # assert
    assert expected_str == actual_str

