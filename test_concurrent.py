"""并发性能测试脚本 - 直接调用后端RAG服务"""
import asyncio
import time
import statistics
import sys
import os

# 设置环境变量，连接到Docker容器中的数据库
os.environ["POSTGRESQL_HOST"] = "localhost"
os.environ["POSTGRESQL_PORT"] = "5434"  # Docker映射的端口
os.environ["REDIS_HOST"] = "localhost"
os.environ["MONGODB_HOST"] = "localhost"
os.environ["MYSQL_HOST"] = "localhost"
os.environ["MYSQL_PORT"] = "3307"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.backend.agents.xiaozhi_agent import XiaozhiAgent

class ConcurrentTester:
    def __init__(self):
        self.results = []
        self.agent = XiaozhiAgent()
    
    async def test_single_user(self, user_id, query):
        """模拟单个用户查询"""
        start_time = time.time()
        try:
            result = await asyncio.to_thread(self.agent.chat, f"test_user_{user_id}", query)
            latency = time.time() - start_time
            self.results.append({
                "user_id": user_id,
                "status": "success",
                "latency": latency,
                "response_length": len(result) if result else 0
            })
            print(f"用户 {user_id}: 成功, 延迟: {latency:.2f}s")
        except Exception as e:
            latency = time.time() - start_time
            self.results.append({
                "user_id": user_id,
                "status": "error",
                "latency": latency,
                "error": str(e)
            })
            print(f"用户 {user_id}: 错误 - {e}")
    
    async def run_test(self, concurrent_users):
        """运行并发测试"""
        print(f"\n=== 开始测试: {concurrent_users} 并发用户 ===")
        start_time = time.time()
        
        queries = [
            "人事管理系统有哪些功能模块？",
            "简历解析功能的需求是什么？",
            "人才库与岗位池管理包含哪些内容？",
            "面试辅助功能有哪些需求？",
            "公司有哪些产品服务？",
            "什么是人工智能？",
            "常见问题有哪些？",
            "业务流程是怎样的？"
        ]
        
        tasks = []
        for i in range(concurrent_users):
            query = queries[i % len(queries)]
            task = asyncio.create_task(self.test_single_user(i, query))
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
            if len(latencies) >= 10:
                print(f"P90延迟: {sorted(latencies)[int(len(latencies)*0.9)]:.2f}s")
                print(f"P95延迟: {sorted(latencies)[int(len(latencies)*0.95)]:.2f}s")
        
        print(f"吞吐量: {concurrent_users / total_time:.2f} 请求/秒")

async def main():
    tester = ConcurrentTester()
    
    # 测试不同并发级别
    test_levels = [10, 20, 30, 50, 100]
    
    for level in test_levels:
        tester.results = []
        await tester.run_test(level)
        await asyncio.sleep(3)  # 给系统恢复时间

if __name__ == "__main__":
    asyncio.run(main())
