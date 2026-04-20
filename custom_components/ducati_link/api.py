from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from .const import (
    API_AUTH_URL,
    API_TELEMETRY_URL,
    API_VEHICLES_URL,
    API_VEHICLE_URL,
)

_LOGGER = logging.getLogger(__name__)

REQUEST_TIMEOUT = 30


class DucatiLinkAuthError(Exception):
    pass


class DucatiLinkApiError(Exception):
    pass


class DucatiLinkApi:
    def __init__(self, session: aiohttp.ClientSession, username: str, password: str) -> None:
        self._session = session
        self._username = username
        self._password = password
        self._token: str | None = None

    async def authenticate(self) -> None:
        payload = {"email": self._username, "password": self._password}
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                resp = await self._session.post(API_AUTH_URL, json=payload)
        except TimeoutError as err:
            raise DucatiLinkApiError("Request timed out") from err
        except aiohttp.ClientError as err:
            raise DucatiLinkApiError(f"Connection error: {err}") from err

        if resp.status == 401:
            raise DucatiLinkAuthError("Invalid credentials")
        if resp.status != 200:
            raise DucatiLinkApiError(f"Authentication failed: HTTP {resp.status}")

        data = await resp.json()
        self._token = data.get("access_token") or data.get("token")
        if not self._token:
            raise DucatiLinkApiError("No access token in response")

    async def _get(self, url: str) -> dict[str, Any]:
        if not self._token:
            await self.authenticate()

        headers = {"Authorization": f"Bearer {self._token}"}
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                resp = await self._session.get(url, headers=headers)
        except TimeoutError as err:
            raise DucatiLinkApiError("Request timed out") from err
        except aiohttp.ClientError as err:
            raise DucatiLinkApiError(f"Connection error: {err}") from err

        if resp.status == 401:
            # Token expired — re-authenticate once
            await self.authenticate()
            headers = {"Authorization": f"Bearer {self._token}"}
            try:
                async with asyncio.timeout(REQUEST_TIMEOUT):
                    resp = await self._session.get(url, headers=headers)
            except (TimeoutError, aiohttp.ClientError) as err:
                raise DucatiLinkApiError(str(err)) from err

        if resp.status != 200:
            raise DucatiLinkApiError(f"API error: HTTP {resp.status}")

        return await resp.json()

    async def get_vehicles(self) -> list[dict[str, Any]]:
        data = await self._get(API_VEHICLES_URL)
        return data if isinstance(data, list) else data.get("vehicles", [])

    async def get_vehicle(self, vin: str) -> dict[str, Any]:
        url = API_VEHICLE_URL.format(vin=vin)
        return await self._get(url)

    async def get_telemetry(self, vin: str) -> dict[str, Any]:
        url = API_TELEMETRY_URL.format(vin=vin)
        return await self._get(url)
