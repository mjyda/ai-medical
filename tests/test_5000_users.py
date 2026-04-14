"""5000并发用户测试脚本"""
import asyncio
import aiohttp
import time

async def test_5000_users():
    """测试5000并发用户"""
    base_url = "http://localhost:80"
    concurrent_users = 50000
    
    print(f"=== 测试 {concurrent_users} 并发用户 ===")
    start_time = time.time()
    
    async def single_request(session, user_id):
        try:
            async with session.get(base_url, timeout=120) as response:
                return response.status == 200
        except:
            return False
    
    async with aiohttp.ClientSession() as session:
        tasks = [single_request(session, i) for i in range(concurrent_users)]
        results = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    success_count = sum(1 for r in results if r)
    success_rate = (success_count / concurrent_users) * 100
    throughput = concurrent_users / total_time
    
    print(f"总耗时: {total_time:.2f}s")
    print(f"成功请求: {success_count}/{concurrent_users}")
    print(f"成功率: {success_rate:.2f}%")
    print(f"吞吐量: {throughput:.2f} 请求/秒")
    print(f"结果: {'通过' if success_rate >= 80 else '未通过'}")

if __name__ == "__main__":
    asyncio.run(test_5000_users())
