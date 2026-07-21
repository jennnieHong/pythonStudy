import psycopg2
import sys

def get_table_metadata(table_name):
    try:
        conn = psycopg2.connect(
            host='192.168.10.206', 
            port='5432', 
            dbname='edb', 
            user='hmsfns_adm', 
            password='astems2!'
        )
        conn.set_client_encoding('UTF8')
        cur = conn.cursor()
        print(f"--- Metadata for table: {table_name} ---")
        
        # 1. Fetch table comment
        cur.execute("""
            SELECT c.relname AS table_name,
                   obj_description(c.oid, 'pg_class') AS comment
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'hmsfns' AND c.relname = %s;
        """, (table_name.lower(),))
        table_info = cur.fetchall()
        print(f"Table Comment: {table_info}")
        
        # 2. Fetch columns
        cur.execute("""
            SELECT a.attname AS column_name,
                   pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
                   a.attnotnull AS not_null,
                   pg_catalog.pg_get_expr(d.adbin, d.adrelid) AS default_value,
                   col_description(a.attrelid, a.attnum) AS comment
            FROM pg_attribute a
            JOIN pg_class c ON c.oid = a.attrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            LEFT JOIN pg_attrdef d ON d.adrelid = c.oid AND d.adnum = a.attnum
            WHERE n.nspname = 'hmsfns'
              AND c.relname = %s
              AND a.attnum > 0
              AND NOT a.attisdropped
            ORDER BY a.attnum;
        """, (table_name.lower(),))
        columns = cur.fetchall()
        print("\nColumns:")
        for col in columns:
            print(col)
            
        # 3. Fetch indexes
        cur.execute("""
            SELECT i.relname AS index_name,
                   pg_get_indexdef(ix.indexrelid) AS index_def
            FROM pg_index ix
            JOIN pg_class t ON t.oid = ix.indrelid
            JOIN pg_class i ON i.oid = ix.indexrelid
            JOIN pg_namespace n ON n.oid = t.relnamespace
            WHERE n.nspname = 'hmsfns' AND t.relname = %s;
        """, (table_name.lower(),))
        indexes = cur.fetchall()
        print("\nIndexes:")
        for idx in indexes:
            print(idx)
            
        # 4. Fetch triggers
        cur.execute("""
            SELECT tgname, tgtype, tgenabled
            FROM pg_trigger t
            JOIN pg_class c ON c.oid = t.tgrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'hmsfns' AND c.relname = %s;
        """, (table_name.lower(),))
        triggers = cur.fetchall()
        print("\nTriggers:")
        for tg in triggers:
            print(tg)
            
        cur.close()
        conn.close()
    except Exception as e:
        print("Error connecting/querying DB:", e)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        get_table_metadata(sys.argv[1])
    else:
        # Default check
        get_table_metadata('if_recpsvtb')
