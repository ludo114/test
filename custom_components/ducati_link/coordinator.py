from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DucatiLinkApi, DucatiLinkAuthError, DucatiLinkApiError
from .const import CONF_VIN, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class DucatiLinkCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, api: DucatiLinkApi) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self._api = api
        self._vin: str = entry.data[CONF_VIN]

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            vehicle, telemetry = await self._fetch_all()
        except DucatiLinkAuthError as err:
            raise ConfigEntryAuthFailed(err) from err
        except DucatiLinkApiError as err:
            raise UpdateFailed(f"Ducati Link API error: {err}") from err

        return {**vehicle, **telemetry}

    async def _fetch_all(self) -> tuple[dict[str, Any], dict[str, Any]]:
        vehicle = await self._api.get_vehicle(self._vin)
        telemetry = await self._api.get_telemetry(self._vin)
        return vehicle, telemetry
