"""简单性能测试脚本 - 测试RAG服务响应时间"""
import time
import statistics
import subprocess
import os

def run_benchmark():
    """运行简单的性能基准测试"""
    print("=== 性能基准测试 ===")
    print("\n1. 测试环境检查")
    
    # 检查Docker服务状态
    result = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True)
    containers = result.stdout.strip().split('\n')
    
    print(f"运行中的容器数量: {len(containers)}")
    for container in containers:
        if container:
            print(f"  - {container}")
    
    print("\n2. 测试Nginx负载均衡")
    result = subprocess.run(["curl", "-s", "-o", "NUL", "-w", "%{http_code}", "http://localhost:80"], 
                           capture_output=True, text=True)
    http_code = result.stdout.strip()
    print(f"Nginx响应状态码: {http_code}")
    
    print("\n3. 测试响应时间")
    latencies = []
    for i in range(5):
        start = time.time()
        subprocess.run(["curl", "-s", "-o", "NUL", "http://localhost:80"], capture_output=True)
        latency = time.time() - start
        latencies.append(latency)
        print(f"  请求 {i+1}: {latency:.2f}s")
    
    if latencies:
        print(f"\n平均响应时间: {statistics.mean(latencies):.2f}s")
        print(f"最小响应时间: {min(latencies):.2f}s")
        print(f"最大响应时间: {max(latencies):.2f}s")
    
    print("\n4. 测试数据库连接")
    # 测试PostgreSQL
    result = subprocess.run(["docker", "exec", "pgvector", "psql", "-U", "postgres", "-c", "SELECT 1"],
                           capture_output=True, text=True)
    if result.returncode == 0:
        print("PostgreSQL: ✅ 连接正常")
    else:
        print(f"PostgreSQL: ❌ 连接失败 - {result.stderr}")
    
    # 测试Redis
    result = subprocess.run(["docker", "exec", "redis-cache", "redis-cli", "ping"],
                           capture_output=True, text=True)
    if result.stdout.strip() == "PONG":
        print("Redis: ✅ 连接正常")
    else:
        print(f"Redis: ❌ 连接失败")
    
    # 测试MongoDB
    result = subprocess.run(["docker", "exec", "mongodb", "mongosh", "--eval", "db.adminCommand('ping')"],
                           capture_output=True, text=True)
    if result.returncode == 0:
        print("MongoDB: ✅ 连接正常")
    else:
        print(f"MongoDB: ❌ 连接失败")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    run_benchmark()
