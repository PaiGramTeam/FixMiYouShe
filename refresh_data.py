from src.data.get_bg import save_bg


async def refresh_data():
    await save_bg()


if __name__ == "__main__":
    import asyncio

    asyncio.run(refresh_data())
