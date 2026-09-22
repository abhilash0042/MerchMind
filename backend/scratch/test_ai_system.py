import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.agents import create_agent
from langchain_core.tools import tool

@tool
async def fetch_sample_roas(product_id: str) -> str:
    """Fetches sample roas asynchronously."""
    await asyncio.sleep(0.01)
    return f"Sample ROAS for {product_id} is 3.5."

async def test():
    key = os.getenv("GROQ_API_KEY")
    llm = ChatGroq(api_key=key, model="qwen/qwen3.8-27b", temperature=0.1)
    agent = create_agent(model=llm, tools=[fetch_sample_roas])
    
    res = await agent.ainvoke({
        "messages": [HumanMessage(content="What is the ROAS for PROD-123?")]
    })
    
    for msg in res["messages"]:
        print(f"[{msg.type}]: {msg.content}")

asyncio.run(test())
