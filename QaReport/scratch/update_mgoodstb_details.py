import json

memos_path = r"D:\hmTest\backoffice\QaReport\table_memos.json"

with open(memos_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

mgoodstb_memo = (
    "### 1. 테이블 개요\n"
    "매장별 상품 마스터 테이블 (`MGOODSTB`).\n"
    "본사 표준 상품 마스터(`TGOODSTB`)로부터 각 개별 매장(`MS_NO`)에 취급 허가된 상품 정보를 상속받고, 매장 단위의 전용 공급단가, 판매단가, 수수료, 재고 관리 기준, 판매 상태 정보 등을 개별 관리하는 매장별 상품의 중앙 기준 마스터 테이블입니다.\n\n"
    "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
    "* **본사-매장 마스터 실시간 동기화 (`Tr_TGOODS_T01` 트리거)**: 본사 상품 마스터(`TGOODSTB`)의 데이터가 변경(INSERT/UPDATE/DELETE)될 때, 해당 데이터가 특정 매장에 적용되거나 전체 매장으로 전파되는 로직을 트리거를 통해 실시간 동기화합니다.\n"
    "* **매출 발생 상품 삭제 제한 (`MGOODS_T02` 트리거)**: `MGOODSTB`에서 특정 상품을 강제 삭제(`BEFORE DELETE`)하기 전, 해당 매장의 월별 매출 실적 테이블(`SGOODMTB`)을 조회하여 매출이 1건이라도 발생한 적이 있는 상품은 시스템 무결성을 위해 삭제가 차단됩니다.\n"
    "* **POS 판매단가 변경 전송 로그 (`MGOODS_T01`, `MGOODS_T03` 트리거)**: 매장 상품이 신규 등록되거나 판매단가(`UPRICE`), 공급가(`USUPRICE`) 등이 변경(`AFTER INSERT/UPDATE`)될 때, 실시간으로 매장 포스(POS) 단말기 및 전송 서버로 단가 패키지를 전파하기 위한 로그(`MMSLOGTB` 등)를 기록합니다.\n"
    "* **실사/폐기 레시피 원자재 자동 분해 (`IMREAL_T01`, `IMDUSE_T01` 트리거)**: 실사 및 폐기 확정 시 대상 품목이 세트/레시피 완제품(`set_fg` = 1, 2, 3)인 경우, 상품 마스터의 레시피 정보(`recipe_cd`)와 레시피 구성정보(`TB_RECIPE`, `TB_RECIPE_GOODS`)를 추적하여 하위 원자재 자재 수량을 자동으로 계산 및 분해하고, 수불 이력(`IMTRLGTB`)과 현재고(`IMCRIOTB`)를 업데이트합니다.\n"
    "* **POS 매출 및 매입 검증 (`STRNDT_T01`, `OBSLPD_T01` 트리거)**: 포스 판매 상세(`STRNDTTB`) 또는 자재 매입입고 상세(`OBSLPDTB`)가 추가/수정될 때, 상품 마스터의 과세 여부(`tax_fg`), 판매 유형, 입수량(`in_qty`)을 참조하여 세금 계산 및 재고 환산 작업을 자동 제어합니다."
)

data["tables"]["mgoodstb"] = {
    "memo": mgoodstb_memo,
    "starred": True,
    "color": "none",
    "columns": {
        "ms_no": "매장코드 (점포 코드)",
        "goods_cd": "상품코드 (자재 코드)",
        "goods_nm": "상품 한글 명칭",
        "goods_sub_nm": "상품 영문 및 보조 명칭",
        "goods_spec": "상품 규격",
        "lclass_cd": "대분류 코드",
        "mclass_cd": "중분류 코드",
        "sclass_cd": "소분류 코드",
        "uprice": "매장 판매가 (소비자가격)",
        "usuprice": "매장 공급가액",
        "ucost": "표준 매입원가",
        "vat_rate": "부가세율 (%)",
        "tax_fg": "과세 구분 (0: 면세, 1: 과세)",
        "goods_price_fg": "금액구분 (0: 일반PLU, 1: NON-PLU, 2: 오픈단가, 3: 포인트 등)",
        "goods_control_fg": "재고 통제 여부 (0: 미통제, 1: 통제)",
        "use_fg": "사용 제한 구분 (0: 일반사용, 1: 판매전용, 2: 매입전용)",
        "set_fg": "세트 상품 구분 (0: 일반단품, 1: 레시피 완제품, 2: 레시피 원자재, 3: 세트구성품)",
        "service_fg": "부가 메뉴 구분 (0: 일반상품, 1: 부가서비스 메뉴)",
        "ord_unit": "발주 단위 코드",
        "in_qty": "매입 포장 입수량 (예: 1박스당 낱개 개수)",
        "inv_unit": "재고 단위 코드",
        "inv_in_qty": "재고 입수량",
        "goods_unit": "상품 기본 단위 수량",
        "min_ord_qty": "최소 발주 제한 수량",
        "goods_point": "상품 적립 포인트",
        "safety_qty": "안전 재고 수량",
        "goods_use_fg": "상품 취급 여부 (0: 정상 사용, 1: 사용 일시중지/단종)",
        "tip_fg": "봉사료 적용 구분 (0: 미적용, 1: 적용)",
        "tax_control_fg": "부가세 통제 구분",
        "source_fg": "소스 코드 사용 여부",
        "goods_type": "상품 유형",
        "calory": "상품 칼로리 정보",
        "defcust_cnt": "적정 보관 일수",
        "origin_no": "원산지 코드 (MGORGMTB 매핑)",
        "product_no": "제조사 코드 (MGPRDMTB 매핑)",
        "grade_no": "상품 등급 코드 (MGRADMTB 매핑)",
        "income_no": "수입원 코드 (MGINCMTB 매핑)",
        "multi_biz_cd": "복수 사업자 코드",
        "create_fg": "등록 구분 (0: 매장직등록, 1: 본사 전송)",
        "create_dtime": "최초 등록 일시",
        "create_id": "최초 등록자 ID",
        "last_dtime": "최종 수정 일시",
        "last_id": "최종 수정자 ID",
        "sub_group_cd": "부가메뉴 그룹 코드",
        "erp_goods_cd": "ERP 연동용 상품코드",
        "goods_brand_cd": "패션/의류 브랜드 코드",
        "goods_style_cd": "의류 스타일 코드",
        "goods_color_cd": "의류 컬러 코드",
        "goods_siz_cd": "의류 사이즈 코드",
        "recipe_cd": "기준 레시피 코드",
        "fictitious_yn": "가상/의제매입세 적용 여부 (Y/N)",
        "supply_yn": "납품 취급 여부 (Y/N)",
        "usuprice_vat": "공급가액 부가세",
        "set_cd": "세트 관계 코드",
        "purch_rate": "매입 수수료율",
        "delivery_type": "배송 유형 (0: 직송, 1: 센터배송)",
        "image_idx": "상품 이미지 코드 (IMGMSTTB 매핑)",
        "product_standard": "상품 표준 규격명",
        "size_gbn_cd": "사이즈 구분 코드",
        "good_size_cd": "상품 사이즈 코드",
        "menu_grp_cd": "식음료 메뉴 그룹 코드",
        "sale_type_cd": "판매 유형 코드",
        "fictitious_tax": "의제매입세율 정보",
        "store_stock_yn": "본사 직재고 관리 대상 여부",
        "store_stock_ucost": "본사 직재고 원가",
        "goods_dc_fg": "할인 적용 가능 여부 (0: 가능, 1: 불가)",
        "ucost_rate": "원가율",
        "goods_short_name": "상품 단축명 (영수증 출력용)",
        "join_vendor": "주거래처 코드 (MVENDRTB 매핑)",
        "dept_cd": "소속 부서 코드"
    },
    "memo_c": "본사에서 신규 상품 출시 및 가맹점 배포 시 동기화 절차에 의해 점포별로 삽입됩니다.",
    "memo_u": "매장 개별 단가 변경이나 상품 취급 상태(goods_use_fg) 변경 시 수정 처리되며, Tr_MGOODS_T01 트리거를 통해 이력이 로깅됩니다.",
    "memo_d": "데이터 참조 무결성을 위해 실질 삭제 대신 delete_yn 또는 goods_use_fg = '1'(중지)로 비활성화 처리를 권장합니다.",
    "memo_r": "POS 매출 결제, 물류 발주, 매입 등록, 재고 실사 등 HMS 백오피스 내 모든 핵심 데이터 조회 시 조인의 중추 역할을 수행합니다.",
    "related_tables": [
        {
            "table_name": "tgoodstb",
            "description": "본사 상품 마스터 테이블. [트리거 TGOODS_T01 연동] 본사 마스터에서 상품 추가/변경 시 가맹점 상품 마스터로 변경 사항을 1:N 실시간 강제 전파 및 동기화합니다."
        },
        {
            "table_name": "imcriotb",
            "description": "매장 현재고 정보 테이블. [트리거 IMREAL_T01 / IMDUSE_T01 연동] 완제품 실사나 폐기 시 마스터의 레시피 정보에 따라 원자재 단위로 분해하여 개별 자재의 실재고 수량을 실시간 갱신합니다."
        },
        {
            "table_name": "tpricetb",
            "description": "상품 단가 마스터 테이블. 매장별 상품의 기간별/단가구분별 공급가 및 판매가 이력을 관리하며 마스터 상의 표준 단가 변경 시 참조됩니다."
        },
        {
            "table_name": "strndttb",
            "description": "매출 상세 테이블. [트리거 STRNDT_T01 연동] 포스(POS) 매출 상세 등록 시 상품 마스터의 과세유형(tax_fg), 세트 구분(set_fg) 정보를 기준으로 매출 유효성을 검증하고 원장 정산을 처리합니다."
        },
        {
            "table_name": "obslpdtb",
            "description": "매입/발주 상세 테이블. [트리거 OBSLPD_T01 연동] 입고 상세 추가 시 상품 마스터의 입수량 규격 및 매입 원가 단가 정보를 대조하여 원장 및 매입 잔액을 처리합니다."
        },
        {
            "table_name": "stckhitb",
            "description": "선입선출 입고대장 테이블. 상품별 입출고에 따른 재고 정산 시 상품 마스터에 기재된 과세 유형 및 매입원가를 참조하여 재고 금액을 평가합니다."
        },
        {
            "table_name": "imtrlgtb",
            "description": "재고 수불 로그 테이블. [트리거 IMREAL_T01 / IMDUSE_T01 연동] 실사/폐기 확정 시 레시피 매핑 분해된 개별 하위 자재들에 대한 수불 거래 상세 레코드를 기록합니다."
        },
        {
            "table_name": "imretptb",
            "description": "임시 실사/조정 테이블. 실사 임시 입력 시 매장 상품 마스터에서 해당 상품이 정상 사용 상태(goods_use_fg = '0') 인지 확인하기 위해 조인 대조합니다."
        },
        {
            "table_name": "weascdtb",
            "description": "POS 및 ERP 환경설정 테이블. 매장별 분류 규격 및 과세 기준 파라미터 매치에 참조됩니다."
        },
        {
            "table_name": "imgmsttb",
            "description": "상품 이미지 마스터 테이블. 포스 터치키 및 백오피스 상품 등록 화면에 표시할 사진 정보(IMAGE_IDX)를 매핑합니다."
        },
        {
            "table_name": "mmembstb",
            "description": "가맹점 마스터 테이블. 가맹점별 상품 취급 유효성을 매칭 검증하기 위해 조인됩니다."
        },
        {
            "table_name": "mnamemtb",
            "description": "공통 명칭 코드 마스터 테이블. 세트 구분, 발주 단위, 재고 단위 등의 상태 코드를 한글 명칭으로 변환하기 위해 조인됩니다."
        },
        {
            "table_name": "muserstb",
            "description": "시스템 사용자 마스터 테이블. 상품 신규 등록 및 수정자의 ID 감사 추적을 위해 조인됩니다."
        },
        {
            "table_name": "sgoodmtb",
            "description": "월별 매장 상품 실적 테이블. [트리거 MGOODS_T02 연동] 상품 마스터에서 삭제(BEFORE DELETE)를 실행할 때, 해당 상품의 월별 매출 실적이 존재하는 경우 삭제를 강제 제한하기 위해 조인 검증합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "가맹점 실시간 전송 로그 테이블. [트리거 MGOODS_T01 / T03 연동] 매장 상품의 단가나 속성 변경 시, POS 기기 및 연동 장비로 실시간 전송할 데이터 로그 패키지를 삽입 보관합니다."
        },
        {
            "table_name": "tb_recipe",
            "description": "기준 레시피 마스터 테이블. [트리거 IMREAL_T01 / IMDUSE_T01 연동] 상품 마스터(recipe_cd)에 지정된 완제품의 표준 조리법 레시피 정보를 조회하기 위해 조인됩니다."
        },
        {
            "table_name": "tb_recipe_goods",
            "description": "레시피 품목 상세 테이블. [트리거 IMREAL_T01 / IMDUSE_T01 연동] 실사/폐기 완제품 분해 시, 소요 중량(weight)에 따라 원자재 차감량을 정밀 환산하기 위해 조인됩니다."
        },
        {
            "table_name": "tb_set_goods",
            "description": "세트 상품 구성 정보 테이블. 상품 마스터(set_cd)와 매핑되어 세트 매출 발생 시 하위 품목을 분해하고 개별 수불 차감을 관리하기 위해 사용됩니다."
        }
    ]
}

with open(memos_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Updated table_memos.json with comprehensive mgoodstb triggers and 18 related tables!")
