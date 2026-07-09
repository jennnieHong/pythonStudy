import pandas as pd
df = pd.read_excel(r"D:\hmTest\Backoffice_Screen_TestAccount_v2.xlsx")
# 컬럼명 임의 지정하여 확인
df.columns = ['class1', 'class2', 'screen_name', 'view_file', 'url', 'user_id', 'password', 'name', 'sys_type', 'role', 'group', 'hq_yn', 'event_role', 'menu_order']
target_screens = ['hq_vendor_00009', 'st_vendor_00006']
filtered_df = df[df['view_file'].isin(target_screens)]
print(filtered_df[['view_file', 'user_id', 'password', 'role', 'hq_yn']])
