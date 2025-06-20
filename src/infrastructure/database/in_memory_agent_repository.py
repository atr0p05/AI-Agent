from examples.enhanced_unified_example import metrics
from examples.parallel_execution_example import agents
from performance_dashboard import stats

from src.agents.enhanced_fsm import state
from src.core.entities.agent import Agent
from src.database.models import agent_id
from src.database.models import agent_type
from src.gaia_components.multi_agent_orchestrator import available_agents
from src.infrastructure.database.in_memory_agent_repository import agent_state
from src.infrastructure.database.in_memory_agent_repository import agents_by_state
from src.infrastructure.database.in_memory_agent_repository import agents_by_type
from src.infrastructure.database.in_memory_agent_repository import total_agents

from src.agents.advanced_agent_fsm import AgentType

from src.agents.advanced_agent_fsm import Agent
# TODO: Fix undefined variables: Any, Dict, List, Optional, UUID, agent_id, agent_state, agent_type, agents, agents_by_state, agents_by_type, available_agents, datetime, e, logging, metrics, state, stats, total_agents, uuid4
from tests.test_gaia_agent import agent

from src.core.entities.agent import AgentType


"""
from typing import Optional
from src.agents.multi_agent_system import AgentState
from src.gaia_components.multi_agent_orchestrator import Agent
from src.infrastructure.agents.agent_factory import AgentType
from uuid import uuid4
# TODO: Fix undefined variables: agent, agent_id, agent_state, agent_type, agents, agents_by_state, agents_by_type, available_agents, e, metrics, self, state, stats, total_agents

In-memory implementation of the agent repository.
"""

from typing import Dict
from typing import Any

from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
import logging
from datetime import datetime

from src.core.interfaces.agent_repository import AgentRepository
from src.core.entities.agent import Agent, AgentType, AgentState
from src.shared.exceptions import InfrastructureException

class InMemoryAgentRepository(AgentRepository):
    """
    In-memory implementation of the agent repository.

    This implementation stores agents in memory and is suitable
    for development and testing purposes.
    """

    def __init__(self) -> None:
        self._agents: Dict[UUID, Agent] = {}
        self.logger = logging.getLogger(__name__)

    async def save(self, agent: Agent) -> Agent:
        """Save an agent to the repository."""
        try:
            if not agent.id:
                agent.id = uuid4()
                agent.created_at = datetime.utcnow()

            agent.updated_at = datetime.utcnow()
            self._agents[agent.id] = agent

            self.logger.debug("Saved agent {} of type {}", extra={"agent_id": agent.id, "agent_agent_type": agent.agent_type})
            return agent

        except Exception as e:
            self.logger.error("Failed to save agent: {}", extra={"str_e_": str(e)})
            raise InfrastructureException(f"Failed to save agent: {str(e)}")

    async def find_by_id(self, agent_id: UUID) -> Optional[Agent]:
        """Find an agent by its ID."""
        try:
            agent = self._agents.get(agent_id)
            if agent:
                self.logger.debug("Found agent {}", extra={"agent_id": agent_id})
            return agent

        except Exception as e:
            self.logger.error("Failed to find agent {}: {}", extra={"agent_id": agent_id, "str_e_": str(e)})
            raise InfrastructureException(f"Failed to find agent {agent_id}: {str(e)}")

    async def find_by_type(self, agent_type: AgentType) -> List[Agent]:
        """Find all agents of a specific type."""
        try:
            agents = [agent for agent in self._agents.values() if agent.agent_type == agent_type]
            self.logger.debug("Found {} agents of type {}", extra={"len_agents_": len(agents), "agent_type": agent_type})
            return agents

        except Exception as e:
            self.logger.error("Failed to find agents of type {}: {}", extra={"agent_type": agent_type, "str_e_": str(e)})
            raise InfrastructureException(f"Failed to find agents of type {agent_type}: {str(e)}")

    async def find_available(self) -> List[Agent]:
        """Find all available agents (not busy)."""
        try:
            available_agents = [
                agent for agent in self._agents.values()
                if agent.state == AgentState.IDLE or agent.state == AgentState.READY
            ]
            self.logger.debug("Found {} available agents", extra={"len_available_agents_": len(available_agents)})
            return available_agents

        except Exception as e:
            self.logger.error("Failed to find available agents: {}", extra={"str_e_": str(e)})
            raise InfrastructureException(f"Failed to find available agents: {str(e)}")

    async def update_state(self, agent_id: UUID, state: AgentState) -> bool:
        """Update an agent's state."""
        try:
            if agent_id not in self._agents:
                self.logger.warning("Agent {} not found for state update", extra={"agent_id": agent_id})
                return False

            self._agents[agent_id].state = state
            self._agents[agent_id].updated_at = datetime.utcnow()

            self.logger.debug("Updated agent {} state to {}", extra={"agent_id": agent_id, "state": state})
            return True

        except Exception as e:
            self.logger.error("Failed to update agent {} state: {}", extra={"agent_id": agent_id, "str_e_": str(e)})
            raise InfrastructureException(f"Failed to update agent {agent_id} state: {str(e)}")

    async def update_performance_metrics(self, agent_id: UUID, metrics: Dict[str, Any]) -> bool:
        """Update an agent's performance metrics."""
        try:
            if agent_id not in self._agents:
                self.logger.warning("Agent {} not found for metrics update", extra={"agent_id": agent_id})
                return False

            agent = self._agents[agent_id]
            if not hasattr(agent, 'performance_metrics'):
                agent.performance_metrics = {}

            agent.performance_metrics.update(metrics)
            agent.updated_at = datetime.utcnow()

            self.logger.debug("Updated performance metrics for agent {}", extra={"agent_id": agent_id})
            return True

        except Exception as e:
            self.logger.error("Failed to update metrics for agent {}: {}", extra={"agent_id": agent_id, "str_e_": str(e)})
            raise InfrastructureException(f"Failed to update metrics for agent {agent_id}: {str(e)}")

    async def delete(self, agent_id: UUID) -> bool:
        """Delete an agent from the repository."""
        try:
            if agent_id not in self._agents:
                self.logger.warning("Agent {} not found for deletion", extra={"agent_id": agent_id})
                return False

            del self._agents[agent_id]
            self.logger.debug("Deleted agent {}", extra={"agent_id": agent_id})
            return True

        except Exception as e:
            self.logger.error("Failed to delete agent {}: {}", extra={"agent_id": agent_id, "str_e_": str(e)})
            raise InfrastructureException(f"Failed to delete agent {agent_id}: {str(e)}")

    async def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics."""
        try:
            total_agents = len(self._agents)
            agents_by_type = {}
            agents_by_state = {}

            for agent in self._agents.values():
                # Count by type
                agent_type = agent.agent_type.value
                agents_by_type[agent_type] = agents_by_type.get(agent_type, 0) + 1

                # Count by state
                agent_state = agent.state.value
                agents_by_state[agent_state] = agents_by_state.get(agent_state, 0) + 1

            stats = {
                "total_agents": total_agents,
                "agents_by_type": agents_by_type,
                "agents_by_state": agents_by_state,
                "created_at": datetime.utcnow().isoformat()
            }

            self.logger.debug("Generated statistics: {}", extra={"stats": stats})
            return stats

        except Exception as e:
            self.logger.error("Failed to get statistics: {}", extra={"str_e_": str(e)})
            raise InfrastructureException(f"Failed to get statistics: {str(e)}")