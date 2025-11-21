#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将航线信息.md中的完整数据导入到更新后的数据库表中
确保所有字段都按照航线信息.md的标准填充
"""

import sqlite3
import json
import os
from datetime import datetime

# 获取数据库文件路径
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

# 航线信息数据 - 从航线信息.md提取的完整数据
wayline_data = {
    "name": "李达机场_试飞_20250711134529",
    "wayline_uuid": "45a7d236-414f-47bb-b11f-03a74d579504",
    "track": {
        "track_id": "36a0c52a-dc11-4dfd-9d1f-0d35ae9e5790",
        "drone_sn": "1581F8HGX255D00A0DUJ",
        "flight_distance": 119,
        "flight_duration": 72,
        "points": [
            {"timestamp": 1752212822000, "latitude": 41.66559758274711, "longitude": 123.13502156043394, "height": 59.17853698730469},
            {"timestamp": 1752212824000, "latitude": 41.66559829233688, "longitude": 123.13502205898742, "height": 59.97853317260742},
            {"timestamp": 1752212826000, "latitude": 41.66559745629363, "longitude": 123.13502155937394, "height": 61.57854080200195},
            {"timestamp": 1752212828000, "latitude": 41.66559740206697, "longitude": 123.13502154522077, "height": 73.07853317260742},
            {"timestamp": 1752212830000, "latitude": 41.66559748416895, "longitude": 123.1350213266112, "height": 81.27853317260742},
            {"timestamp": 1752212832000, "latitude": 41.6655974877486, "longitude": 123.13502112136484, "height": 83.8785331726074},
            {"timestamp": 1752212834000, "latitude": 41.6655976509515, "longitude": 123.1350214197944, "height": 84.6785331726074},
            {"timestamp": 1752212836000, "latitude": 41.6655959755104, "longitude": 123.13502038943912, "height": 85.07853317260742},
            {"timestamp": 1752212838000, "latitude": 41.66559617446769, "longitude": 123.13502053614363, "height": 88.57853317260742},
            {"timestamp": 1752212840000, "latitude": 41.6655959485027, "longitude": 123.13502029435965, "height": 98.67854080200195},
            {"timestamp": 1752212842000, "latitude": 41.6655962149445, "longitude": 123.13502054411366, "height": 110.17853317260742},
            {"timestamp": 1752212844000, "latitude": 41.66559623166775, "longitude": 123.13502054087192, "height": 115.27853317260742},
            {"timestamp": 1752212846000, "latitude": 41.66559689736686, "longitude": 123.13502011720891, "height": 115.17854080200195},
            {"timestamp": 1752212848000, "latitude": 41.6655964560184, "longitude": 123.13502095739821, "height": 115.07854080200195},
            {"timestamp": 1752212850000, "latitude": 41.6655964835894, "longitude": 123.13502085578143, "height": 115.07853317260742},
            {"timestamp": 1752212852000, "latitude": 41.665595879466224, "longitude": 123.1350212879203, "height": 115.07853317260742},
            {"timestamp": 1752212854000, "latitude": 41.66559626852001, "longitude": 123.13502019414695, "height": 115.07854080200195},
            {"timestamp": 1752212856000, "latitude": 41.66559610918616, "longitude": 123.13502005526571, "height": 114.17853317260742},
            {"timestamp": 1752212858000, "latitude": 41.6655955951042, "longitude": 123.1350197534895, "height": 109.47854080200196},
            {"timestamp": 1752212860000, "latitude": 41.66559581888834, "longitude": 123.13501971366703, "height": 100.87854080200196},
            {"timestamp": 1752212862000, "latitude": 41.66559634810426, "longitude": 123.13501974910447, "height": 90.77853317260742},
            {"timestamp": 1752212864000, "latitude": 41.665596532087925, "longitude": 123.13501979941783, "height": 82.6785331726074},
            {"timestamp": 1752212866000, "latitude": 41.6655970961519, "longitude": 123.13501966857135, "height": 76.1785331726074},
            {"timestamp": 1752212868000, "latitude": 41.6655966964549, "longitude": 123.13501976810834, "height": 71.07854080200195},
            {"timestamp": 1752212870000, "latitude": 41.66559683527166, "longitude": 123.13501979633612, "height": 67.17854080200195},
            {"timestamp": 1752212872000, "latitude": 41.665596981954835, "longitude": 123.13501959682122, "height": 64.17854080200195},
            {"timestamp": 1752212874000, "latitude": 41.665596831883, "longitude": 123.1350197366469, "height": 61.778540802001956},
            {"timestamp": 1752212876000, "latitude": 41.6655962320401, "longitude": 123.1350195894465, "height": 60.07853698730469},
            {"timestamp": 1752212878000, "latitude": 41.6655962194249, "longitude": 123.13501972597463, "height": 58.67853698730469},
            {"timestamp": 1752212880000, "latitude": 41.665596347346124, "longitude": 123.13501959002578, "height": 57.57853698730469},
            {"timestamp": 1752212882000, "latitude": 41.665595954480516, "longitude": 123.13502003218336, "height": 56.7785369873047},
            {"timestamp": 1752212884000, "latitude": 41.66559617921498, "longitude": 123.13501996221038, "height": 56.17853698730469},
            {"timestamp": 1752212886000, "latitude": 41.66559652272202, "longitude": 123.13501995789302, "height": 55.7785369873047},
            {"timestamp": 1752212888000, "latitude": 41.6655964267787, "longitude": 123.13501985487062, "height": 55.478536987304686},
            {"timestamp": 1752212890000, "latitude": 41.6655960624709, "longitude": 123.13501997513679, "height": 55.17853698730469}
        ]
    }
}

def import_wayline_data():
    """导入航线数据到数据库"""
    try:
        # 连接到SQLite数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"正在导入航线数据到数据库: {db_path}")
        
        # 准备数据
        wayline_id = wayline_data["wayline_uuid"]
        name = wayline_data["name"]
        track_id = wayline_data["track"]["track_id"]
        drone_sn = wayline_data["track"]["drone_sn"]
        flight_distance = wayline_data["track"]["flight_distance"]
        flight_duration = wayline_data["track"]["flight_duration"]
        waypoints_json = json.dumps(wayline_data["track"]["points"])
        status = "COMPLETED"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 检查记录是否已存在
        cursor.execute("SELECT id FROM telemetry_app_wayline WHERE wayline_id = ?", (wayline_id,))
        existing_record = cursor.fetchone()
        
        if existing_record:
            # 更新现有记录
            update_sql = """
            UPDATE telemetry_app_wayline 
            SET name = ?, track_id = ?, drone_sn = ?, length = ?, estimated_duration = ?, 
                waypoints = ?, status = ?, updated_at = ?
            WHERE wayline_id = ?
            """
            cursor.execute(update_sql, (
                name, track_id, drone_sn, flight_distance, flight_duration,
                waypoints_json, status, current_time, wayline_id
            ))
            conn.commit()
            print(f"成功更新记录，ID: {existing_record[0]}")
        else:
            # 插入新记录
            insert_sql = """
            INSERT INTO telemetry_app_wayline 
            (wayline_id, name, track_id, drone_sn, length, estimated_duration, 
             waypoints, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_sql, (
                wayline_id, name, track_id, drone_sn, flight_distance, flight_duration,
                waypoints_json, status, current_time, current_time
            ))
            conn.commit()
            new_id = cursor.lastrowid
            print(f"成功插入新记录，ID: {new_id}")
        
        # 验证导入的数据
        print("\n验证导入的数据:")
        cursor.execute("""
        SELECT id, wayline_id, name, track_id, drone_sn, length, estimated_duration, status 
        FROM telemetry_app_wayline 
        WHERE wayline_id = ?
        """, (wayline_id,))
        record = cursor.fetchone()
        
        if record:
            print(f"记录ID: {record[0]}")
            print(f"航线ID (wayline_id): {record[1]}")
            print(f"名称 (name): {record[2]}")
            print(f"轨迹ID (track_id): {record[3]}")
            print(f"无人机序列号 (drone_sn): {record[4]}")
            print(f"飞行距离 (length): {record[5]}")
            print(f"飞行时长 (estimated_duration): {record[6]} 秒")
            print(f"状态 (status): {record[7]}")
            
            # 检查航点数量
            cursor.execute("SELECT waypoints FROM telemetry_app_wayline WHERE wayline_id = ?", (wayline_id,))
            waypoints_data = cursor.fetchone()[0]
            waypoints = json.loads(waypoints_data)
            print(f"航点数量: {len(waypoints)}")
        
        print("\n航线数据导入完成!")
        
    except Exception as e:
        print(f"导入航线数据时出错: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    import_wayline_data()