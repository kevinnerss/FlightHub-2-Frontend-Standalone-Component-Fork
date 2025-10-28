import requests
import json

# 后端API基础URL
BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_api_connectivity():
    """
    测试后端API连通性
    """
    print("开始测试后端API连通性...")
    
    # 测试1: 获取告警类型
    print("\n1. 测试获取告警类型:")
    try:
        response = requests.get(f"{BASE_URL}/alarmtypes/")
        if response.status_code == 200:
            alarm_types = response.json()
            print(f"   成功获取到 {len(alarm_types)} 个告警类型:")
            for alarm_type in alarm_types:
                print(f"   - {alarm_type['name']} ({alarm_type['code']})")
        else:
            print(f"   失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 测试2: 获取告警信息
    print("\n2. 测试获取告警信息:")
    try:
        response = requests.get(f"{BASE_URL}/alarms/")
        if response.status_code == 200:
            alarms = response.json()
            print(f"   成功获取到 {len(alarms)} 条告警信息")
            if alarms:
                alarm = alarms[0]
                print(f"   最新告警: {alarm['type_name']} - {alarm['content']}")
        else:
            print(f"   失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 测试3: 获取特定告警
    print("\n3. 测试获取特定告警:")
    try:
        response = requests.get(f"{BASE_URL}/alarms/1/")
        if response.status_code == 200:
            alarm = response.json()
            print(f"   成功获取告警ID为1的信息:")
            print(f"   - 类型: {alarm['type_name']}")
            print(f"   - 内容: {alarm['content']}")
            print(f"   - 状态: {alarm['status']}")
        elif response.status_code == 404:
            print("   告警ID为1的记录不存在")
        else:
            print(f"   失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   错误: {e}")

def test_frontend_connectivity():
    """
    测试前端连接后端API
    """
    print("\n\n开始测试前端连接后端API...")
    
    # 模拟前端请求告警信息
    print("\n1. 模拟前端获取告警列表:")
    try:
        # 设置允许跨域的headers
        headers = {
            'Content-Type': 'application/json',
        }
        
        response = requests.get(f"{BASE_URL}/alarms/", headers=headers)
        if response.status_code == 200:
            alarms = response.json()
            print(f"   前端成功获取到 {len(alarms)} 条告警信息")
            
            # 模拟前端处理数据
            high_priority_alarms = [alarm for alarm in alarms if alarm['status'] == 'PENDING']
            print(f"   其中 {len(high_priority_alarms)} 条为待处理状态")
        else:
            print(f"   失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   错误: {e}")

if __name__ == "__main__":
    test_api_connectivity()
    test_frontend_connectivity()
    print("\n测试完成!")