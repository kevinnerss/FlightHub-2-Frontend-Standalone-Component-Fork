#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
更新数据库表结构以适应航线信息.md的数据格式
"""

import sqlite3
import os

# 获取数据库文件路径
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

# SQL语句列表
sql_statements = [
    # 添加缺失的字段
    "ALTER TABLE telemetry_app_wayline ADD COLUMN track_id VARCHAR(50) NULL;",
    "ALTER TABLE telemetry_app_wayline ADD COLUMN drone_sn VARCHAR(50) NULL;",
    
    # 添加索引
    "CREATE INDEX IF NOT EXISTS idx_telemetry_app_wayline_wayline_id ON telemetry_app_wayline(wayline_id);",
    "CREATE INDEX IF NOT EXISTS idx_telemetry_app_wayline_track_id ON telemetry_app_wayline(track_id);",
    "CREATE INDEX IF NOT EXISTS idx_telemetry_app_wayline_drone_sn ON telemetry_app_wayline(drone_sn);",
    
    # 更新状态字段
    "UPDATE telemetry_app_wayline SET status = 'COMPLETED' WHERE status IS NULL;"
]

def update_database_structure():
    """执行SQL语句更新数据库结构"""
    try:
        # 连接到SQLite数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"正在更新数据库结构: {db_path}")
        
        # 执行每个SQL语句
        for i, sql in enumerate(sql_statements, 1):
            print(f"执行SQL语句 {i}/{len(sql_statements)}: {sql[:50]}...")
            try:
                cursor.execute(sql)
                conn.commit()
                print(f"  成功!")
            except sqlite3.Error as e:
                # 对于某些错误（如字段已存在），我们可以继续执行
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"  警告: {str(e)}. 跳过此语句。")
                    conn.rollback()
                else:
                    raise
        
        # 验证表结构
        print("\n验证表结构:")
        cursor.execute("PRAGMA table_info(telemetry_app_wayline)")
        columns = cursor.fetchall()
        print(f"表telemetry_app_wayline的字段列表 ({len(columns)}个字段):")
        for col in columns:
            print(f"  {col[1]} - {col[2]}")
        
        print("\n数据库结构更新完成!")
        
    except Exception as e:
        print(f"更新数据库结构时出错: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_database_structure()