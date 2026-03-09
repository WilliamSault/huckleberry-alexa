"""Async→sync adapter for the Huckleberry API, with credential and child resolution."""

import asyncio
import os

import aiohttp
from huckleberry_api import HuckleberryAPI


def run_huckleberry(coro_factory):
    """Run an async huckleberry coroutine synchronously.

    coro_factory is a callable that accepts a HuckleberryAPI instance and
    returns a coroutine, e.g.:  lambda api: api.start_nursing(child_uid, side="left")
    """
    async def _run():
        async with aiohttp.ClientSession() as session:
            api = HuckleberryAPI(
                email=os.environ["HUCKLEBERRY_EMAIL"],
                password=os.environ["HUCKLEBERRY_PASSWORD"],
                timezone=os.environ.get("HUCKLEBERRY_TIMEZONE", "UTC"),
                websession=session,
            )
            await api.authenticate()
            return await coro_factory(api)

    return asyncio.run(_run())


def resolve_child_uid(child_name: str | None = None) -> tuple[str, str]:
    """Resolve child UID by name from the Huckleberry account.

    Returns (child_uid, child_name) tuple.
    Raises ValueError with helpful message if name not found.
    """
    default_name = os.environ.get("HUCKLEBERRY_DEFAULT_CHILD", "Frederica")
    target_name = child_name or default_name

    async def _resolve():
        async with aiohttp.ClientSession() as session:
            api = HuckleberryAPI(
                email=os.environ["HUCKLEBERRY_EMAIL"],
                password=os.environ["HUCKLEBERRY_PASSWORD"],
                timezone=os.environ.get("HUCKLEBERRY_TIMEZONE", "UTC"),
                websession=session,
            )
            await api.authenticate()
            user = await api.get_user()
            children = user.childList
            for child in children:
                if child.nickname.lower() == target_name.lower():
                    return child.cid, child.nickname
            available = ", ".join(c.nickname for c in children)
            raise ValueError(
                f"I couldn't find a child named {target_name}. "
                f"Available children are {available}."
            )

    return asyncio.run(_resolve())


def run_huckleberry_with_child(coro_factory, child_name: str | None = None):
    """Resolve child UID and run an async huckleberry coroutine synchronously.

    coro_factory is called as: coro_factory(api, child_uid)
    Returns (result, resolved_child_name).
    """
    default_name = os.environ.get("HUCKLEBERRY_DEFAULT_CHILD", "Frederica")
    target_name = child_name or default_name

    async def _run():
        async with aiohttp.ClientSession() as session:
            api = HuckleberryAPI(
                email=os.environ["HUCKLEBERRY_EMAIL"],
                password=os.environ["HUCKLEBERRY_PASSWORD"],
                timezone=os.environ.get("HUCKLEBERRY_TIMEZONE", "UTC"),
                websession=session,
            )
            await api.authenticate()
            user = await api.get_user()
            children = user.childList
            resolved_uid = None
            resolved_name = None
            for child in children:
                if child.nickname.lower() == target_name.lower():
                    resolved_uid = child.cid
                    resolved_name = child.nickname
                    break
            if resolved_uid is None:
                available = ", ".join(c.nickname for c in children)
                raise ValueError(
                    f"I couldn't find a child named {target_name}. "
                    f"Available children are {available}."
                )
            result = await coro_factory(api, resolved_uid)
            return result, resolved_name

    return asyncio.run(_run())
