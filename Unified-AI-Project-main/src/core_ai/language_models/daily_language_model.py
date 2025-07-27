import json # Added import for JSON parsing
import re # Added import for regular expressions
from typing import Dict, Any, Optional

# Assuming 'src' is in PYTHONPATH, making 'services' and 'shared' top-level packages
from src.services.llm_interface import LLMInterface
from src.shared.types.common_types import LLMInterfaceConfig # For default config typing


class DailyLanguageModel:
    def __init__(self, llm_interface: Optional[LLMInterface] = None, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        if llm_interface:
            self.llm_interface = llm_interface
        else:
            # Create a default LLMInterface if one isn't provided.
            # This default will use its own default (mock) configuration.
            print("DailyLanguageModel: No LLMInterface provided, creating default (mock-based).")
            self.llm_interface = LLMInterface()

        print("DailyLanguageModel: Initialized with LLMInterface.")

    def _construct_tool_selection_prompt(self, text: str, available_tools: Dict[str, str]) -> str:
        prompt = "You are an expert at routing user queries to the correct tool.\n"
        prompt += "Given the user query and a list of available tools, select the most appropriate tool and extract necessary parameters.\n"
        prompt += "If no tool is appropriate, respond with \"NO_TOOL\".\n\n"
        prompt += "Available tools:\n"
        for i, (tool_name, description) in enumerate(available_tools.items()):
            prompt += f"{i+1}. {tool_name}: {description}\n"

        prompt += f"\nUser Query: \"{text}\"\n\n"
        prompt += "Respond ONLY with a valid JSON object adhering to the following structure:\n"
        prompt += "{\n"
        prompt += "  \"tool_name\": \"<selected_tool_name_or_NO_TOOL>\",\n"
        prompt += "  \"parameters\": { <parameters_object_for_the_tool_OR_null_OR_empty_object> }\n" # Using {{}} for object placeholder in text
        prompt += "}\n\n"
        prompt += "Specific instructions for the 'parameters' object based on 'tool_name':\n"
        prompt += "- If 'NO_TOOL' is selected, 'parameters' should be null or an empty {}.\n"
        prompt += "- For 'calculate': 'parameters' must be an object like {\"query\": \"<the_full_arithmetic_expression_to_calculate>\"}. Example: {\"query\": \"2 + 2 / 5\"}.\n"
        prompt += "- For 'evaluate_logic': 'parameters' must be an object like {\"query\": \"<the_logical_expression_to_evaluate>\"}. If the user specifies an evaluation method (e.g., \"using nn\"), include {\"method\": \"nn\"}. Otherwise, you can omit 'method' or use {\"method\": \"parser\"}. Example: {\"query\": \"(true AND false) OR NOT true\"}.\n"
        prompt += "- For 'translate_text': 'parameters' must be an object containing {\"text_to_translate\": \"<text_to_be_translated>\"} and {\"target_language\": \"<target_language_code_or_name>\"}. If the user specifies a source language, also include {\"source_language\": \"<source_language_code_or_name>\"}. Example: {\"text_to_translate\": \"Hello world\", \"target_language\": \"Spanish\"}.\n\n"
        prompt += "Only include parameters relevant to the selected tool.\n"
        return prompt

    async def recognize_intent(self, text: str, available_tools: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Recognizes intent (primarily for tool dispatching) from input text using an LLM.
        Returns a dictionary like {"tool_name": "...", "parameters": {"query": "...", ...}}
        or {"tool_name": None, "parameters": None} if no tool is suitable.
        """
        if not available_tools:
            print("DLM: No available tools provided for intent recognition.")
            return {"tool_name": None, "parameters": None}

        prompt = self._construct_tool_selection_prompt(text, available_tools)

        print(f"DLM: Sending prompt to LLM for intent recognition:\n---\n{prompt}\n---")

        # Use the LLMInterface to generate the response
        # For mock testing, the mock LLM should be configured to respond in the expected JSON format for some inputs.
        llm_response_str = await self.llm_interface.generate_response(prompt)

        print(f"DLM: Received raw response from LLM:\n---\n{llm_response_str}\n---")

        try:
            # Attempt to parse the LLM's response as JSON
            parsed_response = json.loads(llm_response_str)

            tool_name = parsed_response.get("tool_name")
            parameters = parsed_response.get("parameters")

            if tool_name == "NO_TOOL" or not tool_name:
                print("DLM: LLM indicated no appropriate tool.")
                return {"tool_name": None, "parameters": None}

            if tool_name not in available_tools:
                print(f"DLM: Warning - LLM selected tool '{tool_name}' which is not in available_tools. Treating as no tool.")
                return {"tool_name": None, "parameters": None}

            # Ensure parameters is a dict, even if empty
            if parameters is None:
                parameters = {}

            print(f"DLM: Recognized intent: tool='{tool_name}', params='{parameters}'")
            return {"tool_name": tool_name, "parameters": parameters, "confidence": 0.9} # Confidence is high if LLM provides valid tool

        except json.JSONDecodeError:
            print(f"DLM: Error - Could not decode JSON response from LLM: {llm_response_str}")
            return {"tool_name": None, "parameters": None, "error": "LLM response not valid JSON"}
        except Exception as e:
            print(f"DLM: Error processing LLM response: {e}")
            return {"tool_name": None, "parameters": None, "error": str(e)}


if __name__ == '__main__':
    # For testing, LLMInterface will use its default mock configuration.
    # We need to ensure the mock LLMInterface's _get_mock_response can handle the intent prompt.

    # --- Update LLMInterface mock for DLM testing ---
    # This is a bit of a hack for standalone testing. Ideally, you'd configure the mock LLMInterface
    # when instantiating DailyLanguageModel for tests.

    class PatchedLLMInterface(LLMInterface):
        def _get_mock_response(self, prompt: str, model_name: Optional[str]) -> str:
            if "Available tools:" in prompt and "User Query:" in prompt:
                # Simulate LLM recognizing tools based on refined prompt instructions
                if "calculate 2 + 2" in prompt or "what is 10 times 5" in prompt :
                    # Extract the actual expression for the "query" parameter
                    query_text_match = re.search(r"User Query: \"(.*?)\"", prompt)
                    original_query = query_text_match.group(1) if query_text_match else ""

                    expression = original_query # Default to original if specific extraction fails
                    if "calculate" in original_query.lower():
                        expression = original_query.lower().split("calculate")[-1].strip()
                    elif "what is" in original_query.lower():
                         expression = original_query.lower().split("what is")[-1].strip()
                    elif "times" in original_query.lower() or "+" in original_query or "-" in original_query or "/" in original_query:
                        # Keep it simple, assume it's mostly the expression
                        expression = original_query

                    return json.dumps({"tool_name": "calculate", "parameters": {"query": expression.strip("?")}})

                elif "evaluate true and false" in prompt or "logic of (true or not false)" in prompt :
                    query_text_match = re.search(r"User Query: \"(.*?)\"", prompt)
                    original_query = query_text_match.group(1) if query_text_match else ""
                    expression = original_query
                    method = "parser"
                    if "evaluate" in original_query.lower():
                        expression = original_query.lower().split("evaluate")[-1].strip()
                    elif "logic of" in original_query.lower():
                        expression = original_query.lower().split("logic of")[-1].strip()
                    if "using nn" in original_query.lower():
                        method = "nn"
                        expression = expression.replace("using nn", "").strip()

                    return json.dumps({"tool_name": "evaluate_logic",
                                       "parameters": {"query": expression, "method": method}})

                elif "translate hello to chinese" in prompt:
                    return json.dumps({"tool_name": "translate_text",
                                       "parameters": {"text_to_translate": "hello",
                                                      "target_language": "chinese"}})
                elif "translate 'good morning' to spanish" in prompt:
                     return json.dumps({"tool_name": "translate_text",
                                       "parameters": {"text_to_translate": "good morning",
                                                      "target_language": "spanish"}})
                elif "my text in english" in prompt: # Example of less clear intent for translation tool
                     return json.dumps({"tool_name": "translate_text",
                                        "parameters": {"text_to_translate": "my text",
                                                       "target_language": "english"}})
                elif "translate 'bonjour' from french to english" in prompt.lower():
                    return json.dumps({"tool_name": "translate_text",
                                       "parameters": {"text_to_translate": "bonjour",
                                                      "source_language": "french",
                                                      "target_language": "english"}})

                # NO_TOOL examples
                elif "what is the capital of france" in prompt.lower():
                    return json.dumps({"tool_name": "NO_TOOL", "parameters": {}}) # Empty object for parameters
                elif "how are you" in prompt.lower():
                    return json.dumps({"tool_name": "NO_TOOL", "parameters": {}})
                elif "tell me a joke" in prompt.lower():
                    return json.dumps({"tool_name": "NO_TOOL", "parameters": None}) # Testing None for parameters (json.dumps converts to null)

                # Variations for existing tools
                elif "compute 15 / 3" in prompt.lower() or "what's 7 minus 2" in prompt.lower():
                    query_text_match = re.search(r"User Query: \"(.*?)\"", prompt)
                    original_query = query_text_match.group(1) if query_text_match else ""
                    expression = original_query
                    if "compute" in original_query.lower(): expression = original_query.lower().split("compute")[-1].strip()
                    elif "what's" in original_query.lower(): expression = original_query.lower().split("what's")[-1].strip()
                    return json.dumps({"tool_name": "calculate", "parameters": {"query": expression.strip("?")}})

                elif "is (true or false) and true true" in prompt.lower():
                     # More complex extraction, assume LLM gets it right for mock
                    return json.dumps({"tool_name": "evaluate_logic",
                                       "parameters": {"query": "(true or false) and true", "method": "parser"}})

                else:
                    # Default for queries not specifically handled above by PatchedLLMInterface
                    print(f"PatchedLLMInterface: No specific mock rule for prompt containing: '{prompt[:100]}...' Returning NO_TOOL.")
                    return json.dumps({"tool_name": "NO_TOOL", "parameters": {}}) # Default to empty object

            # Fallback to super if not a tool selection prompt (e.g. direct LLMInterface tests)
            return super()._get_mock_response(prompt, model_name)

    print("\n--- DailyLanguageModel with LLMInterface (Mocked) Test ---")
    # Provide a specific LLMInterfaceConfig for the mock to use a specific model for DLM
    mock_llm_config_for_dlm: LLMInterfaceConfig = { #type: ignore
        "default_provider": "mock",
        "default_model": "dlm-intent-mock", # Specific mock model for this test
        "providers": {},
        "default_generation_params": {}
    }
    # Use the patched interface for testing
    dlm = DailyLanguageModel(llm_interface=PatchedLLMInterface(config=mock_llm_config_for_dlm))

    # Mock available_tools as ToolDispatcher().get_available_tools() would provide
    # This is needed for dlm.recognize_intent(query, available_tools)
    mock_available_tools = {
        "calculate": "Performs arithmetic calculations. Example: 'calculate 10 + 5', or 'what is 20 / 4?'",
        "evaluate_logic": "Evaluates simple logical expressions (AND, OR, NOT, true, false, parentheses). Example: 'evaluate true AND (false OR NOT true)'",
        "translate_text": "Translates text between Chinese and English. Example: 'translate 你好 to English'",
    }

    queries_to_test = [
        # Original tests
        "calculate 2 + 2",
        "what is 10 times 5",
        "evaluate true and false",
        "logic of (true or not false)",
        "translate hello to chinese",
        "my text in english", # Already tests a slightly less direct translation intent
        "this is a normal sentence", # Should be NO_TOOL

        # New NO_TOOL examples
        "what is the capital of france", # Already in mock, should be NO_TOOL
        "how are you",
        "tell me a joke",

        # New variations for tools
        "compute 15 / 3",
        "what's 7 minus 2",
        "is (true or false) and true true",
        "translate 'bonjour' from French to English?"
    ]

    for query in queries_to_test:
        intent = dlm.recognize_intent(query, available_tools=mock_available_tools) # Pass available_tools
        print(f"Query: \"{query}\" -> Intent: {intent}")

    print("\nDailyLanguageModel placeholder script finished.")
