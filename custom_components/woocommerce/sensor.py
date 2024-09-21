from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_NAME
import requests
import aiohttp
import asyncio

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up WooCommerce sensors based on config_entry."""
    config = config_entry.data
    sensors = [
        WooCommerceSensor(config, "orders_count", "Orders Count"),
        WooCommerceSensor(config, "total_sales", "Total Sales"),
        WooCommerceSensor(config, "completed_orders", "Completed Orders"),
        WooCommerceSensor(config, "last_order_id", "Last Order ID"),
        WooCommerceLastOrderDateSensor(config, "Last Order Date")  # Ajout du capteur de date
    ]
    async_add_entities(sensors, update_before_add=True)

class WooCommerceSensor(SensorEntity):
    def __init__(self, config, sensor_type, name):
        self._site_name = config["name"]  # Récupère le nom du site à partir de la configuration
        self._name = f"{self._site_name}_{sensor_type}"  # Définit le nom du capteur avec le nom du site
        self._sensor_type = sensor_type
        self._url = config["url"]
        self._consumer_key = config["consumer_key"]
        self._consumer_secret = config["consumer_secret"]
        self._state = None
        self._attr_unique_id = f"woocommerce_{self._site_name}_{sensor_type}"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        """Ajout d'une pause d'une minute avant de mettre à jour."""
        await asyncio.sleep(60)  # Attendre 60 secondes avant de faire la mise à jour

        """Fetch new state data for the sensor."""
        url = f"{self._url}/wp-json/wc/v3/orders?consumer_key={self._consumer_key}&consumer_secret={self._consumer_secret}&per_page=100"
        headers = {"Content-Type": "application/json"}
        
        # Utilisation d'aiohttp pour une requête asynchrone
        session = async_get_clientsession(self.hass)
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                if self._sensor_type == "orders_count":
                    self._state = len(data)
                elif self._sensor_type == "total_sales":
                    self._state = sum(float(order['total']) for order in data)
                elif self._sensor_type == "completed_orders":
                    self._state = len([order for order in data if order['status'] == 'completed'])
                elif self._sensor_type == "last_order_id":
                    self._state = data[0]['id'] if data else None

class WooCommerceLastOrderDateSensor(SensorEntity):
    def __init__(self, config, name):
        self._name = f"{config['name']}_last_order_date"
        self._url = config["url"]
        self._consumer_key = config["consumer_key"]
        self._consumer_secret = config["consumer_secret"]
        self._state = None
        self._attr_unique_id = f"woocommerce_{config['name']}_last_order_date"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        """Fetch the date of the last order."""
        url = f"{self._url}/wp-json/wc/v3/orders?consumer_key={self._consumer_key}&consumer_secret={self._consumer_secret}&per_page=1&orderby=date&order=desc"
        headers = {"Content-Type": "application/json"}

        session = async_get_clientsession(self.hass)
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                if data and len(data) > 0:
                    # Extraire la date de la dernière commande
                    last_order_date = data[0].get('date_created')
                    self._state = last_order_date
                else:
                    self._state = None