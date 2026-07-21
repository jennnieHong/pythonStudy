import psycopg2

conn = psycopg2.connect(
    host='192.168.10.206', 
    port='5432', 
    dbname='edb', 
    user='hmsfns_adm', 
    password='astems2!'
)
cur = conn.cursor()

# Search in pg_proc (stored procedures/functions)
cur.execute("""
    SELECT proname, prosrc
    FROM pg_proc
    WHERE prosrc ILIKE '%ssnametb%';
""")
rows = cur.fetchall()
print("=== Procedures referencing ssnametb ===")
for r in rows:
    print(r[0])

# Search in pg_trigger
cur.execute("""
    SELECT tgname, relname
    FROM pg_trigger tg
    JOIN pg_class c ON c.oid = tg.tgrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE tgname ILIKE '%ssname%';
""")
rows = cur.fetchall()
print("\n=== Triggers referencing ssname ===")
for r in rows:
    print(r)

cur.close()
conn.close()
