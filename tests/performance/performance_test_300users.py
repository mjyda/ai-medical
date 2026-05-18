"""高并发性能测试脚本 - 模拟300用户同时访问"""
import asyncio
import aiohttp
import time
import statistics
from datetime import datetime

class PerformanceTester:
    def __init__(self, base_url="http://localhost:80"):
        self.base_url = base_url
        self.results = []
    
    async def fetch(self, session, user_id, query):
        """模拟单个用户请求"""
        start_time = time.time()
        try:
            async with session.post(
                f"{self.base_url}/chat",
                json={"message": query, "history": []},
                timeout=60
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    latency = time.time() - start_time
                    self.results.append({
                        "user_id": user_id,
                        "status": "success",
                        "latency": latency,
                        "timestamp": datetime.now().isoformat()
                    })
                    print(f"用户 {user_id}: 成功, 延迟: {latency:.2f}s")
                else:
                    latency = time.time() - start_time
                    self.results.append({
                        "user_id": user_id,
                        "status": "failed",
                        "latency": latency,
                        "error": f"HTTP {response.status}"
                    })
                    print(f"用户 {user_id}: 失败, 状态码: {response.status}")
        except Exception as e:
            latency = time.time() - start_time
            self.results.append({
                "user_id": user_id,
                "status": "error",
                "latency": latency,
                "error": str(e)
            })
            print(f"用户 {user_id}: 错误 - {e}")
    
    async def run_concurrent_test(self, concurrent_users, queries):
        """运行并发测试"""
        print(f"\n=== 开始测试: {concurrent_users} 并发用户 ===")
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(concurrent_users):
                query = queries[i % len(queries)]
                task = asyncio.create_task(self.fetch(session, i, query))
                tasks.append(task)
            
            await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        self.print_results(concurrent_users, total_time)
    
    def print_results(self, concurrent_users, total_time):
        """打印测试结果"""
        success_count = sum(1 for r in self.results if r["status"] == "success")
        failed_count = sum(1 for r in self.results if r["status"] != "success")
        latencies = [r["latency"] for r in self.results if r["status"] == "success"]
        
        print(f"\n=== 测试结果: {concurrent_users} 并发用户 ===")
        print(f"总耗时: {total_time:.2f}秒")
        print(f"成功请求: {success_count}")
        print(f"失败请求: {failed_count}")
        print(f"成功率: {(success_count / concurrent_users) * 100:.2f}%")
        
        if latencies:
            print(f"平均延迟: {statistics.mean(latencies):.2f}s")
            print(f"最小延迟: {min(latencies):.2f}s")
            print(f"最大延迟: {max(latencies):.2f}s")
            print(f"P50延迟: {statistics.median(latencies):.2f}s")
            print(f"P90延迟: {sorted(latencies)[int(len(latencies)*0.9)]:.2f}s")
            print(f"P95延迟: {sorted(latencies)[int(len(latencies)*0.95)]:.2f}s")
        
        print(f"吞吐量: {concurrent_users / total_time:.2f} 请求/秒")
    
    async def run_all_tests(self):
        """运行所有测试场景"""
        # 测试查询列表
        queries = [
            "人事管理系统有哪些功能模块？",
            "简历解析功能的需求是什么？",
            "人才库与岗位池管理包含哪些内容？",
            "面试辅助功能有哪些需求？",
            "公司有哪些产品服务？",
            "智能客服系统支持哪些渠道接入？",
            "常见问题有哪些？",
            "业务流程是怎样的？"
        ]
        
        # 逐步增加并发用户数
        test_scenarios = [50, 100, 150, 200, 250, 300]
        
        for users in test_scenarios:
            self.results = []  # 重置结果
            await self.run_concurrent_test(users, queries)
            # 给系统一些恢复时间
            await asyncio.sleep(5)

if __name__ == "__main__":
    tester = PerformanceTester(base_url="http://localhost:80")
    asyncio.run(tester.run_all_tests())