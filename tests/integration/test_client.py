"""Integration tests for run_huckleberry_with_child child resolution."""

import os

import pytest

from huckleberry_alexa.huckleberry_client import run_huckleberry_with_child

pytestmark = pytest.mark.integration

TEST_CHILD_NAME = "Test"


def test_resolves_test_child_by_name():
    _, resolved_name = run_huckleberry_with_child(
        lambda api, uid: api.get_user(),
        child_name=TEST_CHILD_NAME,
    )
    assert resolved_name == TEST_CHILD_NAME


def test_unknown_child_raises_value_error():
    with pytest.raises(ValueError) as exc_info:
        run_huckleberry_with_child(
            lambda api, uid: api.get_user(),
            child_name="NonExistentChildXYZ",
        )
    message = str(exc_info.value)
    assert "couldn't find" in message
    assert "Available children" in message


def test_default_child_env_var_respected(monkeypatch):
    monkeypatch.setenv("HUCKLEBERRY_DEFAULT_CHILD", TEST_CHILD_NAME)
    _, resolved_name = run_huckleberry_with_child(
        lambda api, uid: api.get_user(),
        child_name=None,
    )
    assert resolved_name == TEST_CHILD_NAME
