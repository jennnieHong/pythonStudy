import psycopg2

try:
    conn = psycopg2.connect(
        host='192.168.10.206', 
        port='5432', 
        dbname='edb', 
        user='hmsfns_adm', 
        password='astems2!'
    )
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%menu%' AND table_schema = 'hmsfns'")
    rows = cur.fetchall()
    print("Tables containing 'menu':")
    for r in rows:
        print(r[0])
    cur.close()
    conn.close()
except Exception as e:
    print("Error:", e)
