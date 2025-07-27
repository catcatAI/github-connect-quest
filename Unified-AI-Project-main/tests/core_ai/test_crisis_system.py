import unittest
import pytest
import os
import sys
from unittest.mock import patch # Import patch

# Add src directory to sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..")) #
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from core_ai.crisis_system import CrisisSystem

class TestCrisisSystem(unittest.TestCase):

    def setUp(self):
        # Using a more specific config for testing, aligning with new defaults if needed
        self.test_config = {
            "crisis_keywords": ["emergency", "unsafe", "critical danger"], # Test specific keywords
            "default_crisis_level_on_keyword": 1, # Consistent with new CrisisSystem default
            "crisis_protocols": {
                "1": "test_protocol_level_1",
                "default": "test_default_protocol"
            }
        }
        self.crisis_sys_default_config = CrisisSystem() # Test with its internal defaults
        self.crisis_sys_custom_config = CrisisSystem(config=self.test_config)

    @pytest.mark.timeout(5)
    def test_01_initialization(self):
        self.assertIsNotNone(self.crisis_sys_default_config)
        self.assertEqual(self.crisis_sys_default_config.get_current_crisis_level(), 0)
        self.assertIn("emergency", self.crisis_sys_default_config.crisis_keywords) # Check default keyword

        self.assertIsNotNone(self.crisis_sys_custom_config)
        self.assertEqual(self.crisis_sys_custom_config.get_current_crisis_level(), 0)
        self.assertEqual(self.crisis_sys_custom_config.crisis_keywords, self.test_config["crisis_keywords"])
        self.assertEqual(self.crisis_sys_custom_config.default_crisis_level, self.test_config["default_crisis_level_on_keyword"])
        print("TestCrisisSystem.test_01_initialization PASSED")

    @pytest.mark.timeout(5)
    def test_02_assess_normal_input(self):
        level = self.crisis_sys_custom_config.assess_input_for_crisis({"text": "Tell me a story."})
        self.assertEqual(level, 0)
        self.assertEqual(self.crisis_sys_custom_config.get_current_crisis_level(), 0)
        print("TestCrisisSystem.test_02_assess_normal_input PASSED")

    @pytest.mark.timeout(5)
    def test_03_assess_crisis_input_escalation(self):
        # Test with custom config keywords
        level = self.crisis_sys_custom_config.assess_input_for_crisis({"text": "This is an emergency!"})
        expected_level = self.test_config["default_crisis_level_on_keyword"]
        self.assertEqual(level, expected_level)
        self.assertEqual(self.crisis_sys_custom_config.get_current_crisis_level(), expected_level)

        # Test that subsequent non-crisis input doesn't lower level (as per current logic)
        level_after_normal = self.crisis_sys_custom_config.assess_input_for_crisis({"text": "Everything is fine now."})
        self.assertEqual(level_after_normal, expected_level, "Crisis level should be maintained until resolved.")

        print("TestCrisisSystem.test_03_assess_crisis_input_escalation PASSED")
        self.crisis_sys_custom_config.resolve_crisis("Test cleanup") # Cleanup for next tests

    @pytest.mark.timeout(5)
    def test_04_resolve_crisis(self):
        self.crisis_sys_custom_config.assess_input_for_crisis({"text": "I feel unsafe."})
        self.assertNotEqual(self.crisis_sys_custom_config.get_current_crisis_level(), 0, "Crisis level should have been raised.")

        self.crisis_sys_custom_config.resolve_crisis("User confirmed okay.")
        self.assertEqual(self.crisis_sys_custom_config.get_current_crisis_level(), 0)
        print("TestCrisisSystem.test_04_resolve_crisis PASSED")

    @pytest.mark.timeout(5)
    def test_05_trigger_protocol(self):
        # This test is more about checking if the _trigger_protocol is called and logs something.
        # We can use unittest.mock.patch to spy on print or a logging mechanism if implemented.
        # For now, we'll rely on the fact that assess_input_for_crisis calls it.

        with patch('builtins.print') as mock_print:
            self.crisis_sys_custom_config.assess_input_for_crisis({"text": "critical danger detected"})

            # Check if _trigger_protocol's print was called with expected content
            triggered_protocol_action = self.test_config["crisis_protocols"][str(self.test_config["default_crisis_level_on_keyword"])]

            found_protocol_print = False
            for call_args in mock_print.call_args_list:
                args, _ = call_args
                if args and f"Executing protocol: '{triggered_protocol_action}'" in args[0]:
                    found_protocol_print = True
                    break
            self.assertTrue(found_protocol_print, "Expected protocol execution print not found.")

        print("TestCrisisSystem.test_05_trigger_protocol PASSED")
        self.crisis_sys_custom_config.resolve_crisis("Test cleanup")


if __name__ == '__main__':
    unittest.main(verbosity=2)
