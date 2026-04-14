"""高并发测试脚本 - 测试2000和3000用户"""
import asyncio
import aiohttp
import time
import statistics

async def test_concurrent(base_url, concurrent_users):
    """测试指定并发用户数"""
    print(f"\n=== 测试 {concurrent_users} 并发用户 ===")
    start_time = time.time()
    
    async def single_request(session, user_id):
        try:
            async with session.get(base_url, timeout=60) as response:
                return {"success": response.status == 200}
        except:
            return {"success": False}
    
    async with aiohttp.ClientSession() as session:
        tasks = [single_request(session, i) for i in range(concurrent_users)]
        results = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    success_count = sum(1 for r in results if r["success"])
    success_rate = (success_count / concurrent_users) * 100
    throughput = concurrent_users / total_time
    
    print(f"总耗时: {total_time:.2f}s")
    print(f"成功请求: {success_count}/{concurrent_users}")
    print(f"成功率: {success_rate:.2f}%")
    print(f"吞吐量: {throughput:.2f} 请求/秒")
    
    return {
        "users": concurrent_users,
        "success_rate": success_rate,
        "throughput": throughput,
        "total_time": total_time
    }

async def main():
    base_url = "http://localhost:80"
    test_levels = [2000, 3000]
    
    for level in test_levels:
        result = await test_concurrent(base_url, level)
        status = "通过" if result["success_rate"] >= 80 else "未通过"
        print(f"结果: {status}")
        await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
