#!/usr/bin/env python3
"""
CarePill 데이터베이스 초기화 스크립트
데이터베이스 테이블 생성 및 기본 데이터 설정
"""

import os
import sys
import logging
from datetime import datetime, date
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.database import init_database, DatabaseManager
from database.models import *

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_data(db_manager: DatabaseManager):
    """샘플 데이터 생성"""
    logger.info("샘플 데이터 생성 시작...")

    with db_manager.session_scope() as session:
        # 샘플 약품 데이터
        sample_medications = [
            Medication(
                name="타이레놀정 500mg",
                generic_name="아세트아미노펜",
                manufacturer="한국얀센",
                kfda_code="199800123",
                dosage_form="정제",
                strength="500mg",
                unit="정",
                storage_condition="실온보관",
                shelf_life_months=36,
                prescription_required=False,
                controlled_substance=False
            ),
            Medication(
                name="낙센정 275mg",
                generic_name="나프록센나트륨",
                manufacturer="한국로슈",
                kfda_code="199800456",
                dosage_form="정제",
                strength="275mg",
                unit="정",
                storage_condition="실온보관",
                shelf_life_months=36,
                prescription_required=True,
                controlled_substance=False
            ),
            Medication(
                name="오메프라졸캡슐 20mg",
                generic_name="오메프라졸",
                manufacturer="한국파마",
                kfda_code="199800789",
                dosage_form="캡슐",
                strength="20mg",
                unit="캡슐",
                storage_condition="실온보관",
                shelf_life_months=24,
                prescription_required=True,
                controlled_substance=False
            )
        ]

        for medication in sample_medications:
            session.add(medication)

        session.flush()  # ID 생성을 위해 flush

        # 샘플 환자 데이터
        sample_patient = Patient(
            name="김철수",
            birth_date=date(1980, 5, 15),
            gender="남성",
            phone="010-1234-5678",
            allergies="페니실린 알레르기",
            medical_conditions="고혈압, 당뇨병",
            notes="정기적인 혈압 체크 필요"
        )
        session.add(sample_patient)
        session.flush()

        # 샘플 재고 데이터
        sample_inventory = [
            InventoryItem(
                medication_id=sample_medications[0].id,
                batch_number="B001-2024",
                expiry_date=date(2025, 12, 31),
                quantity=100,
                initial_quantity=100,
                purchase_date=date(2024, 1, 15),
                purchase_price=15000.00,
                supplier="약품유통㈜",
                storage_location="약품보관함-A"
            ),
            InventoryItem(
                medication_id=sample_medications[1].id,
                batch_number="B002-2024",
                expiry_date=date(2025, 6, 30),
                quantity=50,
                initial_quantity=50,
                purchase_date=date(2024, 2, 10),
                purchase_price=25000.00,
                supplier="메디컬파마㈜",
                storage_location="약품보관함-B"
            )
        ]

        for inventory in sample_inventory:
            session.add(inventory)

        # 샘플 DUR 상호작용 데이터
        sample_interactions = [
            DURInteraction(
                medication_id=sample_medications[0].id,
                interaction_type="drug-drug",
                severity_level="medium",
                interacting_medication="와파린",
                description="아세트아미노펜과 와파린의 병용시 출혈 위험 증가",
                clinical_effect="INR 상승, 출혈 시간 연장",
                management="정기적인 INR 모니터링 필요",
                source="KFDA",
                source_date=date(2024, 1, 1)
            ),
            DURInteraction(
                medication_id=sample_medications[1].id,
                interaction_type="drug-drug",
                severity_level="high",
                interacting_medication="리튬",
                description="나프록센과 리튬의 병용시 리튬 독성 위험",
                clinical_effect="리튬 혈중농도 상승",
                management="리튬 혈중농도 모니터링 및 용량 조정",
                source="KFDA",
                source_date=date(2024, 1, 1)
            )
        ]

        for interaction in sample_interactions:
            session.add(interaction)

        # 시스템 설정 데이터
        sample_configs = [
            Configuration(
                key="system.timezone",
                value="Asia/Seoul",
                data_type="string",
                category="system",
                description="시스템 기본 시간대"
            ),
            Configuration(
                key="ocr.confidence_threshold",
                value="0.85",
                data_type="float",
                category="ocr",
                description="OCR 신뢰도 임계값"
            ),
            Configuration(
                key="yolo.model_path",
                value="/models/yolo_medication.pt",
                data_type="string",
                category="yolo",
                description="YOLO 모델 파일 경로"
            ),
            Configuration(
                key="notification.enabled",
                value="true",
                data_type="boolean",
                category="notification",
                description="알림 기능 활성화 여부"
            )
        ]

        for config in sample_configs:
            session.add(config)

        logger.info("샘플 데이터 생성 완료")


def main():
    """메인 실행 함수"""
    try:
        # 환경 변수 설정 (개발 환경)
        os.environ.setdefault('DB_TYPE', 'sqlite')
        os.environ.setdefault('SQLITE_DB_PATH', 'carepill.db')
        os.environ.setdefault('DB_ECHO', 'false')

        logger.info("데이터베이스 초기화 시작...")

        # 데이터베이스 초기화
        db_manager = init_database()

        # 연결 테스트
        if not db_manager.test_connection():
            raise Exception("데이터베이스 연결 실패")

        logger.info("데이터베이스 연결 성공")

        # 테이블 생성
        db_manager.create_tables()
        logger.info("데이터베이스 테이블 생성 완료")

        # 샘플 데이터 생성 (자동 생성)
        create_sample_data(db_manager)

        logger.info("데이터베이스 초기화 완료!")

        # 데이터베이스 정보 출력
        print("\n" + "="*50)
        print("CarePill 데이터베이스 초기화 완료")
        print("="*50)
        print(f"데이터베이스 URL: {db_manager.database_url}")
        print(f"초기화 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)

    except Exception as e:
        logger.error(f"데이터베이스 초기화 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()