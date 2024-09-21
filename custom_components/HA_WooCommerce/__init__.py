from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta
import asyncio
import aiohttp
from aiocache import cached

from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the WooCommerce integration."""
    if not hass.data.get(DOMAIN):
        hass.data[DOMAIN] = {}
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up WooCommerce from a config entry."""
    
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    if entry.entry_id in hass.data[DOMAIN]:
        return False

    # Configure la plateforme "sensor"
    await hass.config_entries.async_forward_entry_setup(entry, "sensor")

    # Initialise l'emplacement pour les entités
    hass.data[DOMAIN][entry.entry_id] = []

    # Définit l'intervalle de mise à jour des capteurs à 15 minutes
    update_interval = timedelta(minutes=15)

    async def update_sensors(event_time):
        """Mise à jour des capteurs WooCommerce."""
        # Récupère les entités associées à l'entrée de configuration
        for entity in hass.data[DOMAIN][entry.entry_id]:
            await entity.async_update_ha_state(True)

    # Suivi de l'intervalle de mise à jour
    async_track_time_interval(hass, update_sensors, update_interval)
    
    return True

@cached(ttl=300)  # Mettre en cache pendant 5 minutes
async def fetch_data_from_woocommerce(url, config):
    """Fetch data from the WooCommerce API."""
    session = async_get_clientsession(hass)
    try:
        async with session.get(url, headers={"Content-Type": "application/json"}) as response:
            if response.status == 200:
                return await response.json()
            else:
                return []
    except aiohttp.ClientError:
        return []

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    
    if unload_ok:
        # Supprime l'entrée de hass.data
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
