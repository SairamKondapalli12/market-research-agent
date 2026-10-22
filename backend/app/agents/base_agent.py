"""Abstract base class for all AI agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.config.logging_config import get_logger
from app.database.models.agent_log_event import AgentLogEvent
from app.database.session import SessionLocal
from app.services.event_bus_service import publish_event

logger = get_logger(__name__)


class BaseAgent(ABC):
    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        llm: Any = None,
        tools: Optional[List[Any]] = None,
        verbose: bool = False,
        request_id: Optional[UUID | str] = None,
    ):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.llm = llm
        self.tools = tools or []
        self.verbose = verbose
        self.request_id = request_id
        self._logger = get_logger(f"agent.{name}")

    def log(
        self,
        message: str,
        level: str = "info",
        progress: Optional[int] = None,
    ) -> None:
        """
        Record an agent event three ways:
          1. Python logger (backend terminal)
          2. Redis pub/sub (live WebSocket stream)
          3. Database (historical replay)
        """
        # 1. Standard logging
        log_fn = getattr(self._logger, level, self._logger.info)
        log_fn(f"[{self.name}] {message}")

        if not self.request_id:
            return

        # 2. Publish to Redis (best-effort, never crashes)
        publish_event(
            request_id=self.request_id,
            agent=self.name,
            message=message,
            level=level,
            progress=progress,
        )

        # 3. Persist to DB (best-effort, never crashes)
        try:
            db = SessionLocal()
            try:
                last = (
                    db.query(AgentLogEvent)
                    .filter(AgentLogEvent.request_id == self.request_id)
                    .order_by(AgentLogEvent.sequence.desc())
                    .first()
                )
                seq = (last.sequence + 1) if last else 0

                db.add(
                    AgentLogEvent(
                        request_id=self.request_id,
                        agent=self.name,
                        level=level,
                        message=message,
                        progress=progress,
                        sequence=seq,
                    )
                )
                db.commit()
            finally:
                db.close()
        except Exception as exc:
            logger.warning(f"Failed to persist agent log: {exc}")

    @abstractmethod
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} role={self.role}>"