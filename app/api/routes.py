"""
API Routes for Customer Support Chatbot
"""
import uuid
from datetime import datetime
from typing import List

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    MessageHistoryResponse,
    MessageResponse,
    SeedOrdersRequest,
)
from app.core.chat_service import ChatService
from app.db.models import Message, Order
from app.db.session import get_db_session

# Create router
router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/healthz", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db_session)
) -> ChatResponse:
    """
    Handle chat conversation with the AI assistant.
    
    Args:
        request: Chat request containing session_id and user_message
        db: Database session
        
    Returns:
        ChatResponse with assistant's reply and metadata
    """
    logger.info(
        "Chat request received",
        session_id=request.session_id,
        message_length=len(request.user_message)
    )
    
    try:
        # Initialize chat service
        chat_service = ChatService(db)
        
        # Process the message
        response = await chat_service.process_message(
            session_id=request.session_id,
            user_message=request.user_message
        )
        
        logger.info(
            "Chat response generated",
            session_id=request.session_id,
            turn_index=response.turn_index,
            tool_calls=response.tool_calls
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "Chat processing failed",
            session_id=request.session_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.get("/sessions/{session_id}/messages", response_model=MessageHistoryResponse)
async def get_session_messages(
    session_id: str,
    db: AsyncSession = Depends(get_db_session)
) -> MessageHistoryResponse:
    """
    Retrieve conversation history for a session.
    
    Args:
        session_id: Session identifier
        db: Database session
        
    Returns:
        MessageHistoryResponse with conversation history
    """
    logger.info("Retrieving session messages", session_id=session_id)
    
    try:
        # Query messages for session
        from sqlalchemy import select
        
        stmt = (
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.turn_index, Message.created_at)
        )
        result = await db.execute(stmt)
        messages = result.scalars().all()
        
        # Convert to response format
        message_responses = [
            MessageResponse(
                role=msg.role,
                content=msg.content,
                turn_index=msg.turn_index,
                timestamp=msg.created_at
            )
            for msg in messages
        ]
        
        logger.info(
            "Session messages retrieved",
            session_id=session_id,
            message_count=len(message_responses)
        )
        
        return MessageHistoryResponse(
            session_id=session_id,
            messages=message_responses
        )
        
    except Exception as e:
        logger.error(
            "Failed to retrieve session messages",
            session_id=session_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve session messages: {str(e)}"
        )


@router.post("/orders/seed")
async def seed_orders(
    request: SeedOrdersRequest,
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Seed database with demo order data.
    
    Args:
        request: Request containing orders to seed
        db: Database session
        
    Returns:
        Success message with count of created orders
    """
    logger.info("Seeding orders", order_count=len(request.orders))
    
    try:
        created_orders = []
        
        for order_data in request.orders:
            # Create order instance
            order = Order(
                id=order_data.id,
                user_id=order_data.user_id,
                status=order_data.status,
                last_update_at=order_data.last_update_at or datetime.utcnow(),
                eta_date=order_data.eta_date,
                carrier=order_data.carrier,
                tracking_number=order_data.tracking_number
            )
            
            db.add(order)
            created_orders.append(order.id)
        
        await db.commit()
        
        logger.info(
            "Orders seeded successfully",
            created_count=len(created_orders),
            order_ids=created_orders
        )
        
        return {
            "message": f"Successfully created {len(created_orders)} orders",
            "order_ids": created_orders
        }
        
    except Exception as e:
        await db.rollback()
        logger.error("Failed to seed orders", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to seed orders: {str(e)}"
        )
