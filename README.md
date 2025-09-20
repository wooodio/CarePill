# CarePill - 스마트 약품 관리 시스템

라즈베리파이 기반의 AI 약품 관리 시스템으로, OCR, 객체 인식, 음성 인터페이스, DUR 점검 기능을 통합한 스마트 약국 솔루션입니다.

## 🚀 주요 기능

### 1. 음성 인터페이스
- OpenAI API 기반 한국어 음성 인식 및 합성
- 자연스러운 대화를 통한 약품 조회 및 관리
- 기존 VoiceChatGPT 시스템 확장

### 2. OCR 텍스트 추출
- 처방전 자동 인식 및 텍스트 추출
- Tesseract 기반 한국어/영어 OCR
- 약품명, 용법, 용량 자동 파싱

### 3. YOLO 객체 인식
- 약품 포장/알약 자동 인식
- 실시간 카메라 모니터링
- 약품 분류 및 카운팅

### 4. DUR 점검 시스템
- 식약처 DUR 데이터 기반 상호작용 점검
- 실시간 약물 상호작용 경고
- 금기사항 및 주의사항 알림

### 5. 재고 관리
- 실시간 재고 현황 추적
- 유효기간 관리 및 알림
- 자동 발주 시스템

## 📋 시스템 요구사항

### 하드웨어
- **라즈베리파이 4B 이상** (4GB RAM 권장)
- **카메라 모듈** (OCR 및 객체 인식)
- **USB 마이크 및 스피커** (음성 인터페이스)
- **32GB+ microSD 카드** (Class 10 이상)

### 소프트웨어
- **OS**: Raspberry Pi OS (Debian 기반)
- **Python**: 3.8+
- **데이터베이스**: SQLite (개발) / MySQL (프로덕션)

## 🛠️ 설치 및 설정

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/carepill.git
cd carepill
```

### 2. Python 환경 설정
```bash
# 가상환경 생성 (권장)
python -m venv carepill_env
source carepill_env/bin/activate  # Linux/Mac
# 또는
carepill_env\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 3. 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집하여 API 키 설정
# OPENAI_API_KEY=your_openai_api_key_here
```

### 4. 데이터베이스 초기화
```bash
# SQLite 사용시 (개발환경)
python -c "from database import init_database; init_database()"

# 또는 메인 애플리케이션 실행시 자동 초기화
python main.py
```

## 🚀 사용법

### 기본 실행
```bash
python main.py
```

### 대화형 명령어
시스템 실행 후 사용 가능한 명령어:
- `voice` - 음성 인터페이스 시작
- `status` - 시스템 상태 확인
- `db` - 데이터베이스 상태 확인
- `exit` - 시스템 종료

### 음성 인터페이스 사용
```
CarePill> voice
```
음성 명령 예시:
- "타이레놀 재고 확인해줘"
- "신규 처방전 등록"
- "유효기간 임박 약품 알려줘"
- "DUR 점검 실행"

## 📁 프로젝트 구조

```
carepill/
├── main.py                 # 메인 애플리케이션
├── voice_chat.py          # 기존 음성 채팅 시스템
├── config/                # 설정 관리
│   ├── __init__.py
│   └── settings.py
├── database/              # 데이터베이스 모델 및 관리
│   ├── __init__.py
│   ├── models.py          # SQLAlchemy 모델
│   ├── database.py        # DB 연결 관리
│   └── migrations/        # 마이그레이션 스크립트
├── modules/               # 기능별 모듈 (추후 구현)
│   ├── ocr/              # OCR 처리
│   ├── yolo/             # 객체 인식
│   ├── dur/              # DUR 점검
│   ├── inventory/        # 재고 관리
│   └── api/              # API 서버
├── utils/                 # 유틸리티
│   ├── __init__.py
│   └── logger.py          # 로깅 시스템
├── tests/                 # 테스트 (추후 구현)
├── uploads/               # 업로드 파일
├── temp/                  # 임시 파일
├── logs/                  # 로그 파일
├── models/                # AI 모델
├── requirements.txt       # Python 의존성
├── .env.example          # 환경 변수 예시
└── README.md             # 이 파일
```

## 🗄️ 데이터베이스 스키마

### 주요 테이블
- **medications**: 약품 기본 정보
- **inventory_items**: 재고 관리
- **patients**: 환자 정보
- **prescriptions**: 처방전
- **prescription_items**: 처방전 상세
- **dispensing_records**: 조제 기록
- **dur_interactions**: DUR 상호작용 데이터
- **ocr_results**: OCR 처리 결과
- **yolo_detections**: 객체 인식 결과

## 🔧 설정

### 환경 변수
주요 환경 변수는 `.env` 파일에서 설정:

```env
# OpenAI API
OPENAI_API_KEY=your_api_key

# 데이터베이스
DB_TYPE=sqlite
SQLITE_DB_PATH=carepill.db

# 기능 활성화
CAMERA_ENABLED=true
AUDIO_ENABLED=true
GPIO_ENABLED=true

# 로깅
LOG_LEVEL=INFO
DEBUG=true
```

### 하드웨어 설정 (라즈베리파이)
```bash
# 카메라 활성화
sudo raspi-config
# -> Interface Options -> Camera -> Enable

# 오디오 설정
sudo apt-get install alsa-utils
alsamixer
```

## 🧪 개발 및 테스트

### 개발 환경 설정
```bash
# 개발 의존성 설치
pip install -r requirements.txt

# 테스트 실행 (추후 구현)
pytest tests/

# 코드 품질 검사
black .
flake8 .
mypy .
```

### 디버깅
```bash
# 디버그 모드로 실행
DEBUG=true python main.py

# 로그 레벨 설정
LOG_LEVEL=DEBUG python main.py
```

## 📖 API 문서

REST API 서버는 추후 Django/FastAPI로 구현 예정:
- `/api/medications/` - 약품 관리
- `/api/inventory/` - 재고 관리
- `/api/prescriptions/` - 처방전 관리
- `/api/ocr/` - OCR 처리
- `/api/yolo/` - 객체 인식

## 🔄 업데이트 로드맵

### Phase 1 - 기반 시스템 (현재)
- [x] 프로젝트 구조 설정
- [x] 데이터베이스 스키마 설계
- [x] 기본 설정 시스템
- [ ] OCR 모듈 구현
- [ ] YOLO 모듈 구현

### Phase 2 - 핵심 기능
- [ ] DUR 점검 엔진
- [ ] 음성 인터페이스 통합
- [ ] 재고 관리 시스템
- [ ] 하드웨어 제어 API

### Phase 3 - 웹/모바일
- [ ] Django 웹 서버
- [ ] 모바일 앱 연동
- [ ] 클라우드 동기화
- [ ] 알림 시스템

### Phase 4 - 고도화
- [ ] 통합 테스트
- [ ] 접근성 최적화
- [ ] 성능 개선
- [ ] 보안 강화

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🆘 지원

- 이슈 리포트: [GitHub Issues](https://github.com/your-username/carepill/issues)
- 문서: [Wiki](https://github.com/your-username/carepill/wiki)
- 이메일: support@carepill.com

---

**CarePill** - Making medication management smarter and safer 💊🤖