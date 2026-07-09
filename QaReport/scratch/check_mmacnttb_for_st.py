import psycopg2
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn_params = {
    "host": "192.168.10.206",
    "port": 5432,
    "database": "edb",
    "user": "hmsfns_was",
    "password": "astems3!"
}

try:
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()
    
    # 1. NC0021 매장의 MMACNTTB (가맹점 계정 마스터) 조회
    cursor.execute("""
        SELECT MS_NO, ACNT_FG, ACNT_CD, ACNT_NM, USE_YN
        FROM hmsfns.MMACNTTB
        WHERE MS_NO = 'NC0021'
        ORDER BY ACNT_FG, ACNT_CD
    """)
    rows = cursor.fetchall()
    print("--- MMACNTTB records for NC0021 ---")
    for r in rows:
        print(f"MS_NO: {r[0]} | ACNT_FG: {r[1]} | ACNT_CD: {r[2]} | ACNT_NM: {r[3]} | USE_YN: {r[4]}")
        
    cursor.close()
    conn.close()
except Exception as e:
    print("Error:", e)
