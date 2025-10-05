"""
Cache Management for Anthropic Prompt Caching
"""

import asyncio
import logging
import httpx
from typing import List, Dict, Any

logger = logging.getLogger("cache-manager")


class CacheManager:
    """Handles Anthropic prompt caching with progressive reduction strategy"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
    
    async def warm_anthropic_cache(self, model: str, system_prompt: str, mcp_tools: List[Dict[str, Any]]) -> bool:
        """Warm Anthropic prompt cache - try all tools first, fallback to batching if rate limited"""
        try:
            logger.info("🔥 Warming Anthropic prompt cache...")
            
            # First, cache system prompt only
            success = await self._cache_system_prompt(model, system_prompt)
            if not success:
                return False
            
            # Try to cache all tools at once (most token efficient)
            if mcp_tools:
                total_tools = len(mcp_tools)
                logger.info(f"📦 Attempting to cache all {total_tools} tools at once...")
                
                success = await self._cache_all_tools(model, system_prompt, mcp_tools)
                if success:
                    logger.info("✅ All tools cached successfully in single request")
                    return True
                
                # Fallback to batch caching if all-at-once failed
                logger.info("📦 Falling back to batch caching due to rate limits...")
                success = await self._cache_tools_in_batches(model, system_prompt, mcp_tools)
                
            logger.info("✅ Cache warming completed")
            return True
                    
        except Exception as e:
            logger.warning(f"⚠️ Cache warming failed: {e}")
            return False
    
    async def _cache_system_prompt(self, model: str, system_prompt: str, max_retries: int = 3) -> bool:
        """Cache system prompt with retry logic"""
        for attempt in range(max_retries):
            try:
                request_data = {
                    "model": model,
                    "system": [
                        {
                            "type": "text",
                            "text": system_prompt,
                            "cache_control": {
                                "type": "ephemeral",
                                "ttl": "1h"
                            }
                        }
                    ],
                    "messages": [
                        {"role": "user", "content": "Warming system prompt cache."}
                    ],
                    "max_tokens": 5
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                }
                
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{self.base_url}/messages",
                        json=request_data,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        if 'usage' in response_data:
                            input_tokens = response_data['usage'].get('input_tokens', 0)
                            logger.info(f"✅ System prompt cached - used {input_tokens} input tokens")
                        else:
                            logger.info("✅ System prompt cached successfully")
                        return True
                    elif response.status_code == 429:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        logger.warning(f"⚠️ Rate limit hit caching system prompt, attempt {attempt + 1}/{max_retries}, waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.warning(f"⚠️ Failed to cache system prompt: {response.status_code}")
                        return False
                        
            except Exception as e:
                logger.warning(f"⚠️ Error caching system prompt attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return False
        
        logger.warning(f"⚠️ Failed to cache system prompt after {max_retries} attempts")
        return False
    
    async def _cache_all_tools(self, model: str, system_prompt: str, all_tools: list, max_retries: int = 2) -> bool:
        """Try to cache all tools at once - most token efficient approach"""
        for attempt in range(max_retries):
            try:
                # Convert all tools to Anthropic format
                anthropic_tools = []
                for i, tool in enumerate(all_tools):
                    anthropic_tool = {
                        "name": tool["function"]["name"],
                        "description": tool["function"]["description"],
                        "input_schema": tool["function"]["parameters"]
                    }
                    
                    # Add cache control to the last tool
                    if i == len(all_tools) - 1:
                        anthropic_tool["cache_control"] = {
                            "type": "ephemeral",
                            "ttl": "1h"
                        }
                    
                    anthropic_tools.append(anthropic_tool)
                
                request_data = {
                    "model": model,
                    "system": [
                        {
                            "type": "text",
                            "text": system_prompt,
                            "cache_control": {
                                "type": "ephemeral",
                                "ttl": "1h"
                            }
                        }
                    ],
                    "messages": [
                        {"role": "user", "content": f"Warming cache with all {len(all_tools)} tools."}
                    ],
                    "tools": anthropic_tools,
                    "max_tokens": 5
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "anthropic-beta": "tools-2024-05-16"
                }
                
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{self.base_url}/messages",
                        json=request_data,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        if 'usage' in response_data:
                            input_tokens = response_data['usage'].get('input_tokens', 0)
                            logger.info(f"✅ All {len(all_tools)} tools cached - used {input_tokens} input tokens")
                        else:
                            logger.info(f"✅ All {len(all_tools)} tools cached successfully")
                        return True
                    elif response.status_code == 429:
                        logger.warning(f"⚠️ Rate limit hit caching all tools, attempt {attempt + 1}/{max_retries}")
                        if attempt < max_retries - 1:
                            wait_time = 2 ** attempt  # Exponential backoff
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            logger.warning("⚠️ Rate limit hit - will fallback to batch caching")
                            return False
                    else:
                        logger.warning(f"⚠️ Failed to cache all tools: {response.status_code}")
                        return False
                        
            except Exception as e:
                logger.warning(f"⚠️ Error caching all tools attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return False
        
        return False
    
    async def _cache_tools_in_batches(self, model: str, system_prompt: str, all_tools: list) -> bool:
        """Fallback: progressive reduction - try all minus 10, minus 20, etc. until success, then cache remaining"""
        total_tools = len(all_tools)
        reduction_step = 10
        
        logger.info(f"📦 Progressive reduction caching for {total_tools} tools...")
        
        # Try progressively smaller sets: all-10, all-20, all-30, etc.
        for reduction in range(reduction_step, total_tools, reduction_step):
            tools_to_cache = all_tools[:-reduction]  # Remove last 'reduction' tools
            remaining_tools = all_tools[-reduction:]  # Tools we removed
            
            logger.info(f"📦 Trying to cache {len(tools_to_cache)} tools (removing last {reduction})")
            
            success = await self._cache_tools_batch(model, system_prompt, tools_to_cache)
            if success:
                logger.info(f"✅ Successfully cached {len(tools_to_cache)} tools")
                
                # Now cache the remaining tools in small batches
                if remaining_tools:
                    logger.info(f"📦 Caching remaining {len(remaining_tools)} tools in batches...")
                    await self._cache_remaining_tools(model, system_prompt, remaining_tools)
                
                return True
            else:
                logger.warning(f"⚠️ Still rate limited with {len(tools_to_cache)} tools, reducing further...")
                await asyncio.sleep(1)
        
        # If we get here, even small sets are rate limited - try very small batches
        logger.warning("⚠️ All reductions failed, falling back to small individual batches...")
        await self._cache_remaining_tools(model, system_prompt, all_tools, batch_size=5)
        return True
    
    async def _cache_remaining_tools(self, model: str, system_prompt: str, remaining_tools: list, batch_size: int = 10) -> bool:
        """Cache remaining tools in small batches"""
        total_remaining = len(remaining_tools)
        total_batches = (total_remaining + batch_size - 1) // batch_size
        
        for batch_start in range(0, total_remaining, batch_size):
            batch_end = min(batch_start + batch_size, total_remaining)
            batch_tools = remaining_tools[batch_start:batch_end]
            batch_num = (batch_start // batch_size) + 1
            
            logger.info(f"📦 Caching remaining batch {batch_num}/{total_batches} ({len(batch_tools)} tools)")
            
            success = await self._cache_tools_batch(model, system_prompt, batch_tools)
            if not success:
                logger.warning(f"⚠️ Failed to cache remaining batch {batch_num}")
            
            # Small delay between batches
            if batch_end < total_remaining:
                await asyncio.sleep(1)
        
        return True
    
    async def _cache_tools_batch(self, model: str, system_prompt: str, tools_batch: list, max_retries: int = 3) -> bool:
        """Cache a cumulative batch of tools with retry logic - EVERY batch gets cache control"""
        for attempt in range(max_retries):
            try:
                # Convert tools to Anthropic format
                anthropic_tools = []
                for i, tool in enumerate(tools_batch):
                    anthropic_tool = {
                        "name": tool["function"]["name"],
                        "description": tool["function"]["description"],
                        "input_schema": tool["function"]["parameters"]
                    }
                    
                    # Add cache control to EVERY last tool in EVERY batch
                    if i == len(tools_batch) - 1:
                        anthropic_tool["cache_control"] = {
                            "type": "ephemeral",
                            "ttl": "1h"
                        }
                    
                    anthropic_tools.append(anthropic_tool)
                
                request_data = {
                    "model": model,
                    "system": [
                        {
                            "type": "text",
                            "text": system_prompt,
                            "cache_control": {
                                "type": "ephemeral",
                                "ttl": "1h"
                            }
                        }
                    ],
                    "messages": [
                        {"role": "user", "content": f"Warming tools cache ({len(tools_batch)} tools cumulative)."}
                    ],
                    "tools": anthropic_tools,
                    "max_tokens": 5
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "anthropic-beta": "tools-2024-05-16"
                }
                
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{self.base_url}/messages",
                        json=request_data,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        if 'usage' in response_data:
                            input_tokens = response_data['usage'].get('input_tokens', 0)
                            logger.info(f"✅ {len(tools_batch)} tools cached cumulatively - used {input_tokens} input tokens")
                        else:
                            logger.info(f"✅ {len(tools_batch)} tools cached cumulatively")
                        return True
                    elif response.status_code == 429:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        logger.warning(f"⚠️ Rate limit hit caching tools batch, attempt {attempt + 1}/{max_retries}, waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.warning(f"⚠️ Failed to cache tools batch: {response.status_code}")
                        return False
                        
            except Exception as e:
                logger.warning(f"⚠️ Error caching tools batch attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return False
        
        logger.warning(f"⚠️ Failed to cache tools batch after {max_retries} attempts")
        return False