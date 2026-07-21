import psycopg2

conn = psycopg2.connect("postgresql://hmsadmin:hmsadmin@127.0.0.1:5432/hmsdb")
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%menu%' AND table_schema = 'hmsfns'")
rows = cur.fetchall()
print("Tables containing 'menu':")
for r in rows:
    print(r[0])
cur.close()
conn.close()
