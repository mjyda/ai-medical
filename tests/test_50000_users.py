"""50000并发用户测试脚本"""
import asyncio
import aiohttp
import time

async def test_50000_users():
    """测试50000并发用户"""
    base_url = "http://localhost:80"
    concurrent_users = 50000
    
    print(f"=== 测试 {concurrent_users} 并发用户 ===")
    print("注意：此测试需要大量系统资源，可能需要较长时间...")
    
    start_time = time.time()
    
    # 分批处理，避免一次性创建过多连接
    batch_size = 5000
    total_success = 0
    total_requests = 0
    
    async with aiohttp.ClientSession() as session:
        for batch in range(0, concurrent_users, batch_size):
            end = min(batch + batch_size, concurrent_users)
            current_batch_size = end - batch
            
            tasks = []
            for i in range(batch, end):
                task = asyncio.create_task(single_request(session, i, base_url))
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            success_count = sum(1 for r in results if r)
            total_success += success_count
            total_requests += current_batch_size
            
            elapsed = time.time() - start_time
            print(f"批次 {batch//batch_size + 1}: {success_count}/{current_batch_size} 成功 | 已完成 {total_requests}/{concurrent_users} | 耗时 {elapsed:.2f}s")
            
            # 给系统一点恢复时间
            await asyncio.sleep(0.5)
    
    total_time = time.time() - start_time
    success_rate = (total_success / concurrent_users) * 100
    throughput = concurrent_users / total_time
    
    print(f"\n=== 测试完成 ===")
    print(f"总耗时: {total_time:.2f}s")
    print(f"成功请求: {total_success}/{concurrent_users}")
    print(f"成功率: {success_rate:.2f}%")
    print(f"吞吐量: {throughput:.2f} 请求/秒")
    print(f"结果: {'通过' if success_rate >= 80 else '未通过'}")

async def single_request(session, user_id, base_url):
    """发送单个请求"""
    try:
        async with session.get(base_url, timeout=120) as response:
            return response.status == 200
    except:
        return False

if __name__ == "__main__":
    asyncio.run(test_50000_users())
