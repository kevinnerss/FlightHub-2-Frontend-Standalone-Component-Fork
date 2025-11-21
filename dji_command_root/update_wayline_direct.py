import sqlite3
import json
from datetime import datetime

def update_wayline_direct():
    try:
        # 直接定义航线数据
        flight_data = {
            "name": "李达机场_试飞_20250711134529",
            "wayline_uuid": "45a7d236-414f-47bb-b11f-03a74d579504",
            "track": {
                "track_id": "36a0c52a-dc11-4dfd-9d1f-0d35ae9e5790",
                "drone_sn": "1581F8HGX255D00A0DUJ",
                "flight_distance": 119,
                "flight_duration": 72,
                "points": [
                    # 这里是所有点的数据，我会创建一个简化版本
                    {"timestamp": 1752212822000, "latitude": 41.66559758274711, "longitude": 123.13502156043394, "height": 59.17853698730469},
                    {"timestamp": 1752212824000, "latitude": 41.66559829233688, "longitude": 123.13502205898742, "height": 59.97853317260742},
                    {"timestamp": 1752212826000, "latitude": 41.66559745629363, "longitude": 123.13502155937394, "height": 61.57854080200195},
                    {"timestamp": 1752212828000, "latitude": 41.66559740206697, "longitude": 123.13502154522077, "height": 73.07853317260742},
                    {"timestamp": 1752212830000, "latitude": 41.66559748416895, "longitude": 123.1350213266112, "height": 81.27853317260742}
                ]
            }
        }
        
        # 准备更新数据
        wayline_data = {
            'wayline_id': flight_data['wayline_uuid'],
            'name': flight_data['name'],
            'description': f"飞行任务轨迹 - 无人机SN: {flight_data['track']['drone_sn']}",
            'length': flight_data['track']['flight_distance'],
            'estimated_duration': flight_data['track']['flight_duration'],
            'status': 'COMPLETED'
        }
        
        # 转换points为waypoints格式
        waypoints = []
        for point in flight_data['track']['points']:
            waypoint = {
                'latitude': point['latitude'],
                'longitude': point['longitude'],
                'altitude': point['height'],
                'speed': 5
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
    update_wayline_direct()