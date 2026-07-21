import psycopg2

conn = psycopg2.connect(
    host='192.168.10.206', 
    port='5432', 
    dbname='edb', 
    user='hmsfns_adm', 
    password='astems2!'
)
cur = conn.cursor()

cur.execute("""
    SELECT relname 
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'hmsfns' AND c.relname LIKE 'ss%';
""")
rows = cur.fetchall()
print("=== All tables starting with ss ===")
for r in rows:
    print(r[0])

cur.close()
conn.close()
