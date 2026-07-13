import psycopg2

def main():
    conn = psycopg2.connect(
        host='192.168.10.206', 
        port='5432', 
        dbname='edb', 
        user='hmsfns_adm', 
        password='astems2!'
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT a.attname AS column_name,
               pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
               col_description(a.attrelid, a.attnum) AS comment
        FROM pg_attribute a
        JOIN pg_class c ON c.oid = a.attrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'hmsfns'
          AND c.relname = 'sgoodmtb'
          AND a.attnum > 0
          AND NOT a.attisdropped
        ORDER BY a.attnum;
    """)
    rows = cur.fetchall()
    for row in rows:
        print(f"Col: {row[0]}, Type: {row[1]}, Comment: {row[2]}")
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
