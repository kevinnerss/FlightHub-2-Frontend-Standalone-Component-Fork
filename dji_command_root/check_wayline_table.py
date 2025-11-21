import sqlite3
import json

def check_wayline_table():
    try:
        # 连接数据库
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        print("查询 telemetry_app_wayline 表结构:")
        # 获取表结构
        cursor.execute("PRAGMA table_info(telemetry_app_wayline)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"- {col[1]}: {col[2]}")
        
        print("\n查询 telemetry_app_wayline 表数据:")
        # 查询表数据
        cursor.execute("SELECT * FROM telemetry_app_wayline LIMIT 10")
        rows = cursor.fetchall()
        
        if rows:
            # 获取列名
            col_names = [desc[0] for desc in cursor.description]
            print(f"找到 {len(rows)} 条记录")
            
            # 查询特定的新记录（我们刚刚更新的航线）
            cursor.execute("SELECT * FROM telemetry_app_wayline WHERE wayline_id = '45a7d236-414f-47bb-b11f-03a74d579504'")
            target_row = cursor.fetchone()
            
            if target_row:
                print("\n刚刚更新的航线记录:")
                for i, value in enumerate(target_row):
                    if col_names[i] == 'waypoints':
                        print(f"{col_names[i]}: [包含 {len(json.loads(value))} 个航点的数据]")
                        # 只打印前3个航点作为示例
                        try:
                            parsed = json.loads(value)
                            print("  前3个航点示例:")
                            for j, wp in enumerate(parsed[:3]):
                                print(f"  航点{j+1}: {json.dumps(wp, ensure_ascii=False)}")
                        except:
                            pass
                    else:
                        print(f"{col_names[i]}: {value}")
        else:
            print("表中没有数据")
            
    except Exception as e:
        print(f"查询出错: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_wayline_table()