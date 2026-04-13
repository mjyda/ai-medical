import requests
import json

# 测试阿里云向量化API
def test_aliyun_embedding_api():
    api_key = "sk-357d261f34b3466ba920059907895050"
    model = "text-embedding-v3"
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 测试数据
    test_texts = ["测试文本1", "测试文本2"]

    data = {
        "model": model,
        "input": test_texts
    }

    try:
        print("正在调用阿里云向量化API...")
        print(f"API URL: {url}")
        print(f"Headers: {headers}")
        print(f"Data: {json.dumps(data, ensure_ascii=False)}")
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"\nResponse status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response JSON: {json.dumps(result, ensure_ascii=False, indent=2)}")
            print("\nAPI调用成功！")
        else:
            print(f"Error response: {response.text}")
            print("API调用失败！")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_aliyun_embedding_api()
