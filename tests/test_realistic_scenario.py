"""真实场景性能测试 - 模拟用户实际使用行为"""
import asyncio
import aiohttp
import time
import random
import statistics

async def simulate_user(session, user_id, think_time=1):
    """模拟真实用户行为"""
    endpoints = [
        "http://localhost:80",
        "http://localhost:80/health",
    ]
    
    # 随机选择一个端点
    endpoint = random.choice(endpoints)
    
    # 模拟思考时间（用户阅读/输入时间）
    await asyncio.sleep(random.uniform(0.5, think_time))
    
    start_time = time.time()
    try:
        async with session.get(endpoint, timeout=30) as response:
            latency = time.time() - start_time
            return {
                "success": response.status == 200,
                "latency": latency,
                "endpoint": endpoint
            }
    except Exception as e:
        latency = time.time() - start_time
        return {
            "success": False,
            "latency": latency,
            "error": str(e)
        }

async def run_realistic_test(concurrent_users, duration=60):
    """运行真实场景测试"""
    print(f"=== 真实场景测试: {concurrent_users} 用户, {duration}秒 ===")
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        results = []
        start_time = time.time()
        
        # 模拟用户持续请求
        async def user_loop(user_id):
            nonlocal results
            while time.time() - start_time < duration:
                result = await simulate_user(session, user_id)
                results.append(result)
        
        # 创建用户任务
        for i in range(concurrent_users):
            task = asyncio.create_task(user_loop(i))
            tasks.append(task)
        
        # 等待测试完成
        await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    success_count = sum(1 for r in results if r["success"])
    total_requests = len(results)
    success_rate = (success_count / total_requests) * 100 if total_requests > 0 else 0
    latencies = [r["latency"] for r in results if r["success"]]
    throughput = total_requests / total_time
    
    print(f"\n测试结果:")
    print(f"总请求数: {total_requests}")
    print(f"成功请求: {success_count}/{total_requests}")
    print(f"成功率: {success_rate:.2f}%")
    if latencies:
        print(f"平均延迟: {statistics.mean(latencies):.2f}s")
        print(f"P50延迟: {sorted(latencies)[int(len(latencies)*0.5)]:.2f}s")
        print(f"P90延迟: {sorted(latencies)[int(len(latencies)*0.9)]:.2f}s")
        print(f"最大延迟: {max(latencies):.2f}s")
    print(f"吞吐量: {throughput:.2f} 请求/秒")
    print(f"结果: {'通过' if success_rate >= 90 else '未通过'}")

if __name__ == "__main__":
    # 测试1000用户真实场景
    asyncio.run(run_realistic_test(1000, duration=30))
