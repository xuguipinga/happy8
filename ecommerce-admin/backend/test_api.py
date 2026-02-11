"""
API 测试脚本
使用方法: python test_api.py
"""
import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_login():
    """测试登录接口"""
    print("\n=== 测试登录接口 ===")
    url = f'{BASE_URL}/auth/login'
    data = {
        'username': 'admin',
        'password': '123456'
    }
    
    response = requests.post(url, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        token = response.json()['data']['token']
        print(f"\n获取到 Token: {token[:50]}...")
        return token
    return None

def test_get_user_info(token):
    """测试获取用户信息接口"""
    print("\n=== 测试获取用户信息接口 ===")
    url = f'{BASE_URL}/auth/info'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(url, headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_register():
    """测试注册接口"""
    print("\n=== 测试注册接口 ===")
    url = f'{BASE_URL}/auth/register'
    data = {
        'username': 'testuser',
        'password': '123456',
        'email': 'test@example.com',
        'phone': '13900139000'
    }
    
    response = requests.post(url, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

if __name__ == '__main__':
    print("开始测试 API...")
    print(f"基础 URL: {BASE_URL}")
    
    # 测试登录
    token = test_login()
    
    # 如果登录成功，测试获取用户信息
    if token:
        test_get_user_info(token)
    
    # 测试注册（可选，如果用户名已存在会报错）
    # test_register()
    
    print("\n测试完成！")
