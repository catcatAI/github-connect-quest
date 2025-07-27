import pytest
import asyncio
import os
import sys
from amqtt.broker import Broker
from src.hsp.connector import HSPConnector

MQTT_BROKER_ADDRESS = "127.0.0.1"
MQTT_BROKER_PORT = 1883
TEST_AI_ID = "did:hsp:test_ai_001"

@pytest.fixture(scope="module")
async def broker(event_loop):
    config = {
        "default": {
            "type": "tcp",
            "bind": f"{MQTT_BROKER_ADDRESS}:{MQTT_BROKER_PORT}",
        },
        "sys_interval": 10,
        "auth": {
            "allow-anonymous": True
        },
        "topic-check": {"enabled": False},
    }
    broker = Broker(config, loop=event_loop)
    await broker.start()
    await asyncio.sleep(3) # Give the broker a moment to fully start
    yield broker
    await broker.shutdown()

@pytest.fixture
async def hsp_connector(broker):
    connector = HSPConnector(
        TEST_AI_ID,
        
         broker_address=MQTT_BROKER_ADDRESS,
         broker_port=1883,
    )
    await connector.connect()
    if not connector.is_connected:
        pytest.fail("Failed to connect HSPConnector")
    yield connector
    await connector.disconnect()

@pytest.mark.asyncio
async def test_broker_and_connector_startup(hsp_connector):
    # If we reach here, it means the broker started and the connector connected successfully
    assert hsp_connector.is_connected, "HSPConnector should be connected"
    print("Broker started and HSPConnector connected successfully!")