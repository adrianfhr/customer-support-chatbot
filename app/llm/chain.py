"""
LangChain chat chain configuration with Ollama integration
"""
import os
from typing import Any, Dict, List

import structlog
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import Tool

from app.core.memory import MemoryManager
from app.llm.prompts import format_prompt_with_context, get_fallback_response


class ChatChain:
    """
    LangChain chat chain for handling conversations with Ollama LLM.
    """
    
    def __init__(self):
        """Initialize the chat chain with Ollama model."""
        self.logger = structlog.get_logger(__name__)
        
        # Initialize Ollama chat model
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        model_name = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.4"))
        
        self.llm = ChatOllama(
            base_url=ollama_host,
            model=model_name,
            temperature=temperature,
            verbose=True,
        )
        
        self.logger.info(
            "Chat chain initialized",
            ollama_host=ollama_host,
            model=model_name,
            temperature=temperature
        )
    
    async def invoke(
        self,
        user_message: str,
        memory_context: List[Dict[str, str]],
        tools: List[Tool],
        session_id: str
    ) -> Dict[str, Any]:
        """
        Invoke the chat chain to generate a response.
        
        Args:
            user_message: User's input message
            memory_context: Previous conversation context
            tools: Available tools for the agent
            session_id: Session identifier for logging
            
        Returns:
            Dictionary containing response message and metadata
        """
        self.logger.info(
            "Invoking chat chain",
            session_id=session_id,
            message_preview=user_message[:50] + "..." if len(user_message) > 50 else user_message,
            memory_length=len(memory_context),
            tool_count=len(tools)
        )
        
        try:
            # Format memory context for prompt
            memory_manager = MemoryManager(None)  # We only need formatting method
            memory_text = memory_manager.format_memory_for_prompt(memory_context)
            
            # Create system prompt with context
            system_prompt = format_prompt_with_context(user_message, memory_text)
            
            # Check if we need to call tools
            tool_calls = []
            tool_results = {}
            
            # Simple keyword-based tool detection
            # In production, this would use LLM function calling
            if await self._should_call_order_tool(user_message):
                order_id = self._extract_order_id(user_message)
                if order_id:
                    order_tool = next((t for t in tools if t.name == "get_order_status"), None)
                    if order_tool:
                        result = await order_tool.func(order_id)
                        tool_results["order_status"] = result
                        tool_calls.append("get_order_status")

            elif await self._should_call_product_tool(user_message):
                product_name = self._extract_product_name(user_message)
                if product_name:
                    product_tool = next((t for t in tools if t.name == "get_product_info"), None)
                    if product_tool:
                        result = await product_tool.func(product_name)
                        tool_results["product_info"] = result
                        tool_calls.append("get_product_info")

            elif await self._should_call_warranty_tool(user_message):
                warranty_tool = next((t for t in tools if t.name == "get_warranty_policy"), None)
                if warranty_tool:
                    result = await warranty_tool.func()
                    tool_results["warranty_policy"] = result
                    tool_calls.append("get_warranty_policy")            # Generate response
            if tool_results:
                # If we have tool results, use them to formulate response
                response_message = await self._generate_response_with_tools(
                    user_message, tool_results, memory_text
                )
            else:
                # Generate regular conversational response
                response_message = await self._generate_regular_response(
                    user_message, memory_text
                )
            
            # Ensure response ends with "Ringkas: ..."
            if not response_message.strip().endswith("Ringkas:"):
                if "Ringkas:" not in response_message:
                    # Add a simple summary
                    response_message += f"\n\nRingkas: Sudah memberikan jawaban sesuai pertanyaan Anda."
            
            self.logger.info(
                "Chat chain response generated",
                session_id=session_id,
                tool_calls=tool_calls,
                response_length=len(response_message)
            )
            
            return {
                "message": response_message,
                "tool_calls": tool_calls,
                "session_id": session_id
            }
            
        except Exception as e:
            self.logger.error(
                "Chat chain invocation failed",
                session_id=session_id,
                error=str(e)
            )
            
            # Return fallback response
            return {
                "message": get_fallback_response(),
                "tool_calls": [],
                "session_id": session_id
            }
    
    async def _should_call_order_tool(self, message: str) -> bool:
        """Check if message requires order status lookup."""
        keywords = ["pesanan", "order", "status", "di mana", "dimana", "ID:", "id:", "ORD"]
        message_lower = message.lower()
        return any(keyword.lower() in message_lower for keyword in keywords)
    
    async def _should_call_product_tool(self, message: str) -> bool:
        """Check if message requires product information."""
        keywords = ["produk", "kelebihan", "fitur", "spesifikasi", "harga", "laptop", "smartphone", "apa kelebihan"]
        message_lower = message.lower()
        return any(keyword.lower() in message_lower for keyword in keywords)
    
    async def _should_call_warranty_tool(self, message: str) -> bool:
        """Check if message requires warranty information."""
        keywords = ["garansi", "warranty", "klaim", "cara klaim", "prosedur"]
        message_lower = message.lower()
        return any(keyword.lower() in message_lower for keyword in keywords)
    
    def _extract_order_id(self, message: str) -> str:
        """Extract order ID from message."""
        import re
        
        # Look for patterns like "ID: ORD123", "id: ORD123", "ORD123"
        patterns = [
            r"ID\s*:\s*([A-Z0-9]+)",
            r"id\s*:\s*([A-Z0-9]+)",
            r"\b(ORD[A-Z0-9]+)\b",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ""
    
    def _extract_product_name(self, message: str) -> str:
        """Extract product name from message."""
        # Simple extraction - look for common product terms
        import re
        
        # Look for product mentions
        patterns = [
            r"produk\s+([A-Za-z0-9\s]+?)[\?\.]",
            r"laptop\s+([A-Za-z0-9\s]+?)[\?\.]",
            r"smartphone\s+([A-Za-z0-9\s]+?)[\?\.]",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback - extract anything after "produk" or similar keywords
        keywords = ["produk", "laptop", "smartphone"]
        for keyword in keywords:
            if keyword.lower() in message.lower():
                # Try to extract word after keyword
                parts = message.lower().split(keyword.lower())
                if len(parts) > 1:
                    candidate = parts[1].strip().split()[0:3]  # Take first 3 words
                    return " ".join(candidate).strip(".,?!")
        
        return "produk"
    
    async def _generate_response_with_tools(
        self,
        user_message: str,
        tool_results: Dict[str, str],
        memory_context: str
    ) -> str:
        """Generate response incorporating tool results."""
        
        # For now, return the tool result directly since it's already well-formatted
        if "order_status" in tool_results:
            result = tool_results["order_status"]
            if not result.endswith("Ringkas:"):
                result += "\n\nRingkas: Informasi pesanan telah ditemukan dan disampaikan."
            return result
        
        elif "product_info" in tool_results:
            result = tool_results["product_info"]
            if not result.endswith("Ringkas:"):
                result += "\n\nRingkas: Informasi produk telah disampaikan dengan lengkap."
            return result
        
        elif "warranty_policy" in tool_results:
            result = tool_results["warranty_policy"]
            if not result.endswith("Ringkas:"):
                result += "\n\nRingkas: Prosedur klaim garansi telah dijelaskan lengkap."
            return result
        
        return "Maaf, terjadi kesalahan dalam memproses permintaan Anda."
    
    async def _generate_regular_response(
        self,
        user_message: str,
        memory_context: str
    ) -> str:
        """Generate regular conversational response using LLM."""
        try:
            # Create messages for LLM
            messages = [
                SystemMessage(content=format_prompt_with_context(user_message, memory_context)),
                HumanMessage(content=user_message)
            ]
            
            # Get LLM response
            response = await self.llm.ainvoke(messages)
            
            return response.content
            
        except Exception as e:
            self.logger.error("LLM generation failed", error=str(e))
            return get_fallback_response()
