"""
Pydantic schemas for API request/response models
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    session_id: str = Field(..., min_length=1, max_length=255, description="Session identifier")
    user_message: str = Field(..., min_length=1, max_length=2000, description="User's message")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    message: str = Field(..., description="Assistant's response message")
    session_id: str = Field(..., description="Session identifier")
    turn_index: int = Field(..., description="Turn index in conversation")
    tool_calls: List[str] = Field(default_factory=list, description="List of tools called")
    timestamp: datetime = Field(..., description="Response timestamp")


class MessageResponse(BaseModel):
    """Response model for individual message."""
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    turn_index: int = Field(..., description="Turn index in conversation")
    timestamp: datetime = Field(..., description="Message timestamp")


class MessageHistoryResponse(BaseModel):
    """Response model for message history."""
    session_id: str = Field(..., description="Session identifier")
    messages: List[MessageResponse] = Field(..., description="List of messages")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str = Field(..., description="API version")


class OrderSeedData(BaseModel):
    """Model for order seed data."""
    id: str = Field(..., description="Order ID")
    user_id: str = Field(..., description="User ID")
    status: str = Field(..., description="Order status")
    last_update_at: Optional[datetime] = Field(None, description="Last update timestamp")
    eta_date: Optional[datetime] = Field(None, description="Estimated delivery date")
    carrier: Optional[str] = Field(None, description="Shipping carrier")
    tracking_number: Optional[str] = Field(None, description="Tracking number")


class SeedOrdersRequest(BaseModel):
    """Request model for seeding orders."""
    orders: List[OrderSeedData] = Field(..., description="List of orders to seed")
