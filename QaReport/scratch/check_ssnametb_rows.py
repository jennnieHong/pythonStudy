import psycopg2

conn = psycopg2.connect(
    host='192.168.10.206', 
    port='5432', 
    dbname='edb', 
    user='hmsfns_adm', 
    password='astems2!'
)
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM hmsfns.mnamemtb;")
cnt = cur.fetchone()[0]
print("Total rows in hmsfns.mnamemtb:", cnt)

if cnt > 0:
    cur.execute("SELECT * FROM hmsfns.mnamemtb LIMIT 5;")
    rows = cur.fetchall()
    for r in rows:
        print(r)

cur.close()
conn.close()
