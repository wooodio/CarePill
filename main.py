"""
CarePill 메인 애플리케이션
약품 관리 시스템의 진입점
"""

import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from utils import get_logger, log_system_event, log_error
from database import init_database, get_db_manager
from voice_chat import VoiceChatGPT


class CarePillApplication:
    """CarePill 메인 애플리케이션 클래스"""

    def __init__(self):
        self.logger = get_logger('carepill.main')
        self.db_manager = None
        self.voice_chat = None
        self.is_running = False

    async def initialize(self):
        """애플리케이션 초기화"""
        try:
            log_system_event('info', 'main', "CarePill 시스템 초기화 시작")

            # 설정 유효성 검사
            if not settings.validate_settings():
                raise RuntimeError("설정 유효성 검사 실패")

            # 데이터베이스 초기화
            self.db_manager = init_database(settings.get_database_url())
            log_system_event('info', 'main', "데이터베이스 초기화 완료")

            # 데이터베이스 연결 테스트
            if not self.db_manager.test_connection():
                raise RuntimeError("데이터베이스 연결 실패")

            # 음성 채팅 시스템 초기화
            try:
                self.voice_chat = VoiceChatGPT()
                log_system_event('info', 'main', "음성 채팅 시스템 초기화 완료")
            except Exception as e:
                log_error("음성 채팅 시스템 초기화 실패", e, 'main')
                self.voice_chat = None

            # 기본 설정 데이터 삽입
            await self._setup_default_configurations()

            log_system_event('info', 'main', "CarePill 시스템 초기화 완료")

        except Exception as e:
            log_error("시스템 초기화 실패", e, 'main')
            raise

    async def _setup_default_configurations(self):
        """기본 설정 데이터 삽입"""
        try:
            from database.models import Configuration

            with self.db_manager.session_scope() as session:
                # 기본 설정이 없을 경우에만 삽입
                existing_config = session.query(Configuration).first()
                if existing_config:
                    return

                default_configs = [
                    {
                        'key': 'system_version',
                        'value': '1.0.0',
                        'category': 'system',
                        'description': '시스템 버전'
                    },
                    {
                        'key': 'ocr_enabled',
                        'value': 'true',
                        'data_type': 'boolean',
                        'category': 'features',
                        'description': 'OCR 기능 활성화'
                    },
                    {
                        'key': 'yolo_enabled',
                        'value': 'true',
                        'data_type': 'boolean',
                        'category': 'features',
                        'description': 'YOLO 객체 인식 기능 활성화'
                    },
                    {
                        'key': 'voice_enabled',
                        'value': 'true',
                        'data_type': 'boolean',
                        'category': 'features',
                        'description': '음성 인터페이스 활성화'
                    },
                    {
                        'key': 'dur_check_enabled',
                        'value': 'true',
                        'data_type': 'boolean',
                        'category': 'features',
                        'description': 'DUR 점검 기능 활성화'
                    },
                    {
                        'key': 'auto_backup_interval',
                        'value': '24',
                        'data_type': 'integer',
                        'category': 'backup',
                        'description': '자동 백업 간격(시간)'
                    },
                    {
                        'key': 'inventory_low_threshold',
                        'value': '10',
                        'data_type': 'integer',
                        'category': 'inventory',
                        'description': '재고 부족 알림 기준'
                    },
                    {
                        'key': 'expiry_warning_days',
                        'value': '30',
                        'data_type': 'integer',
                        'category': 'inventory',
                        'description': '유효기간 만료 경고 일수'
                    }
                ]

                for config_data in default_configs:
                    config = Configuration(**config_data)
                    session.add(config)

                session.commit()
                log_system_event('info', 'main', "기본 설정 데이터 삽입 완료")

        except Exception as e:
            log_error("기본 설정 데이터 삽입 실패", e, 'main')

    async def start_voice_interface(self):
        """음성 인터페이스 시작"""
        if not self.voice_chat:
            log_error("음성 채팅 시스템이 초기화되지 않았습니다", module='main')
            return

        try:
            log_system_event('info', 'main', "음성 인터페이스 시작")
            self.voice_chat.start_conversation()
        except Exception as e:
            log_error("음성 인터페이스 실행 실패", e, 'main')

    async def run_interactive_mode(self):
        """대화형 모드 실행"""
        print("\n" + "="*50)
        print("🏥 CarePill 약품 관리 시스템")
        print("="*50)
        print("\n사용 가능한 명령어:")
        print("1. voice    - 음성 인터페이스 시작")
        print("2. status   - 시스템 상태 확인")
        print("3. db       - 데이터베이스 상태 확인")
        print("4. exit     - 시스템 종료")
        print("-"*50)

        self.is_running = True

        while self.is_running:
            try:
                command = input("\nCarePill> ").strip().lower()

                if command == 'voice':
                    await self.start_voice_interface()

                elif command == 'status':
                    await self._show_system_status()

                elif command == 'db':
                    await self._show_database_status()

                elif command in ['exit', 'quit', '종료']:
                    await self.shutdown()
                    break

                elif command == 'help':
                    print("\n사용 가능한 명령어:")
                    print("- voice: 음성 인터페이스 시작")
                    print("- status: 시스템 상태 확인")
                    print("- db: 데이터베이스 상태 확인")
                    print("- exit: 시스템 종료")

                elif command == '':
                    continue

                else:
                    print(f"알 수 없는 명령어: {command}")
                    print("'help'를 입력하여 사용 가능한 명령어를 확인하세요.")

            except KeyboardInterrupt:
                print("\n\n시스템을 종료합니다...")
                await self.shutdown()
                break
            except Exception as e:
                log_error("대화형 모드 오류", e, 'main')
                print(f"오류가 발생했습니다: {e}")

    async def _show_system_status(self):
        """시스템 상태 표시"""
        print("\n📊 시스템 상태:")
        print(f"  - 데이터베이스: {'✅ 연결됨' if self.db_manager and self.db_manager.test_connection() else '❌ 연결 실패'}")
        print(f"  - 음성 인터페이스: {'✅ 활성화' if self.voice_chat else '❌ 비활성화'}")
        print(f"  - 디버그 모드: {'✅ 활성화' if settings.DEBUG else '❌ 비활성화'}")
        print(f"  - 로그 레벨: {settings.LOG_LEVEL}")

    async def _show_database_status(self):
        """데이터베이스 상태 표시"""
        if not self.db_manager:
            print("❌ 데이터베이스가 초기화되지 않았습니다.")
            return

        try:
            from database.models import Medication, Patient, Prescription

            with self.db_manager.session_scope() as session:
                medication_count = session.query(Medication).count()
                patient_count = session.query(Patient).count()
                prescription_count = session.query(Prescription).count()

                print("\n🗄️ 데이터베이스 상태:")
                print(f"  - 등록된 약품: {medication_count}개")
                print(f"  - 등록된 환자: {patient_count}명")
                print(f"  - 처방전: {prescription_count}건")
                print(f"  - 데이터베이스 타입: {settings.DB_TYPE}")

        except Exception as e:
            log_error("데이터베이스 상태 확인 실패", e, 'main')
            print(f"❌ 데이터베이스 상태 확인 실패: {e}")

    async def shutdown(self):
        """애플리케이션 종료"""
        log_system_event('info', 'main', "CarePill 시스템 종료 시작")

        try:
            self.is_running = False

            # 데이터베이스 연결 종료
            if self.db_manager:
                self.db_manager.close()

            log_system_event('info', 'main', "CarePill 시스템 종료 완료")

        except Exception as e:
            log_error("시스템 종료 중 오류", e, 'main')


async def main():
    """메인 함수"""
    app = CarePillApplication()

    try:
        # 애플리케이션 초기화
        await app.initialize()

        # 대화형 모드 실행
        await app.run_interactive_mode()

    except KeyboardInterrupt:
        print("\n시스템을 종료합니다...")
    except Exception as e:
        log_error("애플리케이션 실행 실패", e, 'main')
        print(f"오류가 발생했습니다: {e}")
    finally:
        await app.shutdown()


if __name__ == "__main__":
    # Python 3.7 이상에서 asyncio.run() 사용
    if sys.version_info >= (3, 7):
        asyncio.run(main())
    else:
        # 이전 버전 호환성
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(main())
        finally:
            loop.close()