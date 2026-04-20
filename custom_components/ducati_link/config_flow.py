from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DucatiLinkApi, DucatiLinkAuthError, DucatiLinkApiError
from .const import CONF_VIN, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class DucatiLinkConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._username: str = ""
        self._password: str = ""
        self._vehicles: list[dict[str, Any]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            self._username = user_input[CONF_USERNAME]
            self._password = user_input[CONF_PASSWORD]

            session = async_get_clientsession(self.hass)
            api = DucatiLinkApi(session, self._username, self._password)

            try:
                await api.authenticate()
                self._vehicles = await api.get_vehicles()
            except DucatiLinkAuthError:
                errors["base"] = "invalid_auth"
            except DucatiLinkApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during Ducati Link setup")
                errors["base"] = "unknown"
            else:
                if not self._vehicles:
                    errors["base"] = "no_vehicles"
                elif len(self._vehicles) == 1:
                    return await self._create_entry(self._vehicles[0])
                else:
                    return await self.async_step_vehicle()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    async def async_step_vehicle(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            vin = user_input[CONF_VIN]
            vehicle = next((v for v in self._vehicles if v.get("vin") == vin), None)
            if vehicle:
                return await self._create_entry(vehicle)
            errors["base"] = "unknown"

        vehicle_options = {
            v["vin"]: f"{v.get('model', 'Ducati')} ({v['vin']})"
            for v in self._vehicles
            if "vin" in v
        }

        return self.async_show_form(
            step_id="vehicle",
            data_schema=vol.Schema({vol.Required(CONF_VIN): vol.In(vehicle_options)}),
            errors=errors,
        )

    async def _create_entry(self, vehicle: dict[str, Any]) -> ConfigFlowResult:
        vin = vehicle.get("vin", "")
        await self.async_set_unique_id(vin)
        self._abort_if_unique_id_configured()

        model = vehicle.get("model", "Ducati")
        title = f"{model} ({vin[-6:]})" if vin else model

        return self.async_create_entry(
            title=title,
            data={
                CONF_USERNAME: self._username,
                CONF_PASSWORD: self._password,
                CONF_VIN: vin,
            },
        )
