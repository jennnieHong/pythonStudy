import psycopg2

conn = psycopg2.connect(
    host='192.168.10.206', 
    port='5432', 
    dbname='edb', 
    user='hmsfns_adm', 
    password='astems2!'
)
cur = conn.cursor()

# Get triggers on mnamemtb
cur.execute("""
    SELECT trigger_name, event_manipulation, action_statement
    FROM information_schema.triggers
    WHERE event_object_table = 'mnamemtb';
""")
rows = cur.fetchall()
print("=== Triggers on mnamemtb ===")
for r in rows:
    print(r)

# Get triggers that mention ssnametb
cur.execute("""
    SELECT trigger_name, event_object_table, action_statement
    FROM information_schema.triggers
    WHERE action_statement LIKE '%ssnametb%' OR action_statement LIKE '%SSNAMETB%';
""")
rows = cur.fetchall()
print("\n=== Triggers modifying ssnametb ===")
for r in rows:
    print(r)

cur.close()
conn.close()
