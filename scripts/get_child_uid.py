#!/usr/bin/env python3
"""One-off script to print child names and UIDs from your Huckleberry account."""

import asyncio
import os
import sys

# Load .env for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import aiohttp
from huckleberry_api import HuckleberryAPI


async def main():
    email = os.environ.get("HUCKLEBERRY_EMAIL")
    password = os.environ.get("HUCKLEBERRY_PASSWORD")
    timezone = os.environ.get("HUCKLEBERRY_TIMEZONE", "UTC")

    if not email or not password:
        print("ERROR: Set HUCKLEBERRY_EMAIL and HUCKLEBERRY_PASSWORD in .env or environment.")
        sys.exit(1)

    async with aiohttp.ClientSession() as session:
        api = HuckleberryAPI(
            email=email,
            password=password,
            timezone=timezone,
            websession=session,
        )
        await api.authenticate()
        user = await api.get_user()

        print(f"Account: {user.email}")
        print(f"\nChildren:")
        for child in user.childList:
            print(f"  Name: {child.nickname!r}  UID: {child.cid}")


if __name__ == "__main__":
    asyncio.run(main())
