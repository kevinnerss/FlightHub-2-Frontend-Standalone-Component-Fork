import sqlite3
conn = sqlite3.connect('db.sqlite3')
rows = conn.execute("select name from sqlite_master where type='table'").fetchall()
print(rows[:5])
conn.close()
