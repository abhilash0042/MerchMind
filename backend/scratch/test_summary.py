import asyncio
from app.db.session import AsyncSessionLocal
from app.routes.analytics import dashboard_summary
import sys

async def test_dashboard():
    try:
        async with AsyncSessionLocal() as db:
            summary = await dashboard_summary(
                seller_id="c592fd56-c939-4448-92ef-930dea943e1d",
                days=30,
                db=db,
                _scope="test"
            )
            print("Summary works:", summary)
    except Exception as e:
        import traceback
        traceback.print_exc()

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(test_dashboard())
