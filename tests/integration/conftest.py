import os

import aiohttp
import pytest
from dotenv import load_dotenv

from huckleberry_api import HuckleberryAPI

load_dotenv()

TEST_CHILD_NAME = "Test"


@pytest.fixture
async def api():
    async with aiohttp.ClientSession() as session:
        _api = HuckleberryAPI(
            email=os.environ["HUCKLEBERRY_EMAIL"],
            password=os.environ["HUCKLEBERRY_PASSWORD"],
            timezone=os.environ.get("HUCKLEBERRY_TIMEZONE", "UTC"),
            websession=session,
        )
        await _api.authenticate()
        yield _api


@pytest.fixture
async def test_child_uid(api):
    user = await api.get_user()
    for child in user.childList:
        if child.nickname.lower() == TEST_CHILD_NAME.lower():
            return child.cid
    raise RuntimeError(f"Test child '{TEST_CHILD_NAME}' not found in account")


@pytest.fixture(autouse=True)
async def clean_nursing_state(api, test_child_uid):
    """Cancel any active nursing before and after each test."""
    await api.cancel_nursing(test_child_uid)
    yield
    await api.cancel_nursing(test_child_uid)
