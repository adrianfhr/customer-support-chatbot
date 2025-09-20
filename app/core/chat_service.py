"""
Core chat service handling conversation flow and memory management
"""
import uuid
from datetime import datetime
from typing import List

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import ChatResponse
from app.core.memory import MemoryManager
from app.core.tools import get_tools
from app.db.models import Message
from app.llm.chain import ChatChain


class ChatService:
    """
    Core service for handling chat conversations with memory and tool calling.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize chat service.
        
        Args:
            db_session: Database session for persistence
        """
        self.db_session = db_session
        self.memory_manager = MemoryManager(db_session)
        self.chat_chain = ChatChain()
        self.logger = structlog.get_logger(__name__)
    
    async def process_message(
        self,
        session_id: str,
        user_message: str
    ) -> ChatResponse:
        """
        Process user message and generate assistant response.
        
        Args:
            session_id: Session identifier
            user_message: User's input message
            
        Returns:
            ChatResponse with assistant reply and metadata
        """
        self.logger.info(
            "Processing message",
            session_id=session_id,
            message_preview=user_message[:50] + "..." if len(user_message) > 50 else user_message
        )
        
        try:
            # Get next turn index
            turn_index = await self._get_next_turn_index(session_id)
            
            # Save user message
            user_msg = await self._save_message(
                session_id=session_id,
                role="user",
                content=user_message,
                turn_index=turn_index
            )
            
            # Get conversation memory
            memory_context = await self.memory_manager.get_memory_context(session_id)
            
            # Prepare tools
            tools = get_tools(self.db_session)
            
            # Generate response using LLM chain
            llm_response = await self.chat_chain.invoke(
                user_message=user_message,
                memory_context=memory_context,
                tools=tools,
                session_id=session_id
            )
            
            # Extract response data
            assistant_message = llm_response["message"]
            tool_calls = llm_response.get("tool_calls", [])
            
            # Save assistant message
            assistant_msg = await self._save_message(
                session_id=session_id,
                role="assistant",
                content=assistant_message,
                turn_index=turn_index
            )
            
            # Update memory
            await self.memory_manager.update_memory(
                session_id=session_id,
                user_message=user_message,
                assistant_message=assistant_message,
                turn_index=turn_index
            )
            
            self.logger.info(
                "Message processed successfully",
                session_id=session_id,
                turn_index=turn_index,
                tool_calls=tool_calls
            )
            
            return ChatResponse(
                message=assistant_message,
                session_id=session_id,
                turn_index=turn_index,
                tool_calls=tool_calls,
                timestamp=assistant_msg.created_at
            )
            
        except Exception as e:
            await self.db_session.rollback()
            self.logger.error(
                "Failed to process message",
                session_id=session_id,
                error=str(e)
            )
            raise
    
    async def _get_next_turn_index(self, session_id: str) -> int:
        """
        Get the next turn index for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Next turn index
        """
        from sqlalchemy import select, func
        
        stmt = (
            select(func.max(Message.turn_index))
            .where(Message.session_id == session_id)
        )
        result = await self.db_session.execute(stmt)
        max_turn = result.scalar()
        
        return (max_turn or 0) + 1
    
    async def _save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        turn_index: int
    ) -> Message:
        """
        Save message to database.
        
        Args:
            session_id: Session identifier
            role: Message role (user/assistant)
            content: Message content
            turn_index: Turn index in conversation
            
        Returns:
            Saved message instance
        """
        message = Message(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            turn_index=turn_index,
            created_at=datetime.utcnow()
        )
        
        self.db_session.add(message)
        await self.db_session.commit()
        await self.db_session.refresh(message)
        
        return message
