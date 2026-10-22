

import asyncio
import time


async def fetch_data(seconds):
    print("Start")
    await asyncio.sleep(seconds)
    print("End")
    
    return f"Waited {seconds} sec"


# this will don't run because we need to run async funtion with asyncio.run(function_name)
# print(fetch_data())
    
    
    
# async def main():
    
#     # print(fetch_data)
    
#     start = time.perf_counter()
    
#     print(await fetch_data(2))
#     print(await fetch_data(4))

#     # in that situaion it doesn't work 4 sec as we wait. because await will be wait until first coroutine wil be finished
    
#     print(time.perf_counter() - start)
    
    
    
    
async def main():
    
    start = time.perf_counter()
    
    task1 = asyncio.create_task(fetch_data(2))
    task2 = asyncio.create_task(fetch_data(4))
    
    await task1
    await task2
    
    # or we can use
    await asyncio.gather(task1, task2)
    
    
    print(f"Time: {time.perf_counter() - start}")

if __name__ == "__main__":
    asyncio.run(main())
    
    

    

    
        
    
    
