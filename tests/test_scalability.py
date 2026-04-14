"""系统可扩展性测试脚本 - 逐步测试并发能力"""
import asyncio
import aiohttp
import time
import statistics

class ScalabilityTester:
    def __init__(self, base_url="http://localhost:80"):
        self.base_url = base_url
        self.max_concurrent = 0
        self.best_throughput = 0
    
    async def single_request(self, session, user_id):
        """发送单个请求"""
        start_time = time.time()
        try:
            async with session.get(self.base_url, timeout=30) as response:
                latency = time.time() - start_time
                return {
                    "user_id": user_id,
                    "success": response.status == 200,
                    "latency": latency,
                    "status_code": response.status
                }
        except Exception as e:
            latency = time.time() - start_time
            return {
                "user_id": user_id,
                "success": False,
                "latency": latency,
                "error": str(e)
            }
    
    async def test_concurrent(self, concurrent_users):
        """测试指定并发用户数"""
        print(f"\n=== 测试 {concurrent_users} 并发用户 ===")
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(concurrent_users):
                task = asyncio.create_task(self.single_request(session, i))
                tasks.append(task)
            
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
        
        return {
            "concurrent_users": concurrent_users,
            "success_rate": success_rate,
            "throughput": throughput,
            "avg_latency": statistics.mean(latencies) if latencies else float('inf')
        }
    
    async def run_scalability_test(self):
        """运行可扩展性测试"""
        print("=== 系统可扩展性测试 ===")
        print(f"测试目标: {self.base_url}")
        print("=" * 50)
        
        # 测试场景：逐步增加并发用户
        test_levels = [10, 20, 30, 50, 80, 100, 150, 200, 300]
        results = []
        
        for level in test_levels:
            result = await self.test_concurrent(level)
            results.append(result)
            
            # 如果成功率低于80%，停止测试
            if result["success_rate"] < 80:
                print(f"\n⚠️ 系统在 {level} 并发时达到瓶颈")
                break
            
            # 记录最佳性能
            if result["throughput"] > self.best_throughput:
                self.best_throughput = result["throughput"]
                self.max_concurrent = level
            
            # 给系统恢复时间
            await asyncio.sleep(2)
        
        # 输出测试总结
        print("\n" + "=" * 50)
        print("=== 测试总结 ===")
        print(f"最大稳定并发用户: {self.max_concurrent}")
        print(f"最高吞吐量: {self.best_throughput:.2f} 请求/秒")
        
        # 输出详细结果
        print("\n详细结果:")
        for r in results:
            status = "✅" if r["success_rate"] >= 80 else "⚠️"
            print(f"{status} {r['concurrent_users']}用户: 成功率{r['success_rate']:.1f}% | 吞吐量{r['throughput']:.1f}req/s | 延迟{r['avg_latency']:.2f}s")

if __name__ == "__main__":
    tester = ScalabilityTester(base_url="http://localhost:80")
    asyncio.run(tester.run_scalability_test())
