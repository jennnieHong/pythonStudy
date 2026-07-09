import pandas as pd

dirty_data = {
    "매장코드": [" nc0002 ", "NC0007", "nc0005  ", "NC0002", "NC9999"],
    "매장정보": ["SEOUL_SHOP_01", "BUSAN_CAFE_02", "INCHEON_SHOP_01", "SEOUL_SHOP_01", "DAEGU_DELI_99"],
    "거래일자": ["2026/07/07", "2026-07-07", "20260707", "2026-07-07", "2026.07.07"],
    "금일매출": ["5,200,000", "3,800,000", "N/A", "5,200,000", None],
    "고객연락처": ["010-1234-5678", "010-9876-5432", "010-5555-6666", "010-1234-5678", "010-1111-2222"]
}

df = pd.DataFrame(dirty_data)
df.to_excel(r"D:\hmTest\backoffice\QaReport\dirty_sales.xlsx", index=False)
print("Generated dirty_sales.xlsx for hands-on practice!")
