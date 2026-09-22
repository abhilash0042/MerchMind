import asyncio
from app.db.session import engine
from sqlalchemy import text
from app.routes.analytics import product_metrics_detailed

async def run():
    class MockDB:
        async def execute(self, *args, **kwargs):
            async with engine.connect() as conn:
                return await conn.execute(*args, **kwargs)

    res = await product_metrics_detailed(
        product_id='03729f82-3baa-400a-bfd3-5c23137ed5bd',
        seller_id='c592fd56-c939-4448-92ef-930dea943e1d',
        db=MockDB(),
        _scope='seller'
    )
    print(res)

asyncio.run(run())
