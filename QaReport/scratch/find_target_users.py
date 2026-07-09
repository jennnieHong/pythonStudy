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
    
    # 1. ACCT_ENABLE = 'Y', FST_LOGIN_PW_CHANGE = 'Y', SYSTEM_TYPE = 'ST'인 사용자 조회
    query = """
        SELECT USER_ID, USER_NM, MS_NO, ACCT_ENABLE, FST_LOGIN_PW_CHANGE, ACCT_LOCK, ACCT_EXPIRE, PW_EXPIRE, ACCT_ROLE
        FROM hmsfns.MUSERSTB
        WHERE SYSTEM_TYPE = 'ST'
          AND ACCT_ENABLE = 'Y'
          AND FST_LOGIN_PW_CHANGE = 'Y'
        LIMIT 10
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    print("--- Suitable users for ST system (FST_LOGIN_PW_CHANGE = 'Y' & ACCT_ENABLE = 'Y') ---")
    for r in rows:
        print(f"ID: {r[0]} | Name: {r[1]} | MS_NO: {r[2]} | ACCT_ENABLE: {r[3]} | PW_CHANGE: {r[4]} | Lock: {r[5]} | Expire: {r[6]} | PW_Expire: {r[7]} | Role: {r[8]}")
        
    cursor.close()
    conn.close()
except Exception as e:
    print("Error querying database:", e)
