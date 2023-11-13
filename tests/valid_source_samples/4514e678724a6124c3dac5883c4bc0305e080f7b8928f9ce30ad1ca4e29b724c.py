def test_async_gen_asyncio_shutdown_02():
    async def main():
        async for i in it:
            break
