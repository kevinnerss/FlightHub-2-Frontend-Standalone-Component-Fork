import os
import sqlite3

# 数据库文件路径
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')

print(f'检查数据库: {db_path}')
print(f'文件存在: {os.path.exists(db_path)}')

if os.path.exists(db_path):
    try:
        # 连接到SQLite数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        print('\n数据库中的所有表:')
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            print(f'- {table[0]}')
        
        # 检查是否存在用户表
        user_tables = [t[0] for t in tables if 'user' in t[0].lower()]
        print(f'\n与用户相关的表: {user_tables}')
        
        # 检查telemetry_app_user表
        if 'telemetry_app_user' in [t[0] for t in tables]:
            print('\ntelemetry_app_user表的列:')
            cursor.execute("PRAGMA table_info(telemetry_app_user);")
            columns = cursor.fetchall()
            for col in columns:
                print(f'- {col[1]} ({col[2]})')
            
            # 检查是否有数据
            cursor.execute("SELECT COUNT(*) FROM telemetry_app_user;")
            count = cursor.fetchone()[0]
            print(f'\n用户表中的记录数: {count}')
            
            if count > 0:
                print('\n用户表数据:')
                cursor.execute("SELECT id, username, name, role FROM telemetry_app_user;")
                users = cursor.fetchall()
                for user in users:
                    print(f'- ID: {user[0]}, 用户名: {user[1]}, 姓名: {user[2]}, 角色: {user[3]}')
        
        conn.close()
        print('\n数据库检查完成')
        
    except Exception as e:
        print(f'\n数据库检查失败: {str(e)}')
else:
    print('数据库文件不存在')