"""
CarePill 약품 관리 시스템 데이터베이스 모델
SQLAlchemy를 사용한 데이터베이스 스키마 정의
"""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Boolean, Float, ForeignKey, JSON, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column

Base = declarative_base()


class Medication(Base):
    """약품 기본 정보"""
    __tablename__ = 'medications'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 기본 정보
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="약품명")
    generic_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="일반명")
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="제조사")

    # 식약처 코드
    kfda_code: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True, comment="식약처 허가번호")
    drug_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="약품코드")

    # 약품 형태 및 용법
    dosage_form: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="제형 (정제, 캡슐, 주사 등)")
    strength: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="함량")
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="단위")

    # 보관 및 유효기간
    storage_condition: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="보관조건")
    shelf_life_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="유효기간(개월)")

    # 처방 정보
    prescription_required: Mapped[bool] = mapped_column(Boolean, default=True, comment="처방전 필요 여부")
    controlled_substance: Mapped[bool] = mapped_column(Boolean, default=False, comment="향정신성 의약품 여부")

    # 시스템 필드
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # 관계
    inventory_items: Mapped[List["InventoryItem"]] = relationship("InventoryItem", back_populates="medication")
    prescriptions: Mapped[List["PrescriptionItem"]] = relationship("PrescriptionItem", back_populates="medication")
    dur_interactions: Mapped[List["DURInteraction"]] = relationship("DURInteraction", foreign_keys="[DURInteraction.medication_id]", back_populates="medication")


class InventoryItem(Base):
    """재고 관리"""
    __tablename__ = 'inventory_items'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    medication_id: Mapped[int] = mapped_column(Integer, ForeignKey('medications.id'), nullable=False)

    # 재고 정보
    batch_number: Mapped[str] = mapped_column(String(50), nullable=False, comment="배치번호/로트번호")
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False, comment="유효기간")
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="현재 수량")
    initial_quantity: Mapped[int] = mapped_column(Integer, nullable=False, comment="초기 입고 수량")

    # 입고 정보
    purchase_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, comment="구입일")
    purchase_price: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True, comment="구입가격")
    supplier: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="공급업체")

    # 보관 위치
    storage_location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="보관 위치")
    storage_temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="보관 온도")

    # 시스템 필드
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # 관계
    medication: Mapped["Medication"] = relationship("Medication", back_populates="inventory_items")
    dispensing_records: Mapped[List["DispensingRecord"]] = relationship("DispensingRecord", back_populates="inventory_item")


class Patient(Base):
    """환자 정보"""
    __tablename__ = 'patients'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 개인 정보
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="환자명")
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, comment="생년월일")
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, comment="성별")
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="전화번호")

    # 의료 정보
    allergies: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="알레르기 정보")
    medical_conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="기존 질환")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="특이사항")

    # 시스템 필드
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # 관계
    prescriptions: Mapped[List["Prescription"]] = relationship("Prescription", back_populates="patient")


class Prescription(Base):
    """처방전"""
    __tablename__ = 'prescriptions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey('patients.id'), nullable=False)

    # 처방 정보
    prescription_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="처방전 번호")
    doctor_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="의사명")
    hospital_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="병원명")
    prescribed_date: Mapped[date] = mapped_column(Date, nullable=False, comment="처방일")

    # 상태
    status: Mapped[str] = mapped_column(String(20), default='pending', comment="상태 (pending, dispensed, cancelled)")
    total_amount: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True, comment="총 금액")

    # 시스템 필드
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    patient: Mapped["Patient"] = relationship("Patient", back_populates="prescriptions")
    prescription_items: Mapped[List["PrescriptionItem"]] = relationship("PrescriptionItem", back_populates="prescription", cascade="all, delete-orphan")


class PrescriptionItem(Base):
    """처방전 항목"""
    __tablename__ = 'prescription_items'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prescription_id: Mapped[int] = mapped_column(Integer, ForeignKey('prescriptions.id'), nullable=False)
    medication_id: Mapped[int] = mapped_column(Integer, ForeignKey('medications.id'), nullable=False)

    # 처방 상세
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, comment="처방 수량")
    dosage: Mapped[str] = mapped_column(String(100), nullable=False, comment="용법")
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False, comment="복용 기간(일)")

    # 조제 정보
    dispensed_quantity: Mapped[int] = mapped_column(Integer, default=0, comment="조제된 수량")
    dispensed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, comment="조제일")

    # 관계
    prescription: Mapped["Prescription"] = relationship("Prescription", back_populates="prescription_items")
    medication: Mapped["Medication"] = relationship("Medication", back_populates="prescriptions")
    dispensing_records: Mapped[List["DispensingRecord"]] = relationship("DispensingRecord", back_populates="prescription_item")


class DispensingRecord(Base):
    """조제 기록"""
    __tablename__ = 'dispensing_records'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prescription_item_id: Mapped[int] = mapped_column(Integer, ForeignKey('prescription_items.id'), nullable=False)
    inventory_item_id: Mapped[int] = mapped_column(Integer, ForeignKey('inventory_items.id'), nullable=False)

    # 조제 정보
    quantity_dispensed: Mapped[int] = mapped_column(Integer, nullable=False, comment="조제 수량")
    dispensed_by: Mapped[str] = mapped_column(String(100), nullable=False, comment="조제자")
    dispensed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, comment="조제 시간")

    # 관계
    prescription_item: Mapped["PrescriptionItem"] = relationship("PrescriptionItem", back_populates="dispensing_records")
    inventory_item: Mapped["InventoryItem"] = relationship("InventoryItem", back_populates="dispensing_records")


class DURInteraction(Base):
    """DUR (Drug Utilization Review) 상호작용 데이터"""
    __tablename__ = 'dur_interactions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    medication_id: Mapped[int] = mapped_column(Integer, ForeignKey('medications.id'), nullable=False)

    # 상호작용 정보
    interaction_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="상호작용 유형")
    severity_level: Mapped[str] = mapped_column(String(20), nullable=False, comment="심각도 (high, medium, low)")
    interacting_medication: Mapped[str] = mapped_column(String(200), nullable=False, comment="상호작용 약품")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="상호작용 설명")
    clinical_effect: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="임상적 영향")
    management: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="관리 방안")

    # 데이터 출처
    source: Mapped[str] = mapped_column(String(100), nullable=False, comment="데이터 출처 (KFDA, etc.)")
    source_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, comment="데이터 수집일")

    # 시스템 필드
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # 관계
    medication: Mapped["Medication"] = relationship("Medication", back_populates="dur_interactions")


class OCRResult(Base):
    """OCR 처리 결과"""
    __tablename__ = 'ocr_results'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 이미지 정보
    image_path: Mapped[str] = mapped_column(String(500), nullable=False, comment="이미지 파일 경로")
    image_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="이미지 해시")

    # OCR 결과
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False, comment="추출된 텍스트")
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="신뢰도 점수")
    processing_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="처리 시간(초)")

    # 인식된 정보
    recognized_medications: Mapped[Optional[str]] = mapped_column(JSON, nullable=True, comment="인식된 약품 정보")
    prescription_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True, comment="처방전 데이터")

    # 처리 상태
    status: Mapped[str] = mapped_column(String(20), default='pending', comment="처리 상태")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="오류 메시지")

    # 시스템 필드
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class YOLODetection(Base):
    """YOLO 객체 인식 결과"""
    __tablename__ = 'yolo_detections'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 이미지 정보
    image_path: Mapped[str] = mapped_column(String(500), nullable=False, comment="이미지 파일 경로")
    image_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="이미지 해시")

    # 검출 결과
    detected_objects: Mapped[str] = mapped_column(JSON, nullable=False, comment="검출된 객체 정보")
    confidence_scores: Mapped[str] = mapped_column(JSON, nullable=False, comment="신뢰도 점수들")
    bounding_boxes: Mapped[str] = mapped_column(JSON, nullable=False, comment="바운딩 박스 좌표")

    # 처리 정보
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, comment="사용된 모델 버전")
    processing_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="처리 시간(초)")

    # 시스템 필드
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SystemLog(Base):
    """시스템 로그"""
    __tablename__ = 'system_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 로그 정보
    level: Mapped[str] = mapped_column(String(20), nullable=False, comment="로그 레벨")
    module: Mapped[str] = mapped_column(String(100), nullable=False, comment="모듈명")
    message: Mapped[str] = mapped_column(Text, nullable=False, comment="로그 메시지")
    details: Mapped[Optional[str]] = mapped_column(JSON, nullable=True, comment="상세 정보")

    # 사용자 정보
    user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="사용자 ID")
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True, comment="IP 주소")

    # 시스템 필드
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Configuration(Base):
    """시스템 설정"""
    __tablename__ = 'configurations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 설정 정보
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="설정 키")
    value: Mapped[str] = mapped_column(Text, nullable=False, comment="설정 값")
    data_type: Mapped[str] = mapped_column(String(20), default='string', comment="데이터 타입")
    category: Mapped[str] = mapped_column(String(50), nullable=False, comment="설정 카테고리")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="설정 설명")

    # 시스템 필드
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)