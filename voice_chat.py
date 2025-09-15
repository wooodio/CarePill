import openai
import pyaudio
import wave
import threading
import time
import pygame
from io import BytesIO
import tempfile
import os
import json

class VoiceChatGPT:
    def __init__(self,config_path='config.json'):
        """
        OpenAI API를 사용한 음성 대화 시스템
        
        Args:
            api_key (str): OpenAI API 키
        """
        self.config = self.load_config(config_path)
        self.client = openai.OpenAI(api_key=self.config['openai_api_key'])
        self.is_recording = False
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        
        # PyAudio 초기화
        self.audio = pyaudio.PyAudio()
        
        # Pygame mixer 초기화 (TTS 재생용)
        pygame.mixer.init()
        
        # 대화 히스토리
        self.conversation_history = [
            {"role": "system", "content": "당신은 도움이 되는 AI 어시스턴트입니다. 한국어로 자연스럽게 대화하세요."}
        ]
    def load_config(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
            # 필수 키 확인
            required_keys = ['openai_api_key']  # API 키가 필수 키로 체크됨
            for key in required_keys:
                if key not in config:
                    raise ValueError(f"설정 파일에 필수 키 '{key}'가 없습니다.")
        return config
    def record_audio(self, duration=5):
        """
        마이크에서 오디오 녹음
        
        Args:
            duration (int): 녹음 시간 (초)
        
        Returns:
            str: 임시 WAV 파일 경로
        """
        print("🎤 녹음을 시작합니다...")
        
        stream = self.audio.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        frames = []
        for _ in range(0, int(self.rate / self.chunk * duration)):
            data = stream.read(self.chunk)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        
        # 임시 파일로 저장
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.audio_format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
        
        print("✅ 녹음 완료!")
        return temp_file.name
    
    def record_until_silence(self, silence_threshold=500, silence_duration=2):
        """
        음성이 끝날 때까지 녹음 (침묵 감지)
        
        Args:
            silence_threshold (int): 침묵으로 간주할 볼륨 임계값
            silence_duration (float): 침묵이 지속되어야 하는 시간 (초)
        """
        print("🎤 말씀하세요... (침묵이 감지되면 자동으로 종료됩니다)")
        
        stream = self.audio.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        frames = []
        silence_start = None
        
        while True:
            data = stream.read(self.chunk)
            frames.append(data)
            
            # 볼륨 계산
            volume = max(data)
            
            if volume < silence_threshold:
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > silence_duration:
                    print("🔇 침묵 감지됨. 녹음을 종료합니다.")
                    break
            else:
                silence_start = None
        
        stream.stop_stream()
        stream.close()
        
        # 임시 파일로 저장
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.audio_format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
        
        return temp_file.name
    
    def speech_to_text(self, audio_file_path):
        """
        Whisper API를 사용하여 음성을 텍스트로 변환
        
        Args:
            audio_file_path (str): 오디오 파일 경로
        
        Returns:
            str: 변환된 텍스트
        """
        print("🔄 음성을 텍스트로 변환 중...")
        
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ko"  # 한국어 지정
                )
            
            text = transcript.text
            print(f"👤 사용자: {text}")
            return text
            
        except Exception as e:
            print(f"❌ STT 오류: {e}")
            return None
        finally:
            # 임시 파일 삭제
            if os.path.exists(audio_file_path):
                os.unlink(audio_file_path)
    
    def chat_with_gpt(self, user_message):
        """
        ChatGPT와 대화
        
        Args:
            user_message (str): 사용자 메시지
        
        Returns:
            str: GPT 응답
        """
        print("🤖 ChatGPT가 응답을 생성 중...")
        
        try:
            # 대화 히스토리에 추가
            self.conversation_history.append({"role": "user", "content": user_message})
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # 또는 "gpt-4"
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            
            # 대화 히스토리에 추가
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            print(f"🤖 ChatGPT: {assistant_message}")
            return assistant_message
            
        except Exception as e:
            print(f"❌ ChatGPT API 오류: {e}")
            return "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."
    
    def text_to_speech(self, text):
        """
        OpenAI TTS API를 사용하여 텍스트를 음성으로 변환하고 재생
        
        Args:
            text (str): 변환할 텍스트
        """
        print("🔊 음성을 생성하고 재생 중...")
        
        try:
            response = self.client.audio.speech.create(
                model=self.config['tts_model'],  # config에서 TTS 모델 사용
                voice=self.config['tts_voice'],   # config에서 음성 설정 사용
                input=text
            )
            
            # BytesIO를 사용하여 메모리에서 오디오 재생
            audio_data = BytesIO(response.content)
            
            # 임시 파일로 저장하여 재생
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            # Pygame으로 재생
            pygame.mixer.music.load(temp_file_path)
            pygame.mixer.music.play()
            
            # 재생이 끝날 때까지 대기
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # 임시 파일 삭제
            os.unlink(temp_file_path)
            
        except Exception as e:
            print(f"❌ TTS 오류: {e}")
    
    def start_conversation(self):
        """
        음성 대화 시작
        """
        print("🎉 ChatGPT 음성 대화를 시작합니다!")
        print("💡 팁: 'exit', '종료', '끝' 이라고 말하면 대화가 종료됩니다.")
        
        try:
            while True:
                print("\n" + "="*50)
                
                # 1. 음성 녹음
                audio_file = self.record_until_silence()
                
                # 2. STT (음성 → 텍스트)
                user_text = self.speech_to_text(audio_file)
                
                if not user_text:
                    print("❌ 음성을 인식하지 못했습니다. 다시 시도해주세요.")
                    continue
                
                # 종료 키워드 확인
                if any(keyword in user_text.lower() for keyword in ['exit', '종료', '끝']):
                    print("👋 대화를 종료합니다.")
                    break
                
                # 3. ChatGPT와 대화
                gpt_response = self.chat_with_gpt(user_text)
                
                # 4. TTS (텍스트 → 음성)
                self.text_to_speech(gpt_response)
                
        except KeyboardInterrupt:
            print("\n👋 대화가 중단되었습니다.")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """
        리소스 정리
        """
        self.audio.terminate()
        pygame.mixer.quit()


# 사용 예시
if __name__ == "__main__":
    try:
        # 음성 대화 시스템 초기화 (config.json에서 API 키 자동 로드)
        voice_chat = VoiceChatGPT()
        
        # 대화 시작
        voice_chat.start_conversation()
        
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
        print("🔧 config.json 파일을 확인해주세요.")