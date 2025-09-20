-- CarePill 데이터베이스 초기 스키마
-- 약품 관리 시스템을 위한 기본 테이블 생성

-- 약품 기본 정보 테이블
CREATE TABLE IF NOT EXISTS medications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    generic_name VARCHAR(200),
    manufacturer VARCHAR(100),
    kfda_code VARCHAR(50) UNIQUE,
    drug_code VARCHAR(50),
    dosage_form VARCHAR(50),
    strength VARCHAR(100),
    unit VARCHAR(20),
    storage_condition VARCHAR(200),
    shelf_life_months INTEGER,
    prescription_required BOOLEAN DEFAULT 1,
    controlled_substance BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- 재고 관리 테이블
CREATE TABLE IF NOT EXISTS inventory_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medication_id INTEGER NOT NULL,
    batch_number VARCHAR(50) NOT NULL,
    expiry_date DATE NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    initial_quantity INTEGER NOT NULL,
    purchase_date DATE,
    purchase_price DECIMAL(10,2),
    supplier VARCHAR(100),
    storage_location VARCHAR(100),
    storage_temperature REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (medication_id) REFERENCES medications(id)
);

-- 환자 정보 테이블
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    birth_date DATE,
    gender VARCHAR(10),
    phone VARCHAR(20),
    allergies TEXT,
    medical_conditions TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- 처방전 테이블
CREATE TABLE IF NOT EXISTS prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    prescription_number VARCHAR(50) UNIQUE NOT NULL,
    doctor_name VARCHAR(100) NOT NULL,
    hospital_name VARCHAR(100) NOT NULL,
    prescribed_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    total_amount DECIMAL(10,2),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

-- 처방전 항목 테이블
CREATE TABLE IF NOT EXISTS prescription_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_id INTEGER NOT NULL,
    medication_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    duration_days INTEGER NOT NULL,
    dispensed_quantity INTEGER DEFAULT 0,
    dispensed_date DATE,
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(id),
    FOREIGN KEY (medication_id) REFERENCES medications(id)
);

-- 조제 기록 테이블
CREATE TABLE IF NOT EXISTS dispensing_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_item_id INTEGER NOT NULL,
    inventory_item_id INTEGER NOT NULL,
    quantity_dispensed INTEGER NOT NULL,
    dispensed_by VARCHAR(100) NOT NULL,
    dispensed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prescription_item_id) REFERENCES prescription_items(id),
    FOREIGN KEY (inventory_item_id) REFERENCES inventory_items(id)
);

-- DUR 상호작용 데이터 테이블
CREATE TABLE IF NOT EXISTS dur_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medication_id INTEGER NOT NULL,
    interaction_type VARCHAR(50) NOT NULL,
    severity_level VARCHAR(20) NOT NULL,
    interacting_medication VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    clinical_effect TEXT,
    management TEXT,
    source VARCHAR(100) NOT NULL,
    source_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (medication_id) REFERENCES medications(id)
);

-- OCR 처리 결과 테이블
CREATE TABLE IF NOT EXISTS ocr_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_path VARCHAR(500) NOT NULL,
    image_hash VARCHAR(64),
    extracted_text TEXT NOT NULL,
    confidence_score REAL,
    processing_time REAL,
    recognized_medications TEXT,
    prescription_data TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME
);

-- YOLO 객체 인식 결과 테이블
CREATE TABLE IF NOT EXISTS yolo_detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_path VARCHAR(500) NOT NULL,
    image_hash VARCHAR(64),
    detected_objects TEXT NOT NULL,
    confidence_scores TEXT NOT NULL,
    bounding_boxes TEXT NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    processing_time REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 시스템 로그 테이블
CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level VARCHAR(20) NOT NULL,
    module VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    details TEXT,
    user_id VARCHAR(100),
    ip_address VARCHAR(45),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 시스템 설정 테이블
CREATE TABLE IF NOT EXISTS configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    data_type VARCHAR(20) DEFAULT 'string',
    category VARCHAR(50) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_medications_kfda_code ON medications(kfda_code);
CREATE INDEX IF NOT EXISTS idx_medications_name ON medications(name);
CREATE INDEX IF NOT EXISTS idx_inventory_expiry_date ON inventory_items(expiry_date);
CREATE INDEX IF NOT EXISTS idx_inventory_medication_id ON inventory_items(medication_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_patient_id ON prescriptions(patient_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_number ON prescriptions(prescription_number);
CREATE INDEX IF NOT EXISTS idx_prescription_items_prescription_id ON prescription_items(prescription_id);
CREATE INDEX IF NOT EXISTS idx_prescription_items_medication_id ON prescription_items(medication_id);
CREATE INDEX IF NOT EXISTS idx_dispensing_records_prescription_item_id ON dispensing_records(prescription_item_id);
CREATE INDEX IF NOT EXISTS idx_dur_interactions_medication_id ON dur_interactions(medication_id);
CREATE INDEX IF NOT EXISTS idx_ocr_results_status ON ocr_results(status);
CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_configurations_key ON configurations(key);

-- 트리거 생성 (updated_at 자동 업데이트)
CREATE TRIGGER IF NOT EXISTS update_medications_timestamp
    AFTER UPDATE ON medications
BEGIN
    UPDATE medications SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_inventory_items_timestamp
    AFTER UPDATE ON inventory_items
BEGIN
    UPDATE inventory_items SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_patients_timestamp
    AFTER UPDATE ON patients
BEGIN
    UPDATE patients SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_prescriptions_timestamp
    AFTER UPDATE ON prescriptions
BEGIN
    UPDATE prescriptions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_dur_interactions_timestamp
    AFTER UPDATE ON dur_interactions
BEGIN
    UPDATE dur_interactions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_configurations_timestamp
    AFTER UPDATE ON configurations
BEGIN
    UPDATE configurations SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;