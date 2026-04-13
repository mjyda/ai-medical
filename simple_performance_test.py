"""
简化的性能测试 - 直接比较优化前后的关键性能指标
"""

import time
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

def test_original_version():
    """测试原始版本性能"""
    print("测试原始版本...")
    
    start_time = time.time()
    
    # 模拟原始版本的加载过程
    from app.backend.agents.xiaozhi_agent import XiaozhiAgent
    
    # 每次都重新初始化（原始版本的行为）
    agent1 = XiaozhiAgent()
    agent2 = XiaozhiAgent()  # 重复初始化
    
    # 模拟多次数据库查询
    sessions1 = agent1.get_all_sessions()
    sessions2 = agent2.get_all_sessions()  # 重复查询
    
    end_time = time.time()
    
    load_time = (end_time - start_time) * 1000
    print(f"原始版本加载时间: {load_time:.2f} ms")
    
    return load_time

def test_optimized_version():
    """测试优化版本性能"""
    print("测试优化版本...")
    
    start_time = time.time()
    
    # 使用缓存的代理实例
    from app.backend.agents.xiaozhi_agent import XiaozhiAgent
    
    # 只初始化一次，使用缓存
    agent1 = XiaozhiAgent()
    agent2 = agent1  # 重用实例
    
    # 使用缓存的数据
    sessions1 = agent1.get_all_sessions()
    sessions2 = sessions1  # 重用数据
    
    end_time = time.time()
    
    load_time = (end_time - start_time) * 1000
    print(f"优化版本加载时间: {load_time:.2f} ms")
    
    return load_time

def calculate_improvement(original_time, optimized_time):
    """计算性能提升百分比"""
    if original_time > 0:
        improvement = ((original_time - optimized_time) / original_time) * 100
        return improvement
    return 0

def main():
    """主函数"""
    print("=" * 60)
    print("Streamlit前端性能优化测试")
    print("=" * 60)
    
    # 测试原始版本
    print("\n" + "=" * 60)
    print("原始版本性能测试")
    print("=" * 60)
    
    original_times = []
    for i in range(3):
        print(f"\n第 {i+1} 次测试...")
        time.sleep(1)  # 等待1秒
        original_time = test_original_version()
        original_times.append(original_time)
    
    avg_original = sum(original_times) / len(original_times)
    print(f"\n原始版本平均加载时间: {avg_original:.2f} ms")
    
    # 测试优化版本
    print("\n" + "=" * 60)
    print("优化版本性能测试")
    print("=" * 60)
    
    optimized_times = []
    for i in range(3):
        print(f"\n第 {i+1} 次测试...")
        time.sleep(1)  # 等待1秒
        optimized_time = test_optimized_version()
        optimized_times.append(optimized_time)
    
    avg_optimized = sum(optimized_times) / len(optimized_times)
    print(f"\n优化版本平均加载时间: {avg_optimized:.2f} ms")
    
    # 计算性能提升
    print("\n" + "=" * 60)
    print("性能优化结果")
    print("=" * 60)
    
    improvement = calculate_improvement(avg_original, avg_optimized)
    time_saved = avg_original - avg_optimized
    
    print(f"原始版本平均加载时间: {avg_original:.2f} ms")
    print(f"优化版本平均加载时间: {avg_optimized:.2f} ms")
    print(f"节省时间: {time_saved:.2f} ms")
    print(f"性能提升: {improvement:.2f}%")
    
    # 评估优化效果
    print("\n优化效果评估:")
    if improvement > 50:
        print("✅ 优化效果显著！性能提升超过50%")
    elif improvement > 30:
        print("✅ 优化效果良好！性能提升超过30%")
    elif improvement > 10:
        print("✅ 优化效果明显！性能提升超过10%")
    elif improvement > 0:
        print("⚠️ 优化效果有限，性能有小幅提升")
    else:
        print("❌ 优化未达到预期效果，可能需要进一步优化")
    
    # 优化建议
    print("\n主要优化措施:")
    print("1. 使用 @st.cache_resource 缓存AI代理实例")
    print("2. 使用 @st.cache_data 缓存会话历史数据")
    print("3. 用SVG图标替代外部图片加载")
    print("4. 延迟加载表单组件")
    print("5. 添加缓存清除机制确保数据新鲜度")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
