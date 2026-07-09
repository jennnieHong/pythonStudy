import psycopg2
import argparse
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="HMS Virtual POS Sales & Settlement Simulator")
    parser.add_argument("--date", type=str, default=datetime.now().strftime("%Y%m%d"), help="Sales Date in YYYYMMDD format (default: today)")
    parser.add_argument("--ms_no", type=str, default="NC0007", help="Store Code (default: NC0007)")
    parser.add_argument("--pos_no", type=str, default="01", help="POS Number (default: 01)")
    parser.add_argument("--sale_amt", type=float, default=50000.0, help="Total Sale Amount (default: 50000.0)")
    parser.add_argument("--cash_amt", type=float, default=10000.0, help="Cash portion of the sales (default: 10000.0)")
    parser.add_argument("--prep_amt", type=float, default=100000.0, help="Open Prep cash / change (default: 100000.0)")
    parser.add_argument("--bill_no", type=str, default="0001", help="Last Receipt Bill Number (default: 0001)")
    
    args = parser.parse_args()
    
    sale_date = args.date
    ms_no = args.ms_no
    pos_no = args.pos_no.zfill(2)
    sale_amt = args.sale_amt
    cash_amt = args.cash_amt
    prep_amt = args.prep_amt
    bill_no = args.bill_no.zfill(4)
    
    # Calculate card amount and vat
    card_amt = sale_amt - cash_amt
    if card_amt < 0:
        print("Error: Cash amount cannot be greater than total sale amount.")
        return
        
    vat_amt = round(sale_amt / 11.0, 2)
    net_sale_amt = sale_amt - vat_amt
    
    # DB connection details
    db_config = {
        "host": "192.168.10.206",
        "port": 5432,
        "database": "edb",
        "user": "hmsfns_was",
        "password": "astems3!"
    }
    
    print("=" * 60)
    print("         HMS VIRTUAL POS SIMULATOR")
    print("=" * 60)
    print(f"  Sales Date     : {sale_date}")
    print(f"  Store Code     : {ms_no}")
    print(f"  POS No         : {pos_no}")
    print(f"  Bill No (Count): {bill_no}")
    print(f"  Total Sale Amt : {sale_amt:,.2f} 원")
    print(f"  - Cash Portion : {cash_amt:,.2f} 원")
    print(f"  - Card Portion : {card_amt:,.2f} 원")
    print(f"  - VAT (10%)    : {vat_amt:,.2f} 원")
    print(f"  - Net Sales    : {net_sale_amt:,.2f} 원")
    print(f"  Prep Cash (준비금): {prep_amt:,.2f} 원")
    print(f"  Expected Cash in Drawer (실물시재): {prep_amt + cash_amt:,.2f} 원")
    print("-" * 60)
    
    try:
        print("Connecting to EDB PostgreSQL...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # 1. Fetch store info (chain_no, chain_area)
        print(f"Querying store master for {ms_no}...")
        cursor.execute("SELECT chain_no, chain_area, ms_nm FROM hmsfns.MMEMBSTB WHERE ms_no = %s;", (ms_no,))
        store_row = cursor.fetchone()
        if not store_row:
            print(f"Warning: Store {ms_no} not found in MMEMBSTB. Using defaults ('C001', '001').")
            chain_no = "C001"
            chain_area = "001"
            ms_nm = "임의가맹점"
        else:
            chain_no = store_row[0] or "C001"
            chain_area = store_row[1] or "001"
            ms_nm = store_row[2]
            print(f"  Found Store: {ms_nm} (Chain: {chain_no}, Area: {chain_area})")
            
        # 2. Clean up existing data for the same key to prevent duplication errors
        print(f"Clearing old simulation data for Date: {sale_date}, Store: {ms_no}, POS: {pos_no}...")
        cursor.execute("""
            DELETE FROM hmsfns.STRNHDTB 
            WHERE sale_date = %s AND ms_no = %s AND pos_no = %s;
        """, (sale_date, ms_no, pos_no))
        deleted_hd = cursor.rowcount
        
        cursor.execute("""
            DELETE FROM hmsfns.SAREGITB 
            WHERE sale_date = %s AND ms_no = %s AND pos_no = %s;
        """, (sale_date, ms_no, pos_no))
        deleted_regi = cursor.rowcount
        print(f"  Removed: {deleted_hd} rows from STRNHDTB, {deleted_regi} rows from SAREGITB")
        
        # 3. Insert into STRNHDTB (POS Transaction Header)
        # We will simulate one transaction matching the totals
        sale_dtime = f"{sale_date}120000" # 12:00:00
        print("Inserting simulated transaction to STRNHDTB...")
        cursor.execute("""
            INSERT INTO hmsfns.STRNHDTB (
                sale_date, ms_no, pos_no, bill_no, chain_no, chain_area, 
                sale_fg, sale_dtime, sale_tot, sale_amt, cash_amt, card_amt, 
                net_sale_amt, vat_amt, detail_cnt, slip_cnt, cancel_yn, native_cnt, foreign_cnt
            ) VALUES (
                %s, %s, %s, %s, %s, %s, 
                '1', %s, %s, %s, %s, %s, 
                %s, %s, 1, 1, 'N', 1, 0
            );
        """, (
            sale_date, ms_no, pos_no, bill_no, chain_no, chain_area,
            sale_dtime, sale_amt, sale_amt, cash_amt, card_amt,
            net_sale_amt, vat_amt
        ))
        
        # 4. Insert into SAREGITB (POS Close Settlement)
        # REGI_TYPE = '0' (Daily Close), Cashier_Id = 'SYSTEM'
        # Set close_stock = prep_amt + cash_amt so cash_loss = 0 (perfect match)
        open_dtime = f"{sale_date}0900" # 09:00
        close_dtime = f"{sale_date}1800" # 18:00
        now_dtime = datetime.now().strftime("%Y%m%d%H%M%S")
        
        print("Inserting simulated settlement to SAREGITB...")
        cursor.execute("""
            INSERT INTO hmsfns.SAREGITB (
                ms_no, sale_date, pos_no, open_dtime, close_dtime, regi_type, 
                cashier_id, cashier_cnt, bill_no,
                tot_amt_cnt, tot_amt, cancel_tot_cnt, cancel_tot, 
                sale_tot_cnt, sale_tot, dc_amt_cnt, dc_amt, 
                sale_amt_cnt, sale_amt, card_amt1_cnt, card_amt1, 
                cash_amt_cnt, cash_amt, pre_amt, cash_tot, close_stock, cash_loss,
                nation_amt_cnt, nation_amt, foreign_amt_cnt, foreign_amt, 
                added_tax, weather_cd, create_dtime, create_id, last_dtime, last_id
            ) VALUES (
                %s, %s, %s, %s, %s, '0', 
                'SYST', 1, %s,
                1, %s, 0, 0, 
                1, %s, 0, 0, 
                1, %s, 1, %s, 
                1, %s, %s, %s, %s, 0.00,
                1, %s, 0, 0.00, 
                %s, '0', %s, 'SYSTEM', %s, 'SYSTEM'
            );
        """, (
            ms_no, sale_date, pos_no, open_dtime, close_dtime, bill_no,
            sale_amt, sale_amt, sale_amt, card_amt,
            cash_amt, prep_amt, cash_amt + prep_amt, cash_amt + prep_amt,
            sale_amt, vat_amt, now_dtime, now_dtime
        ))
        
        conn.commit()
        print("=" * 60)
        print(" [SUCCESS] SIMULATION DATA GENERATION COMPLETED!")
        print("=" * 60)
        print(f"  1. Go to backoffice screen: hq_sysif_00001 (POS정산수집/마감)")
        print(f"  2. Query for Date: '{sale_date}', Store: '{ms_nm}' ({ms_no})")
        print(f"  3. Verify that total amounts match and click [현장마감] (Store Close).")
        print(f"  4. After closing, run the overnight batch to verify inventory reduction.")
        print("=" * 60)
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        print(f"\n [ERROR] Simulation failed: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
