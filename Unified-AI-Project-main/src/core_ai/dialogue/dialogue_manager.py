from __future__ import annotations
import asyncio
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple, TYPE_CHECKING
import uuid
import os
import re
import ast

from src.core_ai.personality.personality_manager import PersonalityManager
from src.core_ai.memory.ham_memory_manager import HAMMemoryManager
from src.services.llm_interface import LLMInterface
from src.core_ai.emotion_system import EmotionSystem
from src.core_ai.crisis_system import CrisisSystem
from src.core_ai.time_system import TimeSystem
from src.core_ai.formula_engine import FormulaEngine
from src.tools.tool_dispatcher import ToolDispatcher
from src.core_ai.learning.learning_manager import LearningManager
from src.core_ai.service_discovery.service_discovery_module import ServiceDiscoveryModule
from src.services.sandbox_executor import SandboxExecutor
import networkx as nx
from src.shared.types.common_types import (
    OperationalConfig, DialogueTurn, DialogueMemoryEntryMetadata
)

from src.hsp.types import HSPTaskResultPayload, HSPMessageEnvelope
from src.core_ai.dialogue.project_coordinator import ProjectCoordinator
from src.core_ai.agent_manager import AgentManager

if TYPE_CHECKING:
    from src.hsp.connector import HSPConnector

class DialogueManager:
    def __init__(self,
                 ai_id: str,
                 personality_manager: PersonalityManager,
                 memory_manager: HAMMemoryManager,
                 llm_interface: LLMInterface,
                 emotion_system: EmotionSystem,
                 crisis_system: CrisisSystem,
                 time_system: TimeSystem,
                 formula_engine: FormulaEngine,
                 tool_dispatcher: ToolDispatcher,
                 learning_manager: LearningManager,
                 service_discovery_module: ServiceDiscoveryModule,
                 hsp_connector: Optional[HSPConnector],
                 agent_manager: Optional[AgentManager],
                 config: Optional[OperationalConfig] = None,
                 **kwargs): # Catch other services that might be passed

        self.ai_id = ai_id
        self.personality_manager = personality_manager
        self.memory_manager = memory_manager
        self.llm_interface = llm_interface
        self.emotion_system = emotion_system
        self.crisis_system = crisis_system
        self.time_system = time_system
        self.formula_engine = formula_engine
        self.tool_dispatcher = tool_dispatcher
        self.learning_manager = learning_manager
        self.service_discovery = service_discovery_module # Store service_discovery_module
        self.hsp_connector = hsp_connector # Store hsp_connector
        self.config = config or {}

        # Load command triggers from config with defaults
        self.triggers = self.config.get("command_triggers", {
            "complex_project": "project:",
            "manual_delegation": "!delegate_to",
            "context_analysis": "!analyze:"
        })

        self.active_sessions: Dict[str, List[DialogueTurn]] = {}
        self.pending_hsp_task_requests: Dict[str, Dict[str, Any]] = {} # Initialize pending_hsp_task_requests
        
        # Initialize ProjectCoordinator
        self.project_coordinator = ProjectCoordinator(
            llm_interface=self.llm_interface,
            service_discovery=self.service_discovery,
            hsp_connector=self.hsp_connector,
            agent_manager=agent_manager,
            memory_manager=self.memory_manager,
            learning_manager=self.learning_manager,
            personality_manager=self.personality_manager,
            dialogue_manager_config=self.config
        )

        if self.hsp_connector:
            self.hsp_connector.register_on_task_result_callback(self._handle_incoming_hsp_task_result)

    async def _handle_incoming_hsp_task_result(self, result_payload: HSPTaskResultPayload, sender_ai_id: str, envelope: HSPMessageEnvelope) -> None:
        """
        Receives all task results and delegates them to the ProjectCoordinator.
        """
        if self.project_coordinator:
            await self.project_coordinator.handle_task_result(result_payload, sender_ai_id, envelope)
        else:
            print(f"[{self.ai_id}] Warning: Received HSP task result but ProjectCoordinator is not available.")

    async def get_simple_response(self, user_input: str, session_id: Optional[str] = None, user_id: Optional[str] = None) -> str:
        ai_name = self.personality_manager.get_current_personality_trait("display_name", "AI")

        # --- Intent Classification ---
        # Use triggers from config to activate special handlers
        if self.project_coordinator and user_input.lower().startswith(self.triggers["complex_project"]):
            project_query = user_input[len(self.triggers["complex_project"]):].strip()
            print(f"[{self.ai_id}] Complex project detected. Delegating to ProjectCoordinator...")
            return await self.project_coordinator.handle_project(project_query, session_id, user_id)

        # --- Existing Simple Response Flow ---
        # This is a simplified version of the original extensive logic.
        # A full implementation would include formula matching, single tool dispatch, etc.
        
        # Attempt to dispatch a tool based on user input
        tool_response = await self.tool_dispatcher.dispatch(user_input, session_id=session_id, user_id=user_id)

        response_text = ""
        if tool_response['status'] == "success":
            response_text = tool_response['payload']
        elif tool_response['status'] == "no_tool_found" or tool_response['status'] == "no_tool_inferred":
            response_text = f"{ai_name}: You said '{user_input}'. This is a simple response."
        else:
            response_text = f"{ai_name}: An error occurred while processing your request: {tool_response['error_message']}"

        # Store user and AI turns in memory
        if self.memory_manager:
            user_metadata: DialogueMemoryEntryMetadata = {"speaker": "user", "timestamp": datetime.now(timezone.utc).isoformat(), "user_id": user_id, "session_id": session_id} # type: ignore
            user_mem_id = self.memory_manager.store_experience(user_input, "user_dialogue_text", user_metadata)

            ai_metadata: DialogueMemoryEntryMetadata = {"speaker": "ai", "timestamp": datetime.now(timezone.utc).isoformat(), "user_id": user_id, "session_id": session_id, "user_input_ref": user_mem_id} # type: ignore
            self.memory_manager.store_experience(response_text, "ai_dialogue_text", ai_metadata)

        # Analyze for personality adjustment
        if self.learning_manager:
            adjustment = await self.learning_manager.analyze_for_personality_adjustment(user_input)
            if adjustment and self.personality_manager:
                self.personality_manager.apply_personality_adjustment(adjustment)

        return response_text

    async def start_session(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> str:
        print(f"DialogueManager: New session started for user '{user_id or 'anonymous'}', session_id: {session_id}.")
        if session_id: self.active_sessions[session_id] = []
        base_prompt = self.personality_manager.get_initial_prompt()
        time_segment = self.time_system.get_time_of_day_segment()
        greetings = {"morning": "Good morning!", "afternoon": "Good afternoon!", "evening": "Good evening!", "night": "Hello,"}
        return f"{greetings.get(time_segment, '')} {base_prompt}".strip()