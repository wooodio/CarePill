"""
CarePill 데이터베이스 연결 및 관리
SQLAlchemy를 사용한 데이터베이스 연결 관리
"""

import os
import logging
from typing import Generator, Optional
from contextlib import contextmanager
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from .models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """데이터베이스 연결 관리 클래스"""

    def __init__(self, database_url: Optional[str] = None):
        """
        데이터베이스 매니저 초기화

        Args:
            database_url: 데이터베이스 연결 URL
        """
        self.database_url = database_url or self._get_database_url()
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self._initialize_engine()

    def _get_database_url(self) -> str:
        """환경 변수에서 데이터베이스 URL 가져오기"""
        # 개발 환경에서는 SQLite 사용
        db_type = os.getenv('DB_TYPE', 'sqlite')

        if db_type == 'sqlite':
            db_path = os.getenv('SQLITE_DB_PATH', 'carepill.db')
            return f"sqlite:///{db_path}"

        elif db_type == 'mysql':
            host = os.getenv('DB_HOST', 'localhost')
            port = os.getenv('DB_PORT', '3306')
            user = os.getenv('DB_USER', 'root')
            password = os.getenv('DB_PASSWORD', '')
            database = os.getenv('DB_NAME', 'carepill')
            return f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"

        else:
            raise ValueError(f"지원하지 않는 데이터베이스 타입: {db_type}")

    def _initialize_engine(self):
        """데이터베이스 엔진 초기화"""
        try:
            if self.database_url.startswith('sqlite'):
                # SQLite 설정
                self.engine = create_engine(
                    self.database_url,
                    poolclass=StaticPool,
                    connect_args={
                        "check_same_thread": False,
                        "timeout": 20
                    },
                    echo=os.getenv('DB_ECHO', 'false').lower() == 'true'
                )
            else:
                # MySQL 설정
                self.engine = create_engine(
                    self.database_url,
                    pool_pre_ping=True,
                    pool_recycle=300,
                    echo=os.getenv('DB_ECHO', 'false').lower() == 'true'
                )

            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            logger.info(f"데이터베이스 엔진 초기화 완료: {self.database_url}")

        except Exception as e:
            logger.error(f"데이터베이스 엔진 초기화 실패: {e}")
            raise

    def create_tables(self):
        """데이터베이스 테이블 생성"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("데이터베이스 테이블 생성 완료")
        except Exception as e:
            logger.error(f"테이블 생성 실패: {e}")
            raise

    def drop_tables(self):
        """데이터베이스 테이블 삭제"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("데이터베이스 테이블 삭제 완료")
        except Exception as e:
            logger.error(f"테이블 삭제 실패: {e}")
            raise

    def get_session(self) -> Session:
        """데이터베이스 세션 반환"""
        if not self.SessionLocal:
            raise RuntimeError("데이터베이스가 초기화되지 않았습니다.")
        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """세션 컨텍스트 매니저"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def test_connection(self) -> bool:
        """데이터베이스 연결 테스트"""
        try:
            with self.session_scope() as session:
                session.execute(text("SELECT 1"))
            logger.info("데이터베이스 연결 테스트 성공")
            return True
        except Exception as e:
            logger.error(f"데이터베이스 연결 테스트 실패: {e}")
            return False

    def close(self):
        """데이터베이스 연결 종료"""
        if self.engine:
            self.engine.dispose()
            logger.info("데이터베이스 연결 종료")


# 전역 데이터베이스 매니저 인스턴스
_db_manager: Optional[DatabaseManager] = None


def init_database(database_url: Optional[str] = None) -> DatabaseManager:
    """
    데이터베이스 초기화

    Args:
        database_url: 데이터베이스 연결 URL

    Returns:
        DatabaseManager: 데이터베이스 매니저 인스턴스
    """
    global _db_manager

    if _db_manager is None:
        _db_manager = DatabaseManager(database_url)
        _db_manager.create_tables()

    return _db_manager


def get_db_manager() -> DatabaseManager:
    """데이터베이스 매니저 인스턴스 반환"""
    if _db_manager is None:
        raise RuntimeError("데이터베이스가 초기화되지 않았습니다. init_database()를 먼저 호출하세요.")
    return _db_manager


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI 의존성 주입용 세션 제너레이터"""
    db_manager = get_db_manager()
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()


def create_tables():
    """테이블 생성 헬퍼 함수"""
    db_manager = get_db_manager()
    db_manager.create_tables()


# 편의 함수들
def with_db_session(func):
    """데이터베이스 세션 데코레이터"""
    def wrapper(*args, **kwargs):
        db_manager = get_db_manager()
        with db_manager.session_scope() as session:
            return func(session, *args, **kwargs)
    return wrapper