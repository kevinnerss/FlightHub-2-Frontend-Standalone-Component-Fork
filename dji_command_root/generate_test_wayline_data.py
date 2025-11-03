#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成测试航线数据
用于向Wayline表中插入示例数据
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 初始化Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dji_command_root.settings')
django.setup()

from telemetry_app.models import Wayline

def generate_random_waypoints(count=5):
    """生成随机航点数据"""
    waypoints = []
    base_lat, base_lng = 39.9042, 116.4074  # 北京中心坐标
    
    for i in range(count):
        # 在基础坐标附近随机生成航点
        lat = base_lat + (random.random() - 0.5) * 0.1
        lng = base_lng + (random.random() - 0.5) * 0.1
        
        waypoints.append({
            "lat": round(lat, 6),
            "lng": round(lng, 6),
            "altitude": random.randint(50, 150),
            "speed": random.randint(5, 15),
            "stay_time": random.randint(0, 10)
        })
    
    return waypoints

def generate_test_waylines():
    """生成测试航线数据"""
    wayline_templates = [
        {
            "wayline_id": "WL001",
            "name": "电力巡检航线一",
            "description": "110kV输电线路常规巡检，覆盖3基铁塔",
            "status": "ACTIVE",
            "created_by": "admin"
        },
        {
            "wayline_id": "WL002",
            "name": "桥梁检测航线",
            "description": "大跨度桥梁结构安全检测，重点关注桥梁墩柱和梁体",
            "status": "DRAFT",
            "created_by": "engineer1"
        },
        {
            "wayline_id": "WL003",
            "name": "河道巡查航线",
            "description": "城市河道水质监测与垃圾巡查，沿河5公里",
            "status": "ARCHIVED",
            "created_by": "inspector2"
        },
        {
            "wayline_id": "WL004",
            "name": "农林监测航线",
            "description": "农田作物生长状况监测，红外热成像拍摄",
            "status": "ACTIVE",
            "created_by": "agriculturist"
        },
        {
            "wayline_id": "WL005",
            "name": "矿区测绘航线",
            "description": "露天矿区三维建模测绘，网格航线规划",
            "status": "DRAFT",
            "created_by": "surveyor"
        }
    ]
    
    created_count = 0
    
    for template in wayline_templates:
        # 检查是否已存在
        if not Wayline.objects.filter(wayline_id=template["wayline_id"]).exists():
            # 生成航点数据
            waypoints = generate_random_waypoints(random.randint(3, 8))
            
            # 计算模拟的航线长度和预计时间
            length = random.uniform(500, 3000)
            estimated_duration = random.randint(120, 600)
            
            # 生成随机的创建时间
            days_ago = random.randint(1, 30)
            created_at = datetime.now() - timedelta(days=days_ago)
            
            # 创建航线
            wayline = Wayline(
                wayline_id=template["wayline_id"],
                name=template["name"],
                description=template["description"],
                waypoints=waypoints,
                length=round(length, 2),
                estimated_duration=estimated_duration,
                status=template["status"],
                created_by=template["created_by"]
            )
            wayline.created_at = created_at
            wayline.save()
            
            created_count += 1
            print(f"创建航线: {template['wayline_id']} - {template['name']}")
        else:
            print(f"航线已存在: {template['wayline_id']} - {template['name']}")
    
    return created_count

if __name__ == "__main__":
    print("开始生成测试航线数据...")
    count = generate_test_waylines()
    print(f"生成完成，共创建 {count} 条航线数据")