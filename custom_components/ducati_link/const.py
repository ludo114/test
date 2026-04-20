DOMAIN = "ducati_link"

API_BASE_URL = "https://api.ducati.com/v1"
API_AUTH_URL = f"{API_BASE_URL}/auth/login"
API_VEHICLES_URL = f"{API_BASE_URL}/vehicles"
API_VEHICLE_URL = f"{API_BASE_URL}/vehicles/{{vin}}"
API_TELEMETRY_URL = f"{API_BASE_URL}/vehicles/{{vin}}/telemetry"

DEFAULT_SCAN_INTERVAL = 300  # seconds

CONF_VIN = "vin"

ATTR_ODOMETER = "odometer"
ATTR_FUEL_LEVEL = "fuel_level"
ATTR_BATTERY_VOLTAGE = "battery_voltage"
ATTR_NEXT_SERVICE_KM = "next_service_km"
ATTR_NEXT_SERVICE_DATE = "next_service_date"
ATTR_LAST_UPDATE = "last_update"

SENSOR_TYPES = {
    ATTR_ODOMETER: {
        "name": "Odometer",
        "unit": "km",
        "icon": "mdi:counter",
        "device_class": None,
        "state_class": "total_increasing",
    },
    ATTR_FUEL_LEVEL: {
        "name": "Fuel Level",
        "unit": "%",
        "icon": "mdi:gas-station",
        "device_class": None,
        "state_class": "measurement",
    },
    ATTR_BATTERY_VOLTAGE: {
        "name": "Battery Voltage",
        "unit": "V",
        "icon": "mdi:battery",
        "device_class": "voltage",
        "state_class": "measurement",
    },
    ATTR_NEXT_SERVICE_KM: {
        "name": "Next Service (km remaining)",
        "unit": "km",
        "icon": "mdi:wrench-clock",
        "device_class": None,
        "state_class": "measurement",
    },
    ATTR_NEXT_SERVICE_DATE: {
        "name": "Next Service Date",
        "unit": None,
        "icon": "mdi:calendar-wrench",
        "device_class": "date",
        "state_class": None,
    },
    ATTR_LAST_UPDATE: {
        "name": "Last Update",
        "unit": None,
        "icon": "mdi:clock-outline",
        "device_class": "timestamp",
        "state_class": None,
    },
}
