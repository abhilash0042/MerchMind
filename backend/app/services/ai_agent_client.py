import os
from typing import Dict, Any, Optional
import httpx
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Using httpx for async requests
async def trigger_simulation(
    seller_id: str, 
    time_window_start: str, 
    time_window_end: str, 
    snapshot_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Sends an async POST request to the ai_agents service to run a multi-agent simulation.
    """
    url = f"{settings.AI_AGENTS_URL}/api/v1/simulate"
    
    payload = {
        "seller_id": seller_id,
        "time_window_start": time_window_start,
        "time_window_end": time_window_end,
        "snapshot_data": snapshot_data
    }
    
    try:
        # Increase timeout as agent simulations can take a while (e.g. 60+ seconds)
        async with httpx.AsyncClient(timeout=300.0) as client:
            logger.info(f"Triggering AI agent simulation for {seller_id} to URL {url}")
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data
            
    except httpx.HTTPError as exc:
        logger.error(f"HTTP Exception while connecting to AI agents API: {exc}")
        return None
    except Exception as exc:
        logger.error(f"Error calling AI agents API: {exc}")
        return None

async def trigger_simulation_stream(
    seller_id: str, 
    time_window_start: str, 
    time_window_end: str, 
    snapshot_data: Dict[str, Any]
):
    """
    Sends an async POST request to the ai_agents service and yields the SSE streaming response.
    """
    url = f"{settings.AI_AGENTS_URL}/api/v1/simulate/stream"
    
    payload = {
        "seller_id": seller_id,
        "time_window_start": time_window_start,
        "time_window_end": time_window_end,
        "snapshot_data": snapshot_data
    }
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk
    except Exception as exc:
        import json
        logger.error(f"Error streaming from AI agents API: {exc}")
        yield f"data: {json.dumps({'error': str(exc)})}\n\n".encode('utf-8')

async def trigger_whatif_stream(seller_id: str, scenario: str):
    """
    Sends an async POST request to the ai_agents service's whatif endpoint and yields the SSE response.
    """
    url = f"{settings.AI_AGENTS_URL}/api/v1/simulate/whatif"
    
    payload = {
        "seller_id": seller_id,
        "scenario": scenario
    }
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk
    except Exception as exc:
        import json
        logger.error(f"Error streaming what-if from AI agents API: {exc}")
        yield f"data: {json.dumps({'error': str(exc)})}\n\n".encode('utf-8')

async def trigger_product_analysis(
    seller_id: str, 
    product_id: str,
    product_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Sends an async POST request to the ai_agents service to run a per-product analysis.
    """
    url = f"{settings.AI_AGENTS_URL}/api/v1/analyze/product"
    
    payload = {
        "seller_id": seller_id,
        "product_id": product_id,
        "product_data": product_data
    }
    
    try:
        # Increase timeout as agent simulations can take a while
        async with httpx.AsyncClient(timeout=300.0) as client:
            logger.info(f"Triggering AI product analysis for product {product_id} to URL {url}")
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data
            
    except httpx.HTTPError as exc:
        logger.error(f"HTTP Exception while connecting to AI agents API: {exc}")
        return None
    except Exception as exc:
        logger.error(f"Error calling AI agents API for product analysis: {exc}")
        return None
