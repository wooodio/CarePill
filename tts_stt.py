import os
import io
import time
import wave
import queue
import numpy as np
import sounddevice as sd
import soundfile as sf
import simpleaudio as sa
from pydub import AudioSegment
import requests
from openai import OpenAI


# ===== 설정 =====
SAMPLE_RATE = 16000
CHANNELS = 1
RECORD_SECONDS = 5         # Enter 누를 때마다 이 길이만큼 녹음
STT_MODEL = "gpt-4o-mini-transcribe"   # 경량/저비용 STT
CHAT_MODEL = "gpt-4o-mini"             # 빠르고 저렴한 대화 모델
TTS_MODEL = "gpt-4o-mini-tts"          # 자연스러운 TTS
TTS_VOICE = "alloy"                    # 음색 이름(문서에 예시 존재)
API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)

# ===== 유틸: 녹음 =====
def record_wav(temp_path="temp_input.wav", seconds=RECORD_SECONDS, sr=SAMPLE_RATE, ch=CHANNELS):
    print(f"\n🎙️  {seconds}초 녹음 시작... (말하세요)")
    audio = sd.rec(int(seconds * sr), samplerate=sr, channels=ch, dtype='float32')
    sd.wait()
    sf.write(temp_path, audio, sr)  # 16kHz mono WAV 저장
    print("✅ 녹음 완료.")
    return temp_path

# ===== 유틸: STT(음성→텍스트) =====
def transcribe_wav(path):
    # REST로 호출(믿음직), 공식 엔드포인트: /v1/audio/transcriptions
    # 참고: Speech-to-Text 가이드 & API 레퍼런스. :contentReference[oaicite:2]{index=2}
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    with open(path, "rb") as f:
        files = {"file": (os.path.basename(path), f, "audio/wav")}
        data = {"model": STT_MODEL, "response_format": "json"}  # 한국어 자동 인식
        resp = requests.post(url, headers=headers, files=files, data=data, timeout=120)
    resp.raise_for_status()
    text = resp.json().get("text", "").strip()
    return text

# ===== 유틸: Chat (텍스트→텍스트) =====
def chat_reply(messages):
    # Chat Completions(또는 Responses)로 대화
    # 여기선 친숙한 Chat Completions 사용
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.7
    )
    return resp.choices[0].message.content.strip()

def tts_speak(text, fmt="wav"):
    """
    - OpenAI TTS를 'wav'로 받아 바로 재생
    - fmt="wav" 권장 (mp3는 ffmpeg 필요)
    """
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini-tts",
        "voice": "alloy",
        "input": text,
        "format": fmt  # "wav" 권장
    }
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    audio_bytes = io.BytesIO(r.content)

    if fmt == "wav":
        # 메모리에서 바로 로드 & 재생
        data, sr = sf.read(audio_bytes, dtype="float32")
        sd.play(data, sr)
        sd.wait()
    else:
        # mp3 등은 ffmpeg가 필요합니다. 가급적 fmt="wav" 사용 권장
        raise RuntimeError("fmt='wav'를 사용하세요 (mp3 재생은 ffmpeg 필요).")

def main():
    print("음성 대화 데모 시작.")
    print("Enter 키를 누르면 녹음하고, 'q' 입력 시 종료합니다.")
    messages = [
        {"role": "system", "content": "당신은 한국어로 간결하고 정확하게 답변하는 음성 비서입니다."}
    ]

    while True:
        cmd = input("\n[Enter=녹음 / q=종료] > ").strip().lower()
        if cmd == "q":
            print("종료합니다.")
            break

        wav_path = record_wav()
        try:
            user_text = transcribe_wav(wav_path)
        except Exception as e:
            print(f"STT 오류: {e}")
            continue

        if not user_text:
            print("인식된 텍스트가 없습니다.")
            continue

        print(f"👤 사용자: {user_text}")
        messages.append({"role": "user", "content": user_text})

        try:
            assistant_text = chat_reply(messages)
        except Exception as e:
            print(f"Chat 오류: {e}")
            continue

        print(f"🤖 어시스턴트: {assistant_text}")
        messages.append({"role": "assistant", "content": assistant_text})

        try:
            tts_speak(assistant_text, fmt="mp3")
        except Exception as e:
            print(f"TTS 오류: {e}")

if __name__ == "__main__":
    if not API_KEY:
        raise RuntimeError("OPENAI_API_KEY 환경변수를 설정하세요.")
    main()