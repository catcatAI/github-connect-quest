# Project Placeholders and TODOs Summary

This document outlines the placeholders and TODO items found within the Unified-AI-Project codebase.

## 1. Configuration Placeholders

These are values intended to be replaced by actual secrets or configurations, typically via environment variables. They are generally structural and not code to be written.

*   **File:** `configs/api_keys.yaml`
    *   `GEMINI_API_KEY_PLACEHOLDER` (L7): Placeholder for Google Gemini API Key.
    *   `OPENAI_API_KEY_PLACEHOLDER` (L11): Placeholder for OpenAI API Key.
    *   `FIREBASE_CREDENTIALS_PATH_PLACEHOLDER` (L18): Placeholder for Firebase Admin SDK JSON credentials file path.
    *   `BASE_URL_PLACEHOLDER` (L22): Placeholder for a general base URL.
    *   `ANOTHER_SERVICE_API_KEY_PLACEHOLDER` (L24, commented out): Example placeholder.
    *   `SOME_COMPLEX_SERVICE_CLIENT_ID_PLACEHOLDER` (L28, commented out): Example placeholder.
    *   `SOME_COMPLEX_SERVICE_CLIENT_SECRET_PLACEHOLDER` (L29, commented out): Example placeholder.
    *   `SOME_COMPLEX_SERVICE_REGION_PLACEHOLDER` (L30, commented out): Example placeholder.
    *   **Note:** The file itself states these are for documentation and structural reference.

## 2. Missing Feature/Logic Implementation (TODOs)

These are comments indicating planned work or missing functionality that requires code implementation.

*   **File:** `src/core_ai/code_understanding/lightweight_code_model.py`
    *   **Line:** ~177 (Original TODO location in `get_tool_structure`)
    *   **Placeholder:** `# COMPLETED: Logic to resolve tool_name to a filepath has been implemented.`
    *   **Context:** Was in the `get_tool_structure` method.
    *   **Required Functionality:** (Implemented in `feat/lcm-tool-name-resolution`) The `get_tool_structure` method now resolves `tool_path_or_name` by checking if it's a direct path, then attempting to find `name.py`, `tool_name.py`, or `name_tool.py` in the configured `tools_directory`.

*   **File:** `src/core_ai/service_discovery/service_discovery_module.py`
    *   **Line:** ~177 (Original TODO location in a previous version of the file)
    *   **Placeholder:** `# COMPLETED: Logic for staleness/expiration of capabilities based on last_seen and a configurable threshold is now implemented.`
    *   **Context:** Was at the end of the class definition in a prior version. Logic now integrated into `find_capabilities` and `get_capability_by_id`.
    *   **Prerequisite Note:** (Resolved) The `ServiceDiscoveryModule` was refactored in `feat/hsp-service-discovery-module` to align with HSP requirements.
    *   **Required Functionality:** (Implemented in `feat/sdm-capability-staleness`) A mechanism to filter out stale advertised HSP capabilities based on `last_seen` timestamp and a configurable `staleness_threshold_seconds` has been added to `find_capabilities` and `get_capability_by_id`.

*   **File:** `src/hsp/connector.py`
    *   **Line:** ~63 (Comment in code updated/removed)
    *   **Placeholder:** `# CLARIFIED: Reconnection strategy is handled by the Paho MQTT client's built-in features (see class docstring and `reconnect_delay_set` usage in HSPConnector).`
    *   **Context:** Was in the `_on_mqtt_disconnect` method, referring to manual reconnection logic.
    *   **Required Functionality:** (N/A - Handled by Paho MQTT client) The connector now relies on Paho's automatic reconnection. Verification and enhanced logging were completed in `feat/hsp-connector-robustness`.
    *   **Line:** ~128
    *   **Placeholder:** `"payload_schema_uri": None, # TODO: Add schema URIs when defined`
    *   **Context:** Within the `_build_hsp_envelope` method.
    *   **Required Functionality:** Update this to populate the `payload_schema_uri` field with appropriate URIs once the HSP message payload schemas are formally defined and published.
    *   **Line:** ~260 (Original TODO location)
    *   **Placeholder:** `# CLARIFIED: Logic for sending 'received' ACKs when qos_parameters.requires_ack is true is implemented in _handle_hsp_message_str and _send_acknowledgement.`
    *   **Context:** Was in the `_handle_hsp_message_str` method.
    *   **Required Functionality:** (Addressed for 'received' ACKs) The connector sends 'received' ACKs as required. Functionality verified and tested in `feat/hsp-ack-handling`. (Future enhancements could include 'processed' ACKs or NACKs).
    *   **Line:** ~128 (Original location of the TODO in `_build_hsp_envelope`)
    *   **Placeholder:** `# COMPLETED (Placeholder): Logic to generate conventional placeholder schema URIs (e.g., 'hsp:schema:payload/Fact/0.1') for 'payload_schema_uri' is implemented.`
    *   **Context:** Within the `_build_hsp_envelope` method.
    *   **Required Functionality:** (Partially Addressed in `feat/hsp-payload-schema-uri-placeholder`) The `payload_schema_uri` field is now populated with placeholder URIs based on message type and version. Actual schema definition and hosting at resolvable URIs are still pending future architectural work.

*   **File:** `src/interfaces/electron_app/renderer.js`
    *   **Line:** ~137 (Original location of TODO comment)
    *   **Placeholder:** `# COMPLETED: Button to trigger/select HSP service has been added.`
    *   **Context:** Was inside the `loadHspServices` function.
    *   **Required Functionality:** (Implemented in `feat/electron-hsp-use-service-button`) A "Use Service" button is now added to each service in the HSP services list. Clicking it populates the "Target Capability ID" field in the HSP Task Request form and clears the parameters field.

*   **Electron App Improvements:**
    *   **File:** `docs/interfaces/ELECTRON_APP_IMPROVEMENTS.md`
    *   **Context:** Comprehensive improvement suggestions for the Electron desktop application.
    *   **Required Functionality:** The document outlines detailed plans for UI enhancements, feature additions, code structure optimizations, and security improvements for the Electron app interface. These improvements are organized into a phased implementation roadmap.

## 3. Code/Data Comments & Clarifications

These are comments that were picked up by the search but are not actionable code placeholders requiring new implementation. They are either logic that handles TODOs, commented-out debug lines, TODOs within example data, or general clarifications.

*   **File:** `scripts/data_processing/process_copilot_logs.py`
    *   Line ~46: `if prompt.startswith("# TODO:") or prompt.startswith("// TODO:")` (Logic for filtering input data)
    *   Line ~47: `# print(f"Skipping row {row_num+2}: Prompt is a TODO comment ('{prompt}').")` (Commented-out debug code)
    *   Line ~96: `2024-05-20T10:10:00Z,"# TODO: Add more comprehensive error handling here",...` (Example TODO within a dummy CSV string in the script)

*   **File:** `src/core_ai/dialogue/dialogue_manager.py`
    *   Line ~618 (approx): `raise NotImplementedError("Tool logic not implemented yet.")` and `# TODO: Implement actual tool logic here`. These are found within a multi-line string that serves as an example/template for an LLM to generate tool code. They are part of the *template's content*, not direct TODOs for the Dialogue Manager itself.

*   **File:** `src/shared/types/common_types.py`
    *   Line ~216: `# TODO: Consider a transformation step if strict snake_case is required internally for these.` (Comment suggesting a potential future refactor for field naming in `OllamaChatHistoryEntry`)
    *   Line ~410: `id: str # The memory_id (mem_XXXXXX)` (A clarifying comment for a field, not a placeholder to be filled.)

## 4. Data Anomalies (Previously "Data Placeholders")

Anomalies observed within data files.

*   **File:** `data/processed_data/dialogue_context_memory.json`
    *   **Observation:** The string `"XXX"` has been found as a substring within some `encrypted_package_b64` values.
    *   **Clarification (as of July 8, 2024):** Initial hypotheses suggested "XXX" might be a special placeholder or a "Deep Mapping" token. However, further investigation, detailed in `docs/architecture/DEEP_MAPPING_AND_PERSONALITY_SIMULATION.md` and summarized in `docs/PROJECT_STATUS_SUMMARY.md` (Section 2), has concluded that these "XXX" sequences are **coincidental substrings** within normally processed (abstracted, compressed, encrypted) HAM data.
    *   **Current Understanding:** These occurrences are not indicative of a deliberate "Deep Mapping" token system or placeholders for missing data in that sense. They are artifacts of the standard data transformation pipeline. While the concept of advanced Deep Mapping remains a potential future architectural goal, it is not represented by these "XXX" findings. Any perceived incompleteness or issues with such data packages should be investigated as potential data integrity or processing artifacts rather than special markers.

This summary provides a clear overview of outstanding tasks and points of interest related to placeholders and TODOs in the project.
