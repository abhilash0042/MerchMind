import asyncio
from app.db.session import AsyncSessionLocal
from app.routes.ai import ai_chat, ChatRequest
import sys

async def test_chat():
    payload = ChatRequest(
        message="What's my revenue?",
        history=[
            {"type": "ai", "text": "Hi"}
        ],
        context={
            "period_days": 30,
            "total_revenue": 10000.0,
            "total_orders": 50,
            "return_rate_pct": 2.0,
            "avg_margin_pct": 20.0,
            "avg_roas": 3.0
        }
    )
    
    try:
        async with AsyncSessionLocal() as db:
            reply = await ai_chat(
                request=payload,
                seller_id="c592fd56-c939-4448-92ef-930dea943e1d",
                db=db,
                _scope="test"
            )
            print("Chat works:", reply)
    except Exception as e:
        import traceback
        traceback.print_exc()

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(test_chat())
