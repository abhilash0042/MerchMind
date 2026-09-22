import os
import random
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_groq_api_key():
    """
    Returns a random Groq API key from the available pool in .env
    to distribute Token Per Minute (TPM) load and avoid 429 errors.
    """
    keys = [
        (os.getenv("GROQ_API_KEY") or "").strip().strip('"').strip("'"),
        (os.getenv("GROQ_API_KEY_2") or "").strip().strip('"').strip("'"),
        (os.getenv("GROQ_API_KEY_3") or "").strip().strip('"').strip("'")
    ]
    # Filter out None/Empty keys and placeholders
    valid_keys = [k for k in keys if k and len(k) > 20 and "from screenshot" not in k]
    
    if not valid_keys:
        # Fallback to the first key if everything fails, but try to be safe
        first_key = os.getenv("GROQ_API_KEY")
        if first_key: return first_key
        raise ValueError("No valid GROQ_API_KEY found in .env")
        
    return random.choice(valid_keys)

class FallbackChatGroq:
    def __init__(self, primary: ChatGroq, fallback: ChatGroq):
        self.primary = primary
        self.fallback = fallback

    def bind_tools(self, tools, **kwargs):
        bound_primary = self.primary.bind_tools(tools, **kwargs)
        bound_fallback = self.fallback.bind_tools(tools, **kwargs)
        return bound_primary.with_fallbacks([bound_fallback])

    def with_structured_output(self, schema, **kwargs):
        struct_primary = self.primary.with_structured_output(schema, **kwargs)
        struct_fallback = self.fallback.with_structured_output(schema, **kwargs)
        return struct_primary.with_fallbacks([struct_fallback])

    def with_config(self, config=None, **kwargs):
        conf = config or {}
        conf.update(kwargs)
        cfg_primary = self.primary.with_config(conf)
        cfg_fallback = self.fallback.with_config(conf)
        return FallbackChatGroq(cfg_primary, cfg_fallback)

    def invoke(self, messages, **kwargs):
        return self.primary.with_fallbacks([self.fallback]).invoke(messages, **kwargs)

    async def ainvoke(self, messages, **kwargs):
        return await self.primary.with_fallbacks([self.fallback]).ainvoke(messages, **kwargs)

def get_fallback_llm(api_key: str = None, temperature: float = 0.0) -> FallbackChatGroq:
    key = api_key or get_groq_api_key()
    fallback_key = get_groq_api_key()
    primary = ChatGroq(api_key=key, model="openai/gpt-oss-20b", temperature=temperature, max_tokens=700)
    fallback = ChatGroq(api_key=fallback_key, model="openai/gpt-oss-120b", temperature=temperature, max_tokens=700)
    return FallbackChatGroq(primary, fallback)
