"""1000并发用户测试脚本"""
import asyncio
import aiohttp
import time
import statistics

async def test_1000_users():
    """测试1000并发用户"""
    base_url = "http://localhost:80"
    concurrent_users = 1000
    
    print(f"=== 测试 {concurrent_users} 并发用户 ===")
    start_time = time.time()
    
    async def single_request(session, user_id):
        try:
            async with session.get(base_url, timeout=60) as response:
                return {
                    "success": response.status == 200,
                    "latency": time.time() - start_time
                }
        except:
            return {"success": False, "latency": time.time() - start_time}
    
    async with aiohttp.ClientSession() as session:
        tasks = [single_request(session, i) for i in range(concurrent_users)]
        results = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    success_count = sum(1 for r in results if r["success"])
    success_rate = (success_count / concurrent_users) * 100
    latencies = [r["latency"] for r in results if r["success"]]
    throughput = concurrent_users / total_time
    
    print(f"总耗时: {total_time:.2f}s")
    print(f"成功请求: {success_count}/{concurrent_users}")
    print(f"成功率: {success_rate:.2f}%")
    if latencies:
        print(f"平均延迟: {statistics.mean(latencies):.2f}s")
        print(f"最大延迟: {max(latencies):.2f}s")
    print(f"吞吐量: {throughput:.2f} 请求/秒")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = asyncio.run(test_1000_users())
    print(f"\n{'✅ 系统支持1000并发用户!' if success else '⚠️ 系统未达到预期性能'}")
