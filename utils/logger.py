"""
CarePill 로깅 유틸리티
시스템 전체에서 사용할 로거 설정 및 관리
"""

import logging
import logging.config
from pathlib import Path
from typing import Optional
from config import settings


class CarePillLogger:
    """CarePill 전용 로거 클래스"""

    _instance: Optional['CarePillLogger'] = None
    _initialized: bool = False

    def __new__(cls) -> 'CarePillLogger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            self._initialized = True

    def _setup_logging(self):
        """로깅 설정 초기화"""
        # 로그 디렉토리 생성
        log_dir = Path(settings.LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # 로깅 설정 적용
        logging_config = settings.get_logging_config()
        logging.config.dictConfig(logging_config)

        # 기본 로거 설정
        self.logger = logging.getLogger('carepill')
        self.logger.info("CarePill 로깅 시스템 초기화 완료")

    def get_logger(self, name: str = 'carepill') -> logging.Logger:
        """지정된 이름의 로거 반환"""
        return logging.getLogger(name)

    def log_system_event(self, level: str, module: str, message: str, **kwargs):
        """시스템 이벤트 로깅"""
        extra = {
            'module': module,
            **kwargs
        }

        logger = self.get_logger('carepill.system')
        getattr(logger, level.lower())(message, extra=extra)

    def log_ocr_event(self, message: str, image_path: str = None, confidence: float = None, **kwargs):
        """OCR 이벤트 로깅"""
        extra = {
            'module': 'ocr',
            'image_path': image_path,
            'confidence': confidence,
            **kwargs
        }

        logger = self.get_logger('carepill.ocr')
        logger.info(message, extra=extra)

    def log_yolo_event(self, message: str, image_path: str = None, detections: int = None, **kwargs):
        """YOLO 이벤트 로깅"""
        extra = {
            'module': 'yolo',
            'image_path': image_path,
            'detections': detections,
            **kwargs
        }

        logger = self.get_logger('carepill.yolo')
        logger.info(message, extra=extra)

    def log_database_event(self, message: str, operation: str = None, table: str = None, **kwargs):
        """데이터베이스 이벤트 로깅"""
        extra = {
            'module': 'database',
            'operation': operation,
            'table': table,
            **kwargs
        }

        logger = self.get_logger('carepill.database')
        logger.info(message, extra=extra)

    def log_api_event(self, message: str, endpoint: str = None, method: str = None, status_code: int = None, **kwargs):
        """API 이벤트 로깅"""
        extra = {
            'module': 'api',
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            **kwargs
        }

        logger = self.get_logger('carepill.api')
        logger.info(message, extra=extra)

    def log_hardware_event(self, message: str, device: str = None, **kwargs):
        """하드웨어 이벤트 로깅"""
        extra = {
            'module': 'hardware',
            'device': device,
            **kwargs
        }

        logger = self.get_logger('carepill.hardware')
        logger.info(message, extra=extra)

    def log_dur_event(self, message: str, interaction_type: str = None, severity: str = None, **kwargs):
        """DUR 이벤트 로깅"""
        extra = {
            'module': 'dur',
            'interaction_type': interaction_type,
            'severity': severity,
            **kwargs
        }

        logger = self.get_logger('carepill.dur')
        logger.info(message, extra=extra)

    def log_voice_event(self, message: str, operation: str = None, duration: float = None, **kwargs):
        """음성 처리 이벤트 로깅"""
        extra = {
            'module': 'voice',
            'operation': operation,
            'duration': duration,
            **kwargs
        }

        logger = self.get_logger('carepill.voice')
        logger.info(message, extra=extra)

    def log_error(self, message: str, error: Exception = None, module: str = None, **kwargs):
        """에러 로깅"""
        extra = {
            'module': module or 'unknown',
            'error_type': type(error).__name__ if error else None,
            'error_details': str(error) if error else None,
            **kwargs
        }

        logger = self.get_logger('carepill.error')
        logger.error(message, extra=extra, exc_info=error)

    def log_performance(self, operation: str, duration: float, module: str = None, **kwargs):
        """성능 로깅"""
        extra = {
            'module': module or 'performance',
            'operation': operation,
            'duration': duration,
            **kwargs
        }

        logger = self.get_logger('carepill.performance')
        logger.info(f"Performance: {operation} took {duration:.3f}s", extra=extra)


# 싱글톤 인스턴스 생성
_carepill_logger = CarePillLogger()

# 편의 함수들
def get_logger(name: str = 'carepill') -> logging.Logger:
    """로거 인스턴스 반환"""
    return _carepill_logger.get_logger(name)

def log_system_event(level: str, module: str, message: str, **kwargs):
    """시스템 이벤트 로깅 헬퍼"""
    _carepill_logger.log_system_event(level, module, message, **kwargs)

def log_error(message: str, error: Exception = None, module: str = None, **kwargs):
    """에러 로깅 헬퍼"""
    _carepill_logger.log_error(message, error, module, **kwargs)

def log_performance(operation: str, duration: float, module: str = None, **kwargs):
    """성능 로깅 헬퍼"""
    _carepill_logger.log_performance(operation, duration, module, **kwargs)

# 모듈별 편의 함수들
def log_ocr_event(message: str, **kwargs):
    """OCR 이벤트 로깅 헬퍼"""
    _carepill_logger.log_ocr_event(message, **kwargs)

def log_yolo_event(message: str, **kwargs):
    """YOLO 이벤트 로깅 헬퍼"""
    _carepill_logger.log_yolo_event(message, **kwargs)

def log_database_event(message: str, **kwargs):
    """데이터베이스 이벤트 로깅 헬퍼"""
    _carepill_logger.log_database_event(message, **kwargs)

def log_api_event(message: str, **kwargs):
    """API 이벤트 로깅 헬퍼"""
    _carepill_logger.log_api_event(message, **kwargs)

def log_hardware_event(message: str, **kwargs):
    """하드웨어 이벤트 로깅 헬퍼"""
    _carepill_logger.log_hardware_event(message, **kwargs)

def log_dur_event(message: str, **kwargs):
    """DUR 이벤트 로깅 헬퍼"""
    _carepill_logger.log_dur_event(message, **kwargs)

def log_voice_event(message: str, **kwargs):
    """음성 처리 이벤트 로깅 헬퍼"""
    _carepill_logger.log_voice_event(message, **kwargs)