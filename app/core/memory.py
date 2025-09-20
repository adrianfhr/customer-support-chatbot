"""
Memory management for conversation context and history
"""
import os
from typing import Dict, List

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Message


class MemoryManager:
    """
    Manages conversation memory and context for chat sessions.
    Implements sliding window memory keeping last N exchanges.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize memory manager.
        
        Args:
            db_session: Database session for querying history
        """
        self.db_session = db_session
        self.max_exchanges = int(os.getenv("MAX_MEMORY_EXCHANGES", "3"))
        self.logger = structlog.get_logger(__name__)
    
    async def get_memory_context(self, session_id: str) -> List[Dict[str, str]]:
        """
        Retrieve memory context for a session (last N exchanges).
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of message dictionaries with role and content
        """
        self.logger.info(
            "Retrieving memory context",
            session_id=session_id,
            max_exchanges=self.max_exchanges
        )
        
        try:
            # Get last N exchanges (N user-assistant pairs)
            # Each exchange = 1 user message + 1 assistant message
            max_turns = self.max_exchanges
            
            stmt = (
                select(Message)
                .where(Message.session_id == session_id)
                .order_by(Message.turn_index.desc(), Message.created_at.desc())
                .limit(max_turns * 2)  # 2 messages per exchange
            )
            
            result = await self.db_session.execute(stmt)
            messages = result.scalars().all()
            
            # Reverse to get chronological order
            messages = list(reversed(messages))
            
            # Convert to context format
            context = []
            for msg in messages:
                context.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            self.logger.info(
                "Memory context retrieved",
                session_id=session_id,
                message_count=len(context)
            )
            
            return context
            
        except Exception as e:
            self.logger.error(
                "Failed to retrieve memory context",
                session_id=session_id,
                error=str(e)
            )
            return []
    
    async def update_memory(
        self,
        session_id: str,
        user_message: str,
        assistant_message: str,
        turn_index: int
    ) -> None:
        """
        Update memory after a new exchange.
        This is a no-op since we retrieve fresh from DB each time,
        but could be extended for in-memory caching.
        
        Args:
            session_id: Session identifier
            user_message: User's message
            assistant_message: Assistant's response
            turn_index: Turn index for this exchange
        """
        self.logger.debug(
            "Memory updated",
            session_id=session_id,
            turn_index=turn_index
        )
        # No-op for now since we query fresh from DB
        pass
    
    async def clear_memory(self, session_id: str) -> None:
        """
        Clear all memory for a session.
        
        Args:
            session_id: Session identifier to clear
        """
        self.logger.info("Clearing memory", session_id=session_id)
        
        try:
            # Delete all messages for session
            from sqlalchemy import delete
            
            stmt = delete(Message).where(Message.session_id == session_id)
            await self.db_session.execute(stmt)
            await self.db_session.commit()
            
            self.logger.info("Memory cleared", session_id=session_id)
            
        except Exception as e:
            await self.db_session.rollback()
            self.logger.error(
                "Failed to clear memory",
                session_id=session_id,
                error=str(e)
            )
            raise
    
    def format_memory_for_prompt(self, context: List[Dict[str, str]]) -> str:
        """
        Format memory context for inclusion in LLM prompt.
        
        Args:
            context: List of message dictionaries
            
        Returns:
            Formatted string for prompt inclusion
        """
        if not context:
            return "Tidak ada riwayat percakapan sebelumnya."
        
        formatted_lines = []
        formatted_lines.append("Riwayat percakapan sebelumnya:")
        
        for msg in context:
            role_label = "Pengguna" if msg["role"] == "user" else "Asisten"
            formatted_lines.append(f"{role_label}: {msg['content']}")
        
        return "\n".join(formatted_lines)
