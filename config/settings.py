"""
CarePill 시스템 설정
환경 변수와 기본 설정을 관리
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트 디렉토리
BASE_DIR = Path(__file__).resolve().parent.parent

# 기본 디렉토리 설정
UPLOAD_DIR = BASE_DIR / "uploads"
IMAGES_DIR = UPLOAD_DIR / "images"
TEMP_DIR = BASE_DIR / "temp"
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"

# 디렉토리 생성
for directory in [UPLOAD_DIR, IMAGES_DIR, TEMP_DIR, LOGS_DIR, MODELS_DIR]:
    directory.mkdir(exist_ok=True)


class Settings:
    """시스템 설정 클래스"""

    # 기본 설정
    DEBUG: bool = os.getenv('DEBUG', 'true').lower() == 'true'
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'carepill-default-secret-key')
    TIMEZONE: str = os.getenv('TIMEZONE', 'Asia/Seoul')

    # 데이터베이스 설정
    DB_TYPE: str = os.getenv('DB_TYPE', 'sqlite')
    SQLITE_DB_PATH: str = os.getenv('SQLITE_DB_PATH', str(BASE_DIR / 'carepill.db'))
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', '3306'))
    DB_USER: str = os.getenv('DB_USER', 'carepill_user')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    DB_NAME: str = os.getenv('DB_NAME', 'carepill')
    DB_ECHO: bool = os.getenv('DB_ECHO', 'false').lower() == 'true'

    # OpenAI API 설정
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    OPENAI_TTS_MODEL: str = os.getenv('OPENAI_TTS_MODEL', 'tts-1')
    OPENAI_TTS_VOICE: str = os.getenv('OPENAI_TTS_VOICE', 'alloy')
    OPENAI_LANGUAGE: str = os.getenv('OPENAI_LANGUAGE', 'ko')
    OPENAI_MAX_TOKENS: int = int(os.getenv('OPENAI_MAX_TOKENS', '2000'))
    OPENAI_TEMPERATURE: float = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))

    # OCR 설정
    TESSERACT_PATH: str = os.getenv('TESSERACT_PATH', '/usr/bin/tesseract')
    TESSERACT_DATA_PATH: str = os.getenv('TESSERACT_DATA_PATH', '/usr/share/tesseract-ocr/4.00/tessdata')
    OCR_LANGUAGES: str = os.getenv('OCR_LANGUAGES', 'kor+eng')
    OCR_CONFIDENCE_THRESHOLD: float = float(os.getenv('OCR_CONFIDENCE_THRESHOLD', '0.6'))

    # YOLO 설정
    YOLO_MODEL_PATH: str = os.getenv('YOLO_MODEL_PATH', str(MODELS_DIR / 'yolo' / 'best.pt'))
    YOLO_CONFIDENCE_THRESHOLD: float = float(os.getenv('YOLO_CONFIDENCE_THRESHOLD', '0.5'))
    YOLO_IOU_THRESHOLD: float = float(os.getenv('YOLO_IOU_THRESHOLD', '0.45'))
    YOLO_MAX_DETECTIONS: int = int(os.getenv('YOLO_MAX_DETECTIONS', '100'))

    # 파일 경로 설정
    UPLOAD_DIR: Path = UPLOAD_DIR
    IMAGES_DIR: Path = IMAGES_DIR
    TEMP_DIR: Path = TEMP_DIR
    LOGS_DIR: Path = LOGS_DIR
    MODELS_DIR: Path = MODELS_DIR

    # 파일 제한 설정
    MAX_UPLOAD_SIZE: int = int(os.getenv('MAX_UPLOAD_SIZE', '10485760'))  # 10MB
    ALLOWED_IMAGE_EXTENSIONS: set = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    ALLOWED_AUDIO_EXTENSIONS: set = {'.wav', '.mp3', '.m4a', '.flac'}

    # 로깅 설정
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', str(LOGS_DIR / 'carepill.log'))
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT: str = '%Y-%m-%d %H:%M:%S'

    # 하드웨어 설정 (라즈베리파이)
    CAMERA_ENABLED: bool = os.getenv('CAMERA_ENABLED', 'true').lower() == 'true'
    AUDIO_ENABLED: bool = os.getenv('AUDIO_ENABLED', 'true').lower() == 'true'
    GPIO_ENABLED: bool = os.getenv('GPIO_ENABLED', 'true').lower() == 'true'

    # 카메라 설정
    CAMERA_WIDTH: int = int(os.getenv('CAMERA_WIDTH', '1920'))
    CAMERA_HEIGHT: int = int(os.getenv('CAMERA_HEIGHT', '1080'))
    CAMERA_FPS: int = int(os.getenv('CAMERA_FPS', '30'))

    # 오디오 설정
    AUDIO_SAMPLE_RATE: int = int(os.getenv('AUDIO_SAMPLE_RATE', '44100'))
    AUDIO_CHANNELS: int = int(os.getenv('AUDIO_CHANNELS', '1'))
    AUDIO_CHUNK_SIZE: int = int(os.getenv('AUDIO_CHUNK_SIZE', '1024'))

    # DUR API 설정
    KFDA_API_KEY: str = os.getenv('KFDA_API_KEY', '')
    DRUG_INFO_API_URL: str = os.getenv('DRUG_INFO_API_URL', 'https://api.example.com/drug-info')
    DUR_UPDATE_INTERVAL: int = int(os.getenv('DUR_UPDATE_INTERVAL', '24'))  # 시간

    # 알림 설정
    ENABLE_NOTIFICATIONS: bool = os.getenv('ENABLE_NOTIFICATIONS', 'true').lower() == 'true'
    NOTIFICATION_EMAIL: str = os.getenv('NOTIFICATION_EMAIL', 'admin@carepill.com')

    # 세션 설정
    SESSION_TIMEOUT: int = int(os.getenv('SESSION_TIMEOUT', '3600'))  # 초
    MAX_SESSIONS: int = int(os.getenv('MAX_SESSIONS', '10'))

    # 성능 설정
    MAX_WORKERS: int = int(os.getenv('MAX_WORKERS', '4'))
    CACHE_TTL: int = int(os.getenv('CACHE_TTL', '300'))  # 초

    @classmethod
    def get_database_url(cls) -> str:
        """데이터베이스 연결 URL 반환"""
        if cls.DB_TYPE == 'sqlite':
            return f"sqlite:///{cls.SQLITE_DB_PATH}"
        elif cls.DB_TYPE == 'mysql':
            return f"mysql+mysqlconnector://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        else:
            raise ValueError(f"지원하지 않는 데이터베이스 타입: {cls.DB_TYPE}")

    @classmethod
    def get_logging_config(cls) -> Dict[str, Any]:
        """로깅 설정 딕셔너리 반환"""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': cls.LOG_FORMAT,
                    'datefmt': cls.LOG_DATE_FORMAT
                },
            },
            'handlers': {
                'default': {
                    'level': cls.LOG_LEVEL,
                    'formatter': 'standard',
                    'class': 'logging.StreamHandler',
                },
                'file': {
                    'level': cls.LOG_LEVEL,
                    'formatter': 'standard',
                    'class': 'logging.FileHandler',
                    'filename': cls.LOG_FILE,
                    'mode': 'a',
                },
            },
            'loggers': {
                '': {
                    'handlers': ['default', 'file'],
                    'level': cls.LOG_LEVEL,
                    'propagate': False
                }
            }
        }

    @classmethod
    def validate_settings(cls) -> bool:
        """설정 유효성 검사"""
        errors = []

        # OpenAI API 키 검사
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY가 설정되지 않았습니다.")

        # 데이터베이스 설정 검사
        if cls.DB_TYPE not in ['sqlite', 'mysql']:
            errors.append(f"지원하지 않는 데이터베이스 타입: {cls.DB_TYPE}")

        # 디렉토리 접근 권한 검사
        for directory in [cls.UPLOAD_DIR, cls.TEMP_DIR, cls.LOGS_DIR]:
            if not directory.exists():
                try:
                    directory.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f"디렉토리 생성 실패 {directory}: {e}")

        if errors:
            for error in errors:
                print(f"설정 오류: {error}")
            return False

        return True


# 전역 설정 인스턴스
settings = Settings()