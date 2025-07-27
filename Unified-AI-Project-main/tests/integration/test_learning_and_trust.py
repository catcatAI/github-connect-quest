import unittest
import pytest
import asyncio
import sys
import os
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core_ai.learning.learning_manager import LearningManager
from src.core_ai.trust_manager.trust_manager_module import TrustManager
from src.core_ai.memory.ham_memory_manager import HAMMemoryManager
from src.hsp.types import HSPFactPayload, HSPMessageEnvelope

class TestLearningAndTrustIntegration(unittest.TestCase):

    def setUp(self):
        """Set up a fresh LearningManager with mocked dependencies for each test."""
        self.ai_id = "test_host_ai"
        self.trust_manager = TrustManager()

        # Use an in-memory HAM mock to avoid file I/O
        self.ham_memory = MagicMock(spec=HAMMemoryManager)
        self.ham_memory.query_core_memory.return_value = []
        self.ham_memory.increment_metadata_field.return_value = True
        self.ham_memory.store_experience.return_value = f"ham_{uuid.uuid4().hex}"

        # Mock ContentAnalyzer as it's not the focus of this test
        mock_content_analyzer = MagicMock()
        mock_content_analyzer.process_hsp_fact_content.return_value = {}

        self.learning_manager = LearningManager(
            ai_id=self.ai_id,
            ham_memory_manager=self.ham_memory,
            fact_extractor=MagicMock(), # Not used in HSP fact processing
            personality_manager=MagicMock(),
            content_analyzer=mock_content_analyzer,
            hsp_connector=MagicMock(),
            trust_manager=self.trust_manager,
            operational_config={"learning_thresholds": {"min_hsp_fact_confidence_to_store": 0.5}}
        )

    @pytest.mark.timeout(10)
    def test_duplicate_fact_increments_corroboration(self):
        """
        Tests that receiving a duplicate fact increments corroboration_count
        and does not store a new fact.
        """
        # 1. Setup: A fact already exists in memory
        existing_ham_id = "ham_existing_fact_001"
        fact_id = "hsp_fact_duplicate_test"
        originator_id = "did:hsp:originator_1"

        existing_record = {
            "id": existing_ham_id,
            "metadata": {
                "hsp_fact_id": fact_id,
                "hsp_originator_ai_id": originator_id,
                "corroboration_count": 1
            }
        }
        self.ham_memory.query_core_memory.return_value = [existing_record]

        # 2. Action: Process the same fact again from a different sender
        duplicate_fact_payload = HSPFactPayload(id=fact_id, source_ai_id=originator_id, statement_nl="This is a test fact.", confidence_score=0.9)
        envelope = HSPMessageEnvelope(message_id="msg2", sender_ai_id="did:hsp:sender_2", recipient_ai_id=self.ai_id, timestamp_sent="", message_type="", protocol_version="")

        result = self.learning_manager.process_and_store_hsp_fact(duplicate_fact_payload, "did:hsp:sender_2", envelope)

        # 3. Assertions
        # It should not store a new fact
        self.assertIsNone(result)
        # It should have queried memory to find the duplicate
        self.ham_memory.query_core_memory.assert_called_once()
        # It should NOT have tried to store a new experience
        self.ham_memory.store_experience.assert_not_called()
        # It SHOULD have incremented the metadata field of the existing record
        self.ham_memory.increment_metadata_field.assert_called_once_with(existing_ham_id, "corroboration_count")

    @pytest.mark.timeout(10)
    def test_fact_from_low_trust_source_is_discarded(self):
        """
        Tests that a fact with high original confidence is discarded if the source has very low trust.
        """
        # 1. Setup: Define a low-trust sender and set their trust score
        low_trust_sender_id = "did:hsp:untrusted_sender"
        self.trust_manager.update_trust_score(low_trust_sender_id, new_absolute_score=0.1)

        # 2. Action: Process a fact from this sender with high original confidence
        fact_payload = HSPFactPayload(id="hsp_fact_low_trust", source_ai_id="originator_2", statement_nl="This is a highly confident but untrusted fact.", confidence_score=0.95)
        envelope = HSPMessageEnvelope(message_id="msg3", sender_ai_id=low_trust_sender_id, recipient_ai_id=self.ai_id, timestamp_sent="", message_type="", protocol_version="")

        result = self.learning_manager.process_and_store_hsp_fact(fact_payload, low_trust_sender_id, envelope)

        # 3. Assertions
        # The effective confidence (0.95 * 0.1 = 0.095) should be below the threshold (0.5)
        self.assertIsNone(result, "Fact from low-trust source should be discarded")
        # Ensure it didn't get stored
        self.ham_memory.store_experience.assert_not_called()

    @pytest.mark.timeout(10)
    def test_fact_from_high_trust_source_is_accepted(self):
        """
        Tests that a fact with medium original confidence is accepted if the source has high trust.
        """
        # 1. Setup: Define a high-trust sender
        high_trust_sender_id = "did:hsp:trusted_sender"
        self.trust_manager.update_trust_score(high_trust_sender_id, new_absolute_score=0.9)

        # 2. Action: Process a fact with medium confidence that would otherwise fail
        # Original confidence 0.55 * trust 0.9 = 0.495, which is just below the 0.5 threshold.
        # Let's use a slightly higher confidence to ensure it passes.
        fact_payload = HSPFactPayload(id="hsp_fact_high_trust", source_ai_id="originator_3", statement_nl="A reasonably confident fact from a trusted source.", confidence_score=0.6)
        # Effective confidence = 0.6 * 0.9 = 0.54, which is above the 0.5 threshold.
        envelope = HSPMessageEnvelope(message_id="msg4", sender_ai_id=high_trust_sender_id, recipient_ai_id=self.ai_id, timestamp_sent="", message_type="", protocol_version="")

        result = self.learning_manager.process_and_store_hsp_fact(fact_payload, high_trust_sender_id, envelope)

        # 3. Assertions
        self.assertIsNotNone(result, "Fact from high-trust source should be accepted")
        # Ensure it was stored
        self.ham_memory.store_experience.assert_called_once()
        # Check that the stored confidence is the final calculated score
        call_args = self.ham_memory.store_experience.call_args
        stored_metadata = call_args.kwargs['metadata']
        self.assertAlmostEqual(stored_metadata['confidence'], (0.6 * 0.9 * 0.7) + (0.5 * 0.15) + (0.5 * 0.15))

if __name__ == '__main__':
    unittest.main()
