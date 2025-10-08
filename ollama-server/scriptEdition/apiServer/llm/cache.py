"""
Provider-Agnostic Cache Management
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from .providers.base import LLMProvider

logger = logging.getLogger("provider-cache-manager")


class ProviderCacheManager:
    """Manages caching for different LLM providers"""
    
    def __init__(self, provider: LLMProvider, enable_caching: bool = True):
        self.provider = provider
        self.enable_caching = enable_caching
        self.cached_tools = None
        self.cached_system_prompt = None
    
    async def warm_cache(self, model: str, system_prompt: str, tools: List[Dict[str, Any]]) -> bool:
        """Warm cache if provider supports it and caching is enabled"""
        if not self.enable_caching:
            logger.info("🔧 Caching disabled by flag, skipping...")
            return True
            
        if not self.provider.supports_caching():
            logger.info(f"🔧 Provider {self.provider.__class__.__name__} doesn't support caching, skipping...")
            return True
        
        logger.info(f"🔥 Warming cache for {self.provider.__class__.__name__}...")
        
        try:
            # Cache system prompt
            success = await self._cache_system_prompt(model, system_prompt)
            if not success:
                return False
            
            # Cache tools if available
            if tools:
                success = await self._cache_tools(model, system_prompt, tools)
                if not success:
                    return False
            
            logger.info("✅ Cache warming completed")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Cache warming failed: {e}")
            return False
    
    async def _cache_system_prompt(self, model: str, system_prompt: str) -> bool:
        """Cache system prompt (provider-agnostic)"""
        return await self._cache_provider_system_prompt(model, system_prompt)
    
    async def _cache_tools(self, model: str, system_prompt: str, tools: List[Dict[str, Any]]) -> bool:
        """Cache tools (provider-agnostic)"""
        return await self._cache_provider_tools(model, system_prompt, tools)
    
    async def _cache_provider_system_prompt(self, model: str, system_prompt: str, max_retries: int = 3) -> bool:
        """Cache system prompt using provider's caching implementation"""
        for attempt in range(max_retries):
            try:
                # Set system prompt on provider for cache warming
                self.provider.set_system_prompt(system_prompt)
                
                response = await self.provider.call_api(
                    model=model,
                    messages=[{"role": "user", "content": "Warming system prompt cache."}],
                    max_tokens=5,
                    enable_caching=True  # Force caching for cache warming
                )
                
                if response["success"]:
                    logger.info("✅ System prompt cached successfully")
                    return True
                else:
                    if "429" in str(response.get("error", "")):
                        wait_time = 2 ** attempt
                        logger.warning(f"⚠️ Rate limit hit, waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.warning(f"⚠️ Failed to cache system prompt: {response.get('error')}")
                        return False
                        
            except Exception as e:
                logger.warning(f"⚠️ Error caching system prompt attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return False
        
        return False
    
    async def _cache_provider_tools(self, model: str, system_prompt: str, tools: List[Dict[str, Any]]) -> bool:
        """Cache tools using provider's caching implementation with progressive reduction"""
        # Try all tools first
        success = await self._cache_provider_tools_batch(model, system_prompt, tools)
        if success:
            logger.info(f"✅ All {len(tools)} tools cached successfully")
            return True
        
        # Fallback to progressive reduction
        logger.info("📦 Falling back to progressive reduction...")
        return await self._progressive_tool_caching(model, system_prompt, tools)
    
    async def _cache_provider_tools_batch(self, model: str, system_prompt: str, tools: List[Dict[str, Any]], max_retries: int = 2) -> bool:
        """Cache a batch of tools using provider's implementation"""
        for attempt in range(max_retries):
            try:
                # Set system prompt and tools on provider for cache warming
                self.provider.set_system_prompt(system_prompt)
                self.provider.set_tools(tools)
                
                response = await self.provider.call_api(
                    model=model,
                    messages=[{"role": "user", "content": f"Warming cache with {len(tools)} tools."}],
                    max_tokens=5,
                    enable_caching=True  # Force caching for cache warming
                )
                
                if response["success"]:
                    logger.info(f"✅ {len(tools)} tools cached successfully")
                    return True
                else:
                    if "429" in str(response.get("error", "")):
                        if attempt < max_retries - 1:
                            wait_time = 2 ** attempt
                            logger.warning(f"⚠️ Rate limit hit, waiting {wait_time}s...")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            logger.warning("⚠️ Rate limit hit - will try progressive reduction")
                            return False
                    else:
                        logger.warning(f"⚠️ Failed to cache tools: {response.get('error')}")
                        return False
                        
            except Exception as e:
                logger.warning(f"⚠️ Error caching tools attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return False
        
        return False
    
    async def _progressive_tool_caching(self, model: str, system_prompt: str, tools: List[Dict[str, Any]]) -> bool:
        """Progressive reduction caching strategy"""
        total_tools = len(tools)
        reduction_step = 10
        
        # Try progressively smaller sets
        for reduction in range(reduction_step, total_tools, reduction_step):
            tools_subset = tools[:-reduction]
            
            logger.info(f"📦 Trying {len(tools_subset)} tools (removing last {reduction})")
            
            success = await self._cache_provider_tools_batch(model, system_prompt, tools_subset)
            if success:
                # Cache remaining tools in small batches
                remaining_tools = tools[-reduction:]
                if remaining_tools:
                    await self._cache_remaining_tools(model, system_prompt, remaining_tools)
                return True
            
            await asyncio.sleep(1)
        
        # Fallback to very small batches
        logger.warning("⚠️ All reductions failed, using small batches...")
        await self._cache_remaining_tools(model, system_prompt, tools, batch_size=5)
        return True
    
    async def _cache_remaining_tools(self, model: str, system_prompt: str, remaining_tools: List[Dict[str, Any]], batch_size: int = 10):
        """Cache remaining tools in small batches"""
        for i in range(0, len(remaining_tools), batch_size):
            batch = remaining_tools[i:i + batch_size]
            logger.info(f"📦 Caching batch of {len(batch)} remaining tools")
            
            await self._cache_provider_tools_batch(model, system_prompt, batch)
            
            if i + batch_size < len(remaining_tools):
                await asyncio.sleep(1)