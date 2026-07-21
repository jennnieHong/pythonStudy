import re

filepath = r"D:\hmTest\backoffice\QaReport\update_memos_json.py"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace occurrences of weascdtb with incorrect descriptions.
# For tsm_tran_mst
content = content.replace(
    '"description": "POS 및 ERP 환경설정 테이블. 영수증 번호 생성 규칙 및 영수증 출력을 위한 봉사료(Msce)와 부가세(Vat) 과세 연산 상수를 매칭 참조합니다."',
    '"description": "외상매출 카드 승인 거래 내역 테이블. POS에서 승인된 신용카드/결제 수단 거래 건별 카드사, 승인번호 및 금액 정보의 정합성을 대조하기 위해 조인 참조됩니다."'
)

# For tsm_tran_mst_bk
content = content.replace(
    '"description": "POS 및 ERP 환경설정 테이블. 데이터 이관/백업 처리 시 적용되는 과거 거래 데이터 보존 연한 설정값을 매칭 참조합니다."',
    '"description": "외상매출 카드 승인 거래 내역 테이블. 이관된 과거 카드 승인 거래 데이터와의 교차 대사를 위해 조인 참조됩니다."'
)

# For tsubmntb
content = content.replace(
    '"description": "POS 및 ERP 환경설정 테이블. POS 화면 구성 및 서브메뉴 옵션 한계 개수(최대 동시 선택 옵션 수 등) 제어 상수를 매칭 참조합니다."',
    '"description": "외상매출 카드 승인 거래 내역 테이블. 서브메뉴(옵션) 추가에 따른 카드 승인 금액 변동 정합성을 검증하기 위해 조인 참조됩니다."'
)

# For ttaxmstb
content = content.replace(
    '"description": "POS 및 ERP 환경설정 테이블. 면세 환급 최소 거래 금액 한도(예: 30,000원 이상 등) 및 영수증 하단 사후면세 안내 문구 출력 파라미터를 매칭 참조합니다."',
    '"description": "외상매출 카드 승인 거래 내역 테이블. 사후 면세 환급 대상 카드 매출 승인 내역의 카드 번호 및 승인 금액을 검증하기 위해 조인 참조됩니다."'
)

# For tvndrgtb
content = content.replace(
    '"description": "POS 및 ERP 환경설정 테이블. 발주 및 입고 시 적용되는 최소 발주 단위 수량 제어 정책 및 입고 마스킹 처리 설정을 매칭 참조합니다."',
    '"description": "외상매출 카드 승인 거래 내역 테이블. 협력업체 공급 물품 거래 대금 중 카드 결제 처리 건의 정합성을 감사하기 위해 조인 참조됩니다."'
)

# For tvndrmtb
content = content.replace(
    '"description": "POS 및 ERP 환경설정 테이블. 본사 매입 채무 정산 시 사용되는 금융기관 은행 코드(BANK_CD) 및 세무 전자세금계산서 연동 파라미터를 매칭 참조합니다."',
    '"description": "외상매출 카드 승인 거래 내역 테이블. 협력업체 정산 대금 중 신용카드 결제 및 매입 청구 거래 내역을 매칭하기 위해 조인 참조됩니다."'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Replacement complete!")
