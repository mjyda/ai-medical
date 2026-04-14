"""10万并发用户测试脚本"""
import asyncio
import aiohttp
import time

async def test_100000_users():
    """测试10万并发用户（分批处理）"""
    base_url = "http://localhost:80"
    total_users = 100000
    batch_size = 10000
    total_success = 0
    total_time = 0
    
    print(f"=== 测试 {total_users} 并发用户 ===")
    print("注意：此测试需要大量系统资源，将分批处理...")
    
    async with aiohttp.ClientSession() as session:
        for batch in range(0, total_users, batch_size):
            start_time = time.time()
            end = min(batch + batch_size, total_users)
            current_batch = end - batch
            
            async def single_request(user_id):
                try:
                    async with session.get(base_url, timeout=60) as response:
                        return response.status == 200
                except:
                    return False
            
            tasks = [single_request(i) for i in range(batch, end)]
            results = await asyncio.gather(*tasks)
            
            batch_success = sum(1 for r in results if r)
            total_success += batch_success
            batch_time = time.time() - start_time
            total_time += batch_time
            
            print(f"批次 {batch//batch_size + 1}: {batch_success}/{current_batch} 成功 | 耗时 {batch_time:.2f}s")
            
            # 给系统恢复时间
            await asyncio.sleep(1)
    
    success_rate = (total_success / total_users) * 100
    throughput = total_users / total_time
    
    print(f"\n=== 测试完成 ===")
    print(f"总耗时: {total_time:.2f}s")
    print(f"成功请求: {total_success}/{total_users}")
    print(f"成功率: {success_rate:.2f}%")
    print(f"吞吐量: {throughput:.2f} 请求/秒")
    print(f"结果: {'通过' if success_rate >= 80 else '未通过'}")

if __name__ == "__main__":
    asyncio.run(test_100000_users())
