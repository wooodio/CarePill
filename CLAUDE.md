# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Korean voice chat system that integrates multiple OpenAI APIs to create a conversational AI with full voice capabilities. The system uses a pipeline approach: voice input → speech-to-text → ChatGPT conversation → text-to-speech → audio output.

## Core Architecture

### Main Components
- **VoiceChatGPT class** (`voice_chat.py`): Single monolithic class handling the entire voice chat pipeline
- **Configuration system** (`config.json`): Centralized settings for all OpenAI API parameters
- **Audio pipeline**: PyAudio (recording) → OpenAI Whisper (STT) → ChatGPT (conversation) → OpenAI TTS → Pygame (playback)

### Key Methods
- `record_until_silence()`: Smart audio recording with automatic silence detection
- `speech_to_text()`: Whisper API integration with Korean language support
- `chat_with_gpt()`: ChatGPT conversation with persistent history
- `text_to_speech()`: OpenAI TTS with configurable voice settings
- `start_conversation()`: Main conversation loop orchestrating the entire pipeline

## Common Commands

```bash
# Start voice chat (requires microphone and speakers)
python voice_chat.py

# No build/test commands - this is a single-file application
# No linting configured - standard Python practices apply
```

The application will:
1. Load configuration from `config.json`
2. Initialize audio systems (PyAudio, Pygame)
3. Start the conversation loop
4. Wait for voice input and respond with synthesized speech

## Configuration

The `config.json` file controls all API and model settings:
- `openai_api_key`: Required OpenAI API key
- `model`: ChatGPT model (default: gpt-3.5-turbo)
- `tts_model`: TTS model (default: tts-1)
- `tts_voice`: Voice type (alloy, echo, fable, onyx, nova, shimmer)
- `language`: Speech recognition language (default: ko for Korean)
- `max_tokens`: ChatGPT response limit
- `temperature`: ChatGPT creativity setting

## Dependencies and Setup

This project uses a conda environment (`carepill`). Required Python packages:
- `openai`: OpenAI API client
- `pyaudio`: Audio recording from microphone
- `pygame`: Audio playback for TTS
- `wave`: WAV file handling (built-in)

Install dependencies:
```bash
pip install openai pyaudio pygame
```

Note: PyAudio may require system-level audio libraries on some platforms.

## Development Notes

### Audio System Design
- Uses temporary files for audio processing (automatically cleaned up)
- Implements smart silence detection for natural conversation flow
- Pygame mixer provides reliable cross-platform audio playback
- All audio operations are synchronous to maintain conversation flow

### Memory Management
- Temporary audio files are created and cleaned up automatically
- Conversation history accumulates in memory (no persistence)
- Audio streams are properly closed after each recording session

### Error Handling
- API failures gracefully fall back with user-friendly messages
- Audio system errors are caught and reported
- Configuration validation ensures required settings are present

### Termination
- Voice commands: "exit", "종료", "끝"
- Keyboard interrupt (Ctrl+C) is handled gracefully
- Resources are properly cleaned up on exit

## Important Security Notes

- The `config.json` file is gitignored but contains the actual API key in this repository
- When working with this code, ensure API keys are never committed to version control
- The current config.json should be treated as a template and replaced with user's own API key

## Task Master AI Instructions
**Import Task Master's development workflow commands and guidelines, treat as if import is in the main CLAUDE.md file.**
@./.taskmaster/CLAUDE.md
