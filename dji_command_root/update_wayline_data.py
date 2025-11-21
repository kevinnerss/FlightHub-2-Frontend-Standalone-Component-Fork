import sqlite3
import json
import os
from datetime import datetime

def update_wayline_data():
    try:
        # 读取航线信息文件
        file_path = '..\航线信息.md'
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取JSON部分，跳过前面的说明文字
        # 直接查找第一个大括号
        json_start = content.find('{')
        if json_start == -1:
            raise ValueError("无法找到JSON数据")
        
        # 从第一个大括号开始，确保获取完整的JSON
        json_content = content[json_start:]
        
        # 解析JSON数据
        data = json.loads(json_content)
        # 确保使用正确的变量名data而不是json_data

        flight_data = data['data']
        track_data = flight_data['track']
        
        # 准备更新数据
        wayline_data = {
            'wayline_id': flight_data['wayline_uuid'],
            'name': flight_data['name'],
            'description': f"飞行任务轨迹 - 无人机SN: {track_data['drone_sn']}",
            'length': track_data['flight_distance'],
            'estimated_duration': track_data['flight_duration'],
            'status': 'COMPLETED'
        }
        
        # 转换points为waypoints格式
        waypoints = []
        for point in track_data['points']:
            waypoint = {
                'latitude': point['latitude'],
                'longitude': point['longitude'],
                'altitude': point['height'],
                'speed': 5  # 默认速度，根据实际情况可调整
            }
            waypoints.append(waypoint)
        
        wayline_data['waypoints'] = json.dumps(waypoints, ensure_ascii=False)
        wayline_data['created_by'] = 'system'
        wayline_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        wayline_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        print("准备更新的数据:")
        print(f"航线名称: {wayline_data['name']}")
        print(f"航线ID: {wayline_data['wayline_id']}")
        print(f"飞行距离: {wayline_data['length']}米")
        print(f"飞行时长: {wayline_data['estimated_duration']}秒")
        print(f"航点数量: {len(waypoints)}")
        
        # 连接数据库
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # 检查是否已存在该航线ID
        cursor.execute("SELECT id FROM telemetry_app_wayline WHERE wayline_id = ?", (wayline_data['wayline_id'],))
        existing = cursor.fetchone()
        
        if existing:
            # 更新现有记录
            cursor.execute("""
                UPDATE telemetry_app_wayline 
                SET name = ?, description = ?, waypoints = ?, length = ?, 
                    estimated_duration = ?, status = ?, updated_at = ? 
                WHERE wayline_id = ?
            """, (
                wayline_data['name'], wayline_data['description'], wayline_data['waypoints'],
                wayline_data['length'], wayline_data['estimated_duration'], wayline_data['status'],
                wayline_data['updated_at'], wayline_data['wayline_id']
            ))
            print(f"已更新ID为 {existing[0]} 的记录")
        else:
            # 插入新记录
            cursor.execute("""
                INSERT INTO telemetry_app_wayline 
                (wayline_id, name, description, waypoints, length, estimated_duration, 
                 status, created_by, created_at, updated_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                wayline_data['wayline_id'], wayline_data['name'], wayline_data['description'],
                wayline_data['waypoints'], wayline_data['length'], wayline_data['estimated_duration'],
                wayline_data['status'], wayline_data['created_by'], wayline_data['created_at'],
                wayline_data['updated_at']
            ))
            print(f"已插入新记录，ID为 {cursor.lastrowid}")
        
        # 提交事务
        conn.commit()
        print("数据库更新成功！")
        
    except Exception as e:
        print(f"更新出错: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    update_wayline_data()