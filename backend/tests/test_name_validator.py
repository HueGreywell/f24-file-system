import pytest

from app.services import name_validator
from app.services.exceptions import InvalidNameException


def test_normalize_trims_whitespace():
    assert name_validator.normalize("  report.txt  ") == "report.txt"


@pytest.mark.parametrize("value", [None, "", "   "])
def test_normalize_rejects_empty(value):
    with pytest.raises(InvalidNameException):
        name_validator.normalize(value)


@pytest.mark.parametrize("value", ["a/b", "a\\b"])
def test_normalize_rejects_path_separators(value):
    with pytest.raises(InvalidNameException):
        name_validator.normalize(value)


def test_normalize_rejects_too_long():
    with pytest.raises(InvalidNameException):
        name_validator.normalize("a" * 256)


def test_normalize_accepts_max_length():
    assert name_validator.normalize("a" * 255) == "a" * 255
