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
    SELECT tgname, relname
    FROM pg_trigger tg
    JOIN pg_class c ON c.oid = tg.tgrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'hmsfns' AND c.relname = 'mnamemtb';
""")
rows = cur.fetchall()
print("=== Triggers on hmsfns.mnamemtb ===")
for r in rows:
    print(r)

cur.close()
conn.close()
