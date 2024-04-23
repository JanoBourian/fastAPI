import asyncio 
import time

def sync_count(sleep_time: int) -> None:
    print(f"One with sleep_time {sleep_time}")
    time.sleep(sleep_time)
    print(f"Two with sleep_time {sleep_time}")

def sync_main() -> None:
    for num in (2, 1, 3):
        sync_count(num)

async def async_count(sleep_time: int) -> None:
    print(f"One with sleep_time {sleep_time}")
    await asyncio.sleep(sleep_time)
    print(f"Two with sleep_time {sleep_time}")

async def async_main() -> None:
    await asyncio.gather(
        async_count(2),
        async_count(1),
        async_count(3),
    )
    
if __name__ == "__main__":
    start = time.time()
    # sync_main()
    asyncio.run(async_main())
    elapsed = time.time() - start
    print(f"{__file__} executed in {elapsed:0.2f} seconds")