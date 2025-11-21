#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
全面验证数据库表结构和数据是否符合航线信息.md的标准
"""

import sqlite3
import json
import os

def validate_database():
    """验证数据库表结构和数据"""
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== 数据库表结构和数据验证 ===")
        print(f"数据库路径: {db_path}")
        
        # 1. 验证表结构
        print("\n1. 验证表结构:")
        cursor.execute("PRAGMA table_info(telemetry_app_wayline)")
        columns = cursor.fetchall()
        
        # 期望的关键字段
        expected_fields = [
            'id', 'wayline_id', 'name', 'track_id', 'drone_sn', 
            'waypoints', 'length', 'estimated_duration', 'status',
            'created_at', 'updated_at'
        ]
        
        # 检查字段是否存在
        column_names = [col[1] for col in columns]
        print(f"表中现有字段 ({len(column_names)} 个): {', '.join(column_names)}")
        
        all_fields_exist = True
        missing_fields = []
        for field in expected_fields:
            if field not in column_names:
                missing_fields.append(field)
                all_fields_exist = False
        
        if missing_fields:
            print(f"❌ 缺失关键字段: {', '.join(missing_fields)}")
        else:
            print("✅ 所有关键字段都已存在")
        
        # 2. 验证示例数据
        print("\n2. 验证示例数据:")
        target_wayline_id = "45a7d236-414f-47bb-b11f-03a74d579504"
        
        cursor.execute("""
        SELECT id, wayline_id, name, track_id, drone_sn, length, 
               estimated_duration, status, waypoints
        FROM telemetry_app_wayline 
        WHERE wayline_id = ?
        """, (target_wayline_id,))
        record = cursor.fetchone()
        
        if record:
            print(f"✅ 找到目标记录，ID: {record[0]}")
            
            # 验证关键字段的值
            validation_results = [
                ("wayline_id", record[1], target_wayline_id, record[1] == target_wayline_id),
                ("name", record[2], "李达机场_试飞_20250711134529", record[2] == "李达机场_试飞_20250711134529"),
                ("track_id", record[3], "36a0c52a-dc11-4dfd-9d1f-0d35ae9e5790", record[3] == "36a0c52a-dc11-4dfd-9d1f-0d35ae9e5790"),
                ("drone_sn", record[4], "1581F8HGX255D00A0DUJ", record[4] == "1581F8HGX255D00A0DUJ"),
                ("length", record[5], 119.0, record[5] == 119.0),
                ("estimated_duration", record[6], 72, record[6] == 72),
                ("status", record[7], "COMPLETED", record[7] == "COMPLETED")
            ]
            
            print("\n字段值验证:")
            all_values_correct = True
            for field_name, actual, expected, is_correct in validation_results:
                status = "✅" if is_correct else "❌"
                if not is_correct:
                    all_values_correct = False
                print(f"  {status} {field_name}: {actual} {'==' if is_correct else '!='} {expected}")
            
            # 验证航点数据
            print("\n航点数据验证:")
            try:
                waypoints = json.loads(record[8])
                print(f"  ✅ 航点JSON格式正确")
                print(f"  ✅ 航点数量: {len(waypoints)} (期望35个)")
                
                if len(waypoints) >= 1:
                    first_point = waypoints[0]
                    expected_keys = ['timestamp', 'latitude', 'longitude', 'height']
                    point_keys_ok = all(key in first_point for key in expected_keys)
                    print(f"  ✅ 航点数据结构正确: {', '.join(expected_keys)}")
                    print(f"  示例航点1: 时间戳={first_point['timestamp']}, 经纬度=({first_point['latitude']}, {first_point['longitude']}), 高度={first_point['height']}")
            except Exception as e:
                print(f"  ❌ 航点数据解析错误: {str(e)}")
        else:
            print(f"❌ 未找到目标记录 (wayline_id: {target_wayline_id})")
        
        # 3. 验证表中的所有记录
        print("\n3. 验证表中的所有记录:")
        cursor.execute("SELECT COUNT(*) FROM telemetry_app_wayline")
        total_records = cursor.fetchone()[0]
        print(f"总记录数: {total_records}")
        
        # 4. 验证索引
        print("\n4. 验证索引:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='telemetry_app_wayline'")
        indexes = cursor.fetchall()
        index_names = [idx[0] for idx in indexes]
        print(f"现有索引: {', '.join(index_names)}")
        
        expected_indexes = [
            'idx_telemetry_app_wayline_wayline_id',
            'idx_telemetry_app_wayline_track_id', 
            'idx_telemetry_app_wayline_drone_sn'
        ]
        
        for idx in expected_indexes:
            if idx in index_names:
                print(f"  ✅ 索引 {idx} 已创建")
            else:
                print(f"  ⚠️  索引 {idx} 未创建 (可选)")
        
        print("\n=== 验证总结 ===")
        if all_fields_exist and record and all_values_correct:
            print("🎉 数据库表结构和数据已完全符合航线信息.md的标准!")
        else:
            print("⚠️  数据库验证存在一些问题，请检查上面的详细报告。")
            
    except Exception as e:
        print(f"验证过程中出错: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    validate_database()