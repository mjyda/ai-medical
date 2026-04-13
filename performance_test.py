"""
性能测试脚本 - 比较优化前后的前端性能
"""

import time
import subprocess
import requests
import statistics

def measure_page_load_time(url, iterations=5):
    """测量页面加载时间"""
    load_times = []
    
    for i in range(iterations):
        start_time = time.time()
        try:
            response = requests.get(url, timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                load_time = (end_time - start_time) * 1000  # 转换为毫秒
                load_times.append(load_time)
                print(f"  第 {i+1} 次加载: {load_time:.2f} ms")
            else:
                print(f"  第 {i+1} 次加载失败: HTTP {response.status_code}")
        except Exception as e:
            print(f"  第 {i+1} 次加载失败: {e}")
    
    if load_times:
        avg_time = statistics.mean(load_times)
        median_time = statistics.median(load_times)
        min_time = min(load_times)
        max_time = max(load_times)
        
        return {
            'average': avg_time,
            'median': median_time,
            'min': min_time,
            'max': max_time,
            'all_times': load_times
        }
    else:
        return None

def start_streamlit_app(script_name, port=8501):
    """启动Streamlit应用"""
    try:
        # 检查端口是否已被占用
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"端口 {port} 已被占用，尝试停止现有进程...")
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'streamlit.exe'], 
                             capture_output=True, timeout=5)
                time.sleep(2)
            except:
                pass
        
        # 启动新的Streamlit应用
        print(f"启动 {script_name}...")
        process = subprocess.Popen(
            ['streamlit', 'run', script_name, '--server.port', str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待应用启动
        print("等待应用启动...")
        time.sleep(8)  # 给应用足够时间启动
        
        return process, f"http://localhost:{port}"
    except Exception as e:
        print(f"启动应用失败: {e}")
        return None, None

def stop_streamlit_app(process):
    """停止Streamlit应用"""
    if process:
        try:
            process.terminate()
            time.sleep(2)
            if process.poll() is None:
                process.kill()
            print("应用已停止")
        except Exception as e:
            print(f"停止应用失败: {e}")

def compare_performance(original_time, optimized_time):
    """比较性能提升"""
    if original_time and optimized_time:
        improvement = ((original_time - optimized_time) / original_time) * 100
        
        print("\n" + "=" * 60)
        print("性能对比结果")
        print("=" * 60)
        print(f"优化前平均加载时间: {original_time:.2f} ms")
        print(f"优化后平均加载时间: {optimized_time:.2f} ms")
        print(f"性能提升: {improvement:.2f}%")
        print(f"节省时间: {(original_time - optimized_time):.2f} ms")
        print("=" * 60)
        
        return improvement
    return 0

def main():
    """主函数"""
    print("=" * 60)
    print("Streamlit前端性能测试")
    print("=" * 60)
    
    # 测试优化前版本
    print("\n测试优化前版本...")
    original_process, original_url = start_streamlit_app("app/frontend/app.py", 8501)
    
    if original_process and original_url:
        print(f"应用已启动: {original_url}")
        print("开始测量性能...")
        
        original_results = measure_page_load_time(original_url, iterations=5)
        
        if original_results:
            print(f"\n优化前性能统计:")
            print(f"  平均加载时间: {original_results['average']:.2f} ms")
            print(f"  中位数加载时间: {original_results['median']:.2f} ms")
            print(f"  最快加载时间: {original_results['min']:.2f} ms")
            print(f"  最慢加载时间: {original_results['max']:.2f} ms")
        
        stop_streamlit_app(original_process)
        time.sleep(3)  # 等待端口释放
    
    # 测试优化后版本
    print("\n测试优化后版本...")
    optimized_process, optimized_url = start_streamlit_app("app/frontend/app_optimized.py", 8502)
    
    if optimized_process and optimized_url:
        print(f"应用已启动: {optimized_url}")
        print("开始测量性能...")
        
        optimized_results = measure_page_load_time(optimized_url, iterations=5)
        
        if optimized_results:
            print(f"\n优化后性能统计:")
            print(f"  平均加载时间: {optimized_results['average']:.2f} ms")
            print(f"  中位数加载时间: {optimized_results['median']:.2f} ms")
            print(f"  最快加载时间: {optimized_results['min']:.2f} ms")
            print(f"  最慢加载时间: {optimized_results['max']:.2f} ms")
        
        stop_streamlit_app(optimized_process)
    
    # 比较性能
    if original_results and optimized_results:
        improvement = compare_performance(original_results['average'], optimized_results['average'])
        
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

if __name__ == "__main__":
    main()
