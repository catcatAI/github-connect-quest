import unittest
import pytest
import asyncio
import uuid
import os
import sys
from unittest.mock import MagicMock, AsyncMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.agents.data_analysis_agent import DataAnalysisAgent
from src.hsp.types import HSPTaskRequestPayload, HSPMessageEnvelope
from src.shared.types.common_types import ToolDispatcherResponse

class TestDataAnalysisAgent(unittest.TestCase):

    def setUp(self):
        self.agent_id = f"did:hsp:test_data_analysis_agent_{uuid.uuid4().hex[:6]}"

        # We need to mock the services that the agent's base class initializes
        self.mock_services = {
            "hsp_connector": MagicMock(),
            "tool_dispatcher": MagicMock()
        }

        # Patch the service initialization and getter
        patcher_initialize = patch('src.agents.base_agent.initialize_services', return_value=None)
        patcher_get = patch('src.agents.base_agent.get_services', return_value=self.mock_services)

        self.addCleanup(patcher_initialize.stop)
        self.addCleanup(patcher_get.stop)

        self.mock_initialize = patcher_initialize.start()
        self.mock_get_services = patcher_get.start()

        # We also need to mock the ToolDispatcher used by the agent itself
        patcher_tool_dispatcher = patch('src.agents.data_analysis_agent.ToolDispatcher')
        self.mock_ToolDispatcher_class = patcher_tool_dispatcher.start()
        self.addCleanup(patcher_tool_dispatcher.stop)

        # Configure the mock instance that will be created
        self.mock_tool_dispatcher_instance = MagicMock()
        self.mock_ToolDispatcher_class.return_value = self.mock_tool_dispatcher_instance

        self.agent = DataAnalysisAgent(agent_id=self.agent_id)
        self.agent.hsp_connector = self.mock_services["hsp_connector"]

    @pytest.mark.timeout(10)
    def test_initialization(self):
        """Test that the agent initializes correctly and advertises its capabilities."""
        self.assertEqual(self.agent.agent_id, self.agent_id)
        self.assertIsNotNone(self.agent.hsp_connector)

        # Check that capabilities were defined
        self.assertTrue(len(self.agent.capabilities) > 0)
        self.assertEqual(self.agent.capabilities[0]['name'], 'CSV Data Analyzer')

    @pytest.mark.timeout(10)
    def test_handle_task_request_success(self):
        """Test the agent's handling of a successful task request."""
        # 1. Configure the mock ToolDispatcher to return a successful response
        mock_tool_response = ToolDispatcherResponse(
            status="success",
            payload="Analysis complete: 2 rows, 2 columns.",
            tool_name_attempted="analyze_csv",
            original_query_for_tool="summarize",
            error_message=None
        )
        self.mock_tool_dispatcher_instance.dispatch.return_value = mock_tool_response

        # 2. Create a mock HSP task payload
        request_id = "test_req_001"
        task_payload = HSPTaskRequestPayload(
            request_id=request_id,
            capability_id_filter=self.agent.capabilities[0]['capability_id'],
            parameters={"csv_content": "a,b\n1,2", "query": "summarize"},
            callback_address="hsp/results/test_requester/req_001"
        )
        envelope = HSPMessageEnvelope(message_id="msg1", sender_ai_id="test_sender", recipient_ai_id=self.agent_id, timestamp_sent="", message_type="", protocol_version="")

        # 3. Run the handle_task_request method
        asyncio.run(self.agent.handle_task_request(task_payload, "test_sender", envelope))

        # 4. Assert that the tool dispatcher was called correctly
        self.mock_tool_dispatcher_instance.dispatch.assert_called_once_with(
            query="summarize",
            explicit_tool_name="analyze_csv",
            csv_content="a,b\n1,2"
        )

        # 5. Assert that the HSP connector sent the correct result
        self.agent.hsp_connector.send_task_result.assert_called_once()
        sent_payload = self.agent.hsp_connector.send_task_result.call_args[0][0]
        sent_topic = self.agent.hsp_connector.send_task_result.call_args[0][1]

        self.assertEqual(sent_topic, "hsp/results/test_requester/req_001")
        self.assertEqual(sent_payload['request_id'], request_id)
        self.assertEqual(sent_payload['status'], "success")
        self.assertEqual(sent_payload['payload'], "Analysis complete: 2 rows, 2 columns.")
        self.assertIsNone(sent_payload['error_details'])

    @pytest.mark.timeout(10)
    def test_handle_task_request_tool_failure(self):
        """Test the agent's handling of a task where the tool fails."""
        # 1. Configure the mock ToolDispatcher to return a failure response
        mock_tool_response = ToolDispatcherResponse(
            status="failure_tool_error",
            payload=None,
            tool_name_attempted="analyze_csv",
            original_query_for_tool="summarize",
            error_message="Invalid CSV format"
        )
        self.mock_tool_dispatcher_instance.dispatch.return_value = mock_tool_response

        # 2. Create a mock HSP task payload
        request_id = "test_req_002"
        task_payload = HSPTaskRequestPayload(
            request_id=request_id,
            capability_id_filter=self.agent.capabilities[0]['capability_id'],
            parameters={"csv_content": "a,b\n1,2,3", "query": "summarize"},
            callback_address="hsp/results/test_requester/req_002"
        )
        envelope = HSPMessageEnvelope(message_id="msg2", sender_ai_id="test_sender", recipient_ai_id=self.agent_id, timestamp_sent="", message_type="", protocol_version="")

        # 3. Run the handler
        asyncio.run(self.agent.handle_task_request(task_payload, "test_sender", envelope))

        # 4. Assert HSP connector sent a failure result
        self.agent.hsp_connector.send_task_result.assert_called_once()
        sent_payload = self.agent.hsp_connector.send_task_result.call_args[0][0]

        self.assertEqual(sent_payload['status'], "failure")
        self.assertIsNotNone(sent_payload['error_details'])
        self.assertEqual(sent_payload['error_details']['error_message'], "Invalid CSV format")

if __name__ == '__main__':
    unittest.main()
