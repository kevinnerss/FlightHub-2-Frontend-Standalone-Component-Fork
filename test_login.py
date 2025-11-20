import requests
import json

# 测试登录API
print("开始测试登录功能...\n")

# 测试环境
API_URL = "http://localhost:8001/api/v1/auth/login/"
TEST_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}
TEST_INVALID_CREDENTIALS = {
    "username": "admin",
    "password": "wrongpassword"
}

def test_login_success():
    """测试成功登录"""
    print("1. 测试成功登录...")
    try:
        response = requests.post(API_URL, json=TEST_CREDENTIALS)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            if "key" in data and "user" in data:
                print("   ✅ 登录成功，返回了token和用户信息")
                return data["key"]
            else:
                print("   ❌ 登录响应格式不正确")
        else:
            print(f"   ❌ 登录失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 登录请求异常: {str(e)}")
    return None

def test_login_failure():
    """测试失败登录"""
    print("\n2. 测试失败登录...")
    try:
        response = requests.post(API_URL, json=TEST_INVALID_CREDENTIALS)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 400 or response.status_code == 401:
            print(f"   ✅ 正确拒绝了无效凭证")
        else:
            print(f"   ❌ 未正确处理无效凭证: {response.text}")
    except Exception as e:
        print(f"   ❌ 请求异常: {str(e)}")

def test_token_authentication(token):
    """测试使用token进行身份验证"""
    if not token:
        print("\n3. 跳过token验证测试（因为登录失败）")
        return
    
    print("\n3. 测试token验证...")
    try:
        headers = {"Authorization": f"Token {token}"}
        user_url = "http://localhost:8001/api/v1/users/me/"
        response = requests.get(user_url, headers=headers)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Token验证成功，获取到用户信息")
            print(f"   用户信息: {json.dumps(user_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"   ❌ Token验证失败: {response.text}")
    except Exception as e:
        print(f"   ❌ Token验证请求异常: {str(e)}")

def test_logout(token):
    """测试登出功能"""
    if not token:
        print("\n4. 跳過登出测试（因为登录失败）")
        return
    
    print("\n4. 测试登出功能...")
    try:
        headers = {"Authorization": f"Token {token}"}
        logout_url = "http://localhost:8001/api/v1/auth/logout/"
        response = requests.post(logout_url, headers=headers)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ 登出成功")
            
            # 验证token是否失效
            user_url = "http://localhost:8001/api/v1/users/me/"
            test_response = requests.get(user_url, headers=headers)
            if test_response.status_code == 401:
                print("   ✅ Token已成功失效")
            else:
                print("   ❌ Token未失效，登出不完全")
        else:
            print(f"   ❌ 登出失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 登出请求异常: {str(e)}")

if __name__ == "__main__":
    # 运行所有测试
    token = test_login_success()
    test_login_failure()
    test_token_authentication(token)
    test_logout(token)
    
    print("\n测试完成!")