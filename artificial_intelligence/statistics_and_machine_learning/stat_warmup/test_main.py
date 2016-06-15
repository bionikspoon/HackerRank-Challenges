# coding=utf-8
import pytest

from .main import describe


@pytest.fixture
def data():
    return 64630, 11735, 14216, 99233, 14470, 4978, 73429, 38120, 51135, 67060


def test_describe_mean(data):
    summary = describe(data)
    assert summary.mean == 43900.6

def test_describe_median(data):
    summary = describe(data)
    assert summary.median == 44627.5

def test_describe_mode(data):
    summary = describe(data)
    assert summary.mode == 4978

def test_describe_std(data):
    summary = describe(data)
    assert summary.std == 30466.9

def test_describe_interval(data):
    summary = describe(data)
    assert summary.interval == (25017.0, 62784.2)
