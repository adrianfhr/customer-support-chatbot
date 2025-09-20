"""
Tool functions for LangChain agent to handle specific user intents
"""
from datetime import datetime
from typing import Dict, List

import structlog
from langchain_core.tools import Tool
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Order, Product, Policy


logger = structlog.get_logger(__name__)


async def get_order_status_impl(order_id: str, db_session: AsyncSession) -> str:
    """
    Implementation function for order status lookup.
    
    Args:
        order_id: Order ID to look up
        db_session: Database session
        
    Returns:
        Formatted order status information
    """
    try:
        logger.info("Looking up order status", order_id=order_id)
        
        # Query order from database
        stmt = select(Order).where(Order.id == order_id)
        result = await db_session.execute(stmt)
        order = result.scalar_one_or_none()
        
        if not order:
            return f"Pesanan dengan ID {order_id} tidak ditemukan. Pastikan ID pesanan benar atau hubungi customer service."
        
        # Format response based on order status
        status_messages = {
            "pending": "sedang diproses",
            "confirmed": "telah dikonfirmasi",
            "shipped": "sedang dalam pengiriman",
            "delivered": "telah sampai tujuan",
            "cancelled": "telah dibatalkan"
        }
        
        status_text = status_messages.get(order.status, order.status)
        
        response_parts = [f"Pesanan {order_id} {status_text}"]
        
        if order.carrier and order.tracking_number:
            response_parts.append(f"via {order.carrier} dengan nomor resi {order.tracking_number}")
        
        if order.eta_date and order.status in ["confirmed", "shipped"]:
            eta_str = order.eta_date.strftime("%d %B %Y")
            response_parts.append(f"dengan estimasi tiba {eta_str}")
        
        if order.last_update_at:
            update_str = order.last_update_at.strftime("%d %B %Y pukul %H:%M")
            response_parts.append(f"Terakhir diupdate: {update_str}")
        
        result = ". ".join(response_parts) + "."
        
        logger.info("Order status retrieved", order_id=order_id, status=order.status)
        return result
        
    except Exception as e:
        logger.error("Failed to get order status", order_id=order_id, error=str(e))
        return f"Maaf, terjadi kesalahan saat mencari pesanan {order_id}. Silakan coba lagi atau hubungi customer service."


async def get_product_info_impl(product_name: str, db_session: AsyncSession) -> str:
    """
    Implementation function for product information lookup.
    
    Args:
        product_name: Product name to search for
        db_session: Database session
        
    Returns:
        Formatted product information
    """
    try:
        logger.info("Looking up product info", product_name=product_name)
        
        # Query product by name (case-insensitive partial match)
        stmt = (
            select(Product)
            .where(Product.name.ilike(f"%{product_name}%"))
        )
        result = await db_session.execute(stmt)
        products = result.scalars().all()
        
        if not products:
            return f"Produk '{product_name}' tidak ditemukan. Silakan periksa nama produk atau lihat katalog lengkap di website kami."
        
        # Take first match
        product = products[0]
        
        response_parts = [f"Produk: {product.name}"]
        
        if product.features:
            response_parts.append(f"Fitur: {product.features}")
        
        if product.price:
            price_formatted = f"Rp {product.price:,.0f}".replace(",", ".")
            response_parts.append(f"Harga: {price_formatted}")
        
        if product.stock is not None:
            if product.stock > 0:
                response_parts.append(f"Stok: {product.stock} unit tersedia")
            else:
                response_parts.append("Stok: sedang kosong")
        
        result = ". ".join(response_parts) + "."
        
        logger.info("Product info retrieved", product_name=product_name, product_id=product.id)
        return result
        
    except Exception as e:
        logger.error("Failed to get product info", product_name=product_name, error=str(e))
        return f"Maaf, terjadi kesalahan saat mencari produk '{product_name}'. Silakan coba lagi."


async def get_warranty_policy_impl(db_session: AsyncSession) -> str:
    """
    Implementation function for warranty policy lookup.
    
    Args:
        db_session: Database session
        
    Returns:
        Formatted warranty policy information
    """
    try:
        logger.info("Looking up warranty policy")
        
        # Query warranty policy
        stmt = (
            select(Policy)
            .where(Policy.type == "warranty")
        )
        result = await db_session.execute(stmt)
        policy = result.scalar_one_or_none()
        
        if not policy:
            # Fallback default policy
            return """Prosedur klaim garansi:
1. Siapkan nota pembelian asli dan kartu garansi
2. Hubungi customer service di 0800-1234-5678 (gratis) atau email cs@toko.com
3. Jelaskan masalah produk dengan detail
4. Tim CS akan memberikan instruksi selanjutnya (perbaikan atau penggantian)
5. Garansi berlaku 1 tahun dari tanggal pembelian untuk kerusakan manufaktur

Catatan: Garansi tidak berlaku untuk kerusakan akibat kesalahan penggunaan atau faktor eksternal."""
        
        # Return policy content
        result = policy.content_markdown
        
        logger.info("Warranty policy retrieved")
        return result
        
    except Exception as e:
        logger.error("Failed to get warranty policy", error=str(e))
        return "Maaf, terjadi kesalahan saat mengambil informasi garansi. Silakan hubungi customer service di 0800-1234-5678."


def create_order_status_tool(db_session: AsyncSession) -> Tool:
    """
    Create LangChain tool for order status lookup.
    
    Args:
        db_session: Database session
        
    Returns:
        LangChain Tool instance
    """
    async def tool_func(order_id: str) -> str:
        return await get_order_status_impl(order_id, db_session)
    
    return Tool(
        name="get_order_status",
        description="Mencari status pesanan berdasarkan ID pesanan. Gunakan ketika user menanyakan pesanan dengan menyebutkan ID atau nomor pesanan. Input: order_id (string)",
        func=tool_func
    )


def create_product_info_tool(db_session: AsyncSession) -> Tool:
    """
    Create LangChain tool for product information lookup.
    
    Args:
        db_session: Database session
        
    Returns:
        LangChain Tool instance
    """
    async def tool_func(product_name: str) -> str:
        return await get_product_info_impl(product_name, db_session)
    
    return Tool(
        name="get_product_info",
        description="Mencari informasi produk berdasarkan nama produk. Gunakan ketika user menanyakan spesifikasi, fitur, atau harga produk. Input: product_name (string)",
        func=tool_func
    )


def create_warranty_policy_tool(db_session: AsyncSession) -> Tool:
    """
    Create LangChain tool for warranty policy lookup.
    
    Args:
        db_session: Database session
        
    Returns:
        LangChain Tool instance
    """
    async def tool_func() -> str:
        return await get_warranty_policy_impl(db_session)
    
    return Tool(
        name="get_warranty_policy",
        description="Mengambil informasi kebijakan garansi dan prosedur klaim. Gunakan ketika user menanyakan tentang garansi, klaim garansi, atau warranty. Tidak memerlukan input.",
        func=tool_func
    )


def get_tools(db_session: AsyncSession) -> List[Tool]:
    """
    Get all available tools for the chat agent.
    
    Args:
        db_session: Database session
        
    Returns:
        List of LangChain Tool instances
    """
    return [
        create_order_status_tool(db_session),
        create_product_info_tool(db_session),
        create_warranty_policy_tool(db_session),
    ]
