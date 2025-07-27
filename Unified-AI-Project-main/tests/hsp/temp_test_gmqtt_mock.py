import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

class MockGmqttClient:
    def __init__(self):
        self.publish = AsyncMock()

@pytest.mark.asyncio
async def test_gmqtt_publish_mock():
    client = MockGmqttClient()
    topic = "test/topic"
    payload = b"test_payload"
    qos = 1

    try:
        await client.publish(topic, payload, qos=qos)
        print("Mocked gmqtt.Client.publish called successfully.")
    except Exception as e:
        print(f"Error calling mocked gmqtt.Client.publish: {e}")
        pytest.fail(f"Mocked gmqtt.Client.publish raised an exception: {e}")

    client.publish.assert_called_once_with(topic, payload, qos=qos)
    print("Assertion passed: Mocked gmqtt.Client.publish was called with correct arguments.")
